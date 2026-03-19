#!/usr/bin/env python3
"""Step 2 (real data): GH Archive ingestion + AI-adoption proxy integration.

This script builds a repo-week panel that is schema-compatible with the synthetic
pipeline's downstream analysis scripts (Step 3-6). The treatment variable is a
*proxy* for AI-assisted coding adoption inferred from public text mentions.

Example:
  python scripts/step2_real_pipeline.py \
    --start-date 2025-02-01 \
    --end-date 2025-02-28 \
    --repos-file scripts/config/pilot_repos.txt \
    --hour-step 24 \
    --max-lines-per-hour 120000 \
    --tag pilot \
    --output-dir outputs/real_pilot
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


AI_PROXY_KEYWORDS = [
    "copilot",
    "chatgpt",
    "gpt-4",
    "gpt4",
    "gpt",
    "claude",
    "openai",
    "anthropic",
    "gemini",
    "llama",
    "cursor",
    "codeium",
    "tabnine",
    "llm",
    "assistant",
    "prompt",
    "ai",
    "generative ai",
]

AI_REGEX = re.compile(r"\b(" + "|".join(re.escape(k) for k in AI_PROXY_KEYWORDS) + r")\b", re.IGNORECASE)
BUG_REGEX = re.compile(r"\b(bug|regression|hotfix|revert|rollback|defect)\b", re.IGNORECASE)


@dataclass
class RealConfig:
    start_date: date
    end_date: date
    repos: list[str]
    hour_step: int = 24
    hour_offset: int = 0
    max_hours: int | None = None
    max_lines_per_hour: int | None = 120000
    junior_prior_contrib_threshold: int = 25
    ai_intensity_threshold: float = 0.02
    ai_min_signal_events: int = 2
    min_total_output_for_sample: int = 3
    request_timeout_sec: int = 120
    user_agent: str = "Mozilla/5.0 (compatible; OpenClaw-ResearchBot/1.0)"


def parse_iso_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def week_start_from_ts(ts: datetime) -> date:
    d = ts.date()
    return d - timedelta(days=d.weekday())


def monday_floor(d: date) -> date:
    return d - timedelta(days=d.weekday())


def enumerate_weeks(start: date, end: date) -> list[date]:
    first = monday_floor(start)
    last = monday_floor(end)
    weeks = []
    current = first
    while current <= last:
        weeks.append(current)
        current += timedelta(days=7)
    return weeks


def iter_hour_stamps(start: date, end: date, step: int, offset: int = 0, max_hours: int | None = None) -> list[datetime]:
    if step <= 0:
        raise ValueError("hour_step must be >= 1")
    if offset < 0 or offset >= step:
        raise ValueError("hour_offset must satisfy 0 <= hour_offset < hour_step")

    start_dt = datetime.combine(start, time.min, tzinfo=UTC)
    end_dt = datetime.combine(end, time(hour=23), tzinfo=UTC)

    out: list[datetime] = []
    idx = 0
    current = start_dt
    while current <= end_dt:
        if idx % step == offset:
            out.append(current)
            if max_hours is not None and len(out) >= max_hours:
                break
        idx += 1
        current += timedelta(hours=1)

    return out


def gharchive_url(ts: datetime) -> str:
    return f"https://data.gharchive.org/{ts.year:04d}-{ts.month:02d}-{ts.day:02d}-{ts.hour}.json.gz"


def read_repo_list(path: Path) -> list[str]:
    repos = []
    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        repos.append(clean.lower())
    if not repos:
        raise ValueError(f"No repos found in {path}")
    return sorted(set(repos))


def safe_median(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(np.median(np.array(values, dtype=float)))


def text_has_ai_proxy(*texts: str | None) -> bool:
    combined = "\n".join(t for t in texts if t)
    if not combined:
        return False
    return bool(AI_REGEX.search(combined))


def issue_has_bug_marker(issue: dict) -> bool:
    title = issue.get("title")
    body = issue.get("body")
    if text_has_bug_proxy(title, body):
        return True

    labels = issue.get("labels") or []
    for label in labels:
        if isinstance(label, dict):
            name = str(label.get("name") or "")
        else:
            name = str(label)
        if BUG_REGEX.search(name):
            return True
    return False


def text_has_bug_proxy(*texts: str | None) -> bool:
    combined = "\n".join(t for t in texts if t)
    if not combined:
        return False
    return bool(BUG_REGEX.search(combined))


def iter_hour_events(url: str, timeout_sec: int, user_agent: str, max_lines: int | None) -> Iterable[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout_sec) as response:
        with gzip.GzipFile(fileobj=response) as gz:
            for line_idx, raw in enumerate(gz, start=1):
                if max_lines is not None and line_idx > max_lines:
                    break
                try:
                    yield json.loads(raw)
                except json.JSONDecodeError:
                    continue


def write_data_dictionary(path: Path) -> None:
    rows = [
        ("team_id", "string", "Repository name as team proxy (owner/repo)"),
        ("calendar_week", "date", "Week start date (Monday, UTC)"),
        ("week_index", "int", "Sequential week index in sample"),
        ("adoption_week", "float", "Proxy AI adoption week index; NaN for never-adopters"),
        ("treated", "int", "1 if week_index >= adoption_week for adopter repos"),
        ("post_period", "int", "Alias timing indicator for treated period"),
        ("event_time", "float", "week_index - adoption_week for adopters"),
        ("total_merged_prs", "int", "Merged PR count from PullRequestEvent merged closures"),
        ("total_completed_tickets", "int", "Closed issues count from IssuesEvent action=closed"),
        ("total_output", "int", "total_merged_prs + total_completed_tickets"),
        ("junior_merged_prs", "int", "Merged PRs by authors flagged junior via prior contribution proxy"),
        ("junior_completed_tickets", "int", "Closed issues by actors flagged junior via prior contribution proxy"),
        ("junior_output", "int", "junior_merged_prs + junior_completed_tickets"),
        ("total_commits", "int", "PushEvent commit count (pusher-attributed)"),
        ("junior_commits", "int", "PushEvent commit count by junior-proxy actors"),
        ("junior_merged_pr_share", "float", "junior_merged_prs / total_merged_prs"),
        ("junior_ticket_share", "float", "junior_completed_tickets / total_completed_tickets"),
        ("junior_commit_share", "float", "junior_commits / total_commits"),
        ("junior_output_share", "float", "Primary outcome: junior_output / total_output"),
        ("merge_count", "int", "Alias for total_merged_prs"),
        ("median_cycle_time_hours", "float", "Median merged PR cycle time (merged_at - created_at)"),
        ("review_latency_hours", "float", "Median review latency proxy (review submitted - PR created)"),
        ("post_merge_bug_proxy", "float", "Bug-marker issue openings per merged PR in week"),
        ("ai_signal_events", "int", "Text-bearing events with AI-proxy keyword mention"),
        ("ai_eligible_events", "int", "Text-bearing events considered for AI signal denominator"),
        ("ai_intensity", "float", "ai_signal_events / ai_eligible_events (proxy intensity)"),
        ("analysis_sample", "int", "1 if total_output >= threshold and junior_output_share observed"),
    ]
    pd.DataFrame(rows, columns=["variable", "type", "definition"]).to_csv(path, index=False)


def build_real_panel(cfg: RealConfig) -> tuple[pd.DataFrame, dict]:
    repo_set = set(cfg.repos)

    metric_default = lambda: {
        "total_merged_prs": 0,
        "total_completed_tickets": 0,
        "total_commits": 0,
        "bug_issue_opened": 0,
        "ai_signal_events": 0,
        "ai_eligible_events": 0,
        "cycle_time_hours": [],
        "review_latency_hours": [],
        "observed_events": 0,
    }
    repo_week_metrics: dict[tuple[str, date], dict] = defaultdict(metric_default)

    author_week = defaultdict(lambda: {"merged_prs": 0, "commits": 0, "completed_tickets": 0})

    hour_stamps = iter_hour_stamps(
        start=cfg.start_date,
        end=cfg.end_date,
        step=cfg.hour_step,
        offset=cfg.hour_offset,
        max_hours=cfg.max_hours,
    )

    fetch_stats = {
        "hours_requested": len(hour_stamps),
        "hours_successful": 0,
        "hours_failed": 0,
        "events_scanned": 0,
        "events_repo_matched": 0,
        "http_errors": [],
    }

    for stamp in hour_stamps:
        url = gharchive_url(stamp)
        try:
            for event in iter_hour_events(
                url=url,
                timeout_sec=cfg.request_timeout_sec,
                user_agent=cfg.user_agent,
                max_lines=cfg.max_lines_per_hour,
            ):
                fetch_stats["events_scanned"] += 1

                repo_name = str(event.get("repo", {}).get("name") or "").lower()
                if repo_name not in repo_set:
                    continue

                created_ts = parse_iso_ts(event.get("created_at"))
                if created_ts is None:
                    continue

                fetch_stats["events_repo_matched"] += 1
                wstart = week_start_from_ts(created_ts)
                rw_key = (repo_name, wstart)
                rw = repo_week_metrics[rw_key]
                rw["observed_events"] += 1

                actor_login = str(event.get("actor", {}).get("login") or "").lower()
                payload = event.get("payload") or {}
                event_type = event.get("type")

                if event_type == "PullRequestEvent":
                    pr = payload.get("pull_request") or {}
                    action = payload.get("action")
                    ai_hit = text_has_ai_proxy(pr.get("title"), pr.get("body"))
                    rw["ai_eligible_events"] += 1
                    if ai_hit:
                        rw["ai_signal_events"] += 1

                    if action == "closed" and bool(pr.get("merged")):
                        rw["total_merged_prs"] += 1
                        author_login = str((pr.get("user") or {}).get("login") or "").lower()
                        if author_login:
                            author_week[(repo_name, wstart, author_login)]["merged_prs"] += 1

                        pr_created = parse_iso_ts(pr.get("created_at"))
                        pr_merged = parse_iso_ts(pr.get("merged_at")) or created_ts
                        if pr_created and pr_merged and pr_merged >= pr_created:
                            cycle_hours = (pr_merged - pr_created).total_seconds() / 3600.0
                            if 0.0 <= cycle_hours <= 24 * 120:
                                rw["cycle_time_hours"].append(cycle_hours)

                elif event_type == "PushEvent":
                    commits = payload.get("commits") or []
                    n_commits = len(commits)
                    if n_commits > 0:
                        rw["total_commits"] += n_commits
                        if actor_login:
                            author_week[(repo_name, wstart, actor_login)]["commits"] += n_commits
                        messages = [str(c.get("message") or "") for c in commits if isinstance(c, dict)]
                        rw["ai_eligible_events"] += 1
                        if text_has_ai_proxy("\n".join(messages)):
                            rw["ai_signal_events"] += 1

                elif event_type == "IssuesEvent":
                    issue = payload.get("issue") or {}
                    action = payload.get("action")

                    rw["ai_eligible_events"] += 1
                    if text_has_ai_proxy(issue.get("title"), issue.get("body")):
                        rw["ai_signal_events"] += 1

                    if action == "closed":
                        rw["total_completed_tickets"] += 1
                        if actor_login:
                            author_week[(repo_name, wstart, actor_login)]["completed_tickets"] += 1

                    if action == "opened" and issue_has_bug_marker(issue):
                        rw["bug_issue_opened"] += 1

                elif event_type == "PullRequestReviewEvent":
                    pr = payload.get("pull_request") or {}
                    review = payload.get("review") or {}
                    rw["ai_eligible_events"] += 1
                    if text_has_ai_proxy(review.get("body"), pr.get("title"), pr.get("body")):
                        rw["ai_signal_events"] += 1

                    pr_created = parse_iso_ts(pr.get("created_at"))
                    review_ts = parse_iso_ts(review.get("submitted_at")) or created_ts
                    if pr_created and review_ts and review_ts >= pr_created:
                        latency_hours = (review_ts - pr_created).total_seconds() / 3600.0
                        if 0.0 <= latency_hours <= 24 * 120:
                            rw["review_latency_hours"].append(latency_hours)

                elif event_type in {"IssueCommentEvent", "PullRequestReviewCommentEvent"}:
                    comment = payload.get("comment") or {}
                    rw["ai_eligible_events"] += 1
                    if text_has_ai_proxy(comment.get("body")):
                        rw["ai_signal_events"] += 1

            fetch_stats["hours_successful"] += 1

        except urllib.error.HTTPError as exc:
            fetch_stats["hours_failed"] += 1
            fetch_stats["http_errors"].append({"url": url, "status": exc.code})
            continue
        except urllib.error.URLError:
            fetch_stats["hours_failed"] += 1
            fetch_stats["http_errors"].append({"url": url, "status": "urlerror"})
            continue

    # Build author-week table for junior proxy classification.
    author_rows = []
    for (repo, wstart, author), vals in author_week.items():
        coding_contrib = int(vals["merged_prs"] + vals["commits"])
        author_rows.append(
            {
                "team_id": repo,
                "calendar_week": wstart,
                "author": author,
                "merged_prs": int(vals["merged_prs"]),
                "commits": int(vals["commits"]),
                "completed_tickets": int(vals["completed_tickets"]),
                "coding_contrib": coding_contrib,
            }
        )

    author_df = pd.DataFrame(author_rows)
    if author_df.empty:
        author_df = pd.DataFrame(
            columns=[
                "team_id",
                "calendar_week",
                "author",
                "merged_prs",
                "commits",
                "completed_tickets",
                "coding_contrib",
                "prior_coding_contrib",
                "is_junior_proxy",
            ]
        )
    else:
        author_df = author_df.sort_values(["team_id", "author", "calendar_week"]).reset_index(drop=True)
        author_df["prior_coding_contrib"] = (
            author_df.groupby(["team_id", "author"], as_index=False)["coding_contrib"]
            .cumsum()
            - author_df["coding_contrib"]
        )
        author_df["is_junior_proxy"] = (
            author_df["prior_coding_contrib"] <= cfg.junior_prior_contrib_threshold
        ).astype(int)

    junior_week = (
        author_df.loc[author_df.get("is_junior_proxy", pd.Series(dtype=int)) == 1]
        .groupby(["team_id", "calendar_week"], as_index=False)[["merged_prs", "commits", "completed_tickets"]]
        .sum()
        .rename(
            columns={
                "merged_prs": "junior_merged_prs",
                "commits": "junior_commits",
                "completed_tickets": "junior_completed_tickets",
            }
        )
    )

    # Build balanced repo-week panel.
    weeks = enumerate_weeks(cfg.start_date, cfg.end_date)
    idx = pd.MultiIndex.from_product([cfg.repos, weeks], names=["team_id", "calendar_week"])
    panel = idx.to_frame(index=False)
    panel["week_index"] = panel["calendar_week"].rank(method="dense").astype(int)

    metric_rows = []
    for (repo, wstart), vals in repo_week_metrics.items():
        metric_rows.append(
            {
                "team_id": repo,
                "calendar_week": wstart,
                "total_merged_prs": int(vals["total_merged_prs"]),
                "total_completed_tickets": int(vals["total_completed_tickets"]),
                "total_commits": int(vals["total_commits"]),
                "merge_count": int(vals["total_merged_prs"]),
                "median_cycle_time_hours": safe_median(vals["cycle_time_hours"]),
                "review_latency_hours": safe_median(vals["review_latency_hours"]),
                "post_merge_bug_proxy": (
                    float(vals["bug_issue_opened"]) / max(float(vals["total_merged_prs"]), 1.0)
                ),
                "ai_signal_events": int(vals["ai_signal_events"]),
                "ai_eligible_events": int(vals["ai_eligible_events"]),
                "observed_events": int(vals["observed_events"]),
            }
        )

    metric_df = pd.DataFrame(metric_rows)
    if metric_df.empty:
        metric_df = pd.DataFrame(
            columns=[
                "team_id",
                "calendar_week",
                "total_merged_prs",
                "total_completed_tickets",
                "total_commits",
                "merge_count",
                "median_cycle_time_hours",
                "review_latency_hours",
                "post_merge_bug_proxy",
                "ai_signal_events",
                "ai_eligible_events",
                "observed_events",
            ]
        )

    panel = panel.merge(metric_df, on=["team_id", "calendar_week"], how="left")
    panel = panel.merge(junior_week, on=["team_id", "calendar_week"], how="left")

    fill_zero_cols = [
        "total_merged_prs",
        "total_completed_tickets",
        "total_commits",
        "merge_count",
        "ai_signal_events",
        "ai_eligible_events",
        "observed_events",
        "junior_merged_prs",
        "junior_commits",
        "junior_completed_tickets",
    ]
    for col in fill_zero_cols:
        panel[col] = panel[col].fillna(0).astype(int)

    panel["total_output"] = panel["total_merged_prs"] + panel["total_completed_tickets"]
    panel["junior_output"] = panel["junior_merged_prs"] + panel["junior_completed_tickets"]

    panel["junior_merged_pr_share"] = np.where(
        panel["total_merged_prs"] > 0,
        panel["junior_merged_prs"] / panel["total_merged_prs"],
        np.nan,
    )
    panel["junior_ticket_share"] = np.where(
        panel["total_completed_tickets"] > 0,
        panel["junior_completed_tickets"] / panel["total_completed_tickets"],
        np.nan,
    )
    panel["junior_commit_share"] = np.where(
        panel["total_commits"] > 0,
        panel["junior_commits"] / panel["total_commits"],
        np.nan,
    )
    panel["junior_output_share"] = np.where(
        panel["total_output"] > 0,
        panel["junior_output"] / panel["total_output"],
        np.nan,
    )

    panel["ai_intensity"] = np.where(
        panel["ai_eligible_events"] > 0,
        panel["ai_signal_events"] / panel["ai_eligible_events"],
        0.0,
    )

    adoption_df = (
        panel.assign(
            ai_proxy_trigger=lambda x: (
                (x["ai_intensity"] >= cfg.ai_intensity_threshold)
                & (x["ai_signal_events"] >= cfg.ai_min_signal_events)
            ).astype(int)
        )
        .sort_values(["team_id", "week_index"])
        .groupby("team_id", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "adoption_week": (
                        float(g.loc[g["ai_proxy_trigger"] == 1, "week_index"].min())
                        if (g["ai_proxy_trigger"] == 1).any()
                        else np.nan
                    )
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    panel = panel.merge(adoption_df, on="team_id", how="left")

    # One-week burn-in: if the first observed sample week already has AI-proxy signals,
    # set adoption to week 2 to preserve within-unit pre-period variation.
    max_week_index = int(panel["week_index"].max()) if not panel.empty else 0
    if max_week_index >= 2:
        panel.loc[panel["adoption_week"] == 1, "adoption_week"] = 2

    panel["treated"] = (
        panel["adoption_week"].notna() & (panel["week_index"] >= panel["adoption_week"])
    ).astype(int)
    panel["post_period"] = panel["treated"]
    panel["event_time"] = np.where(
        panel["adoption_week"].notna(),
        panel["week_index"] - panel["adoption_week"],
        np.nan,
    )
    panel["analysis_sample"] = (
        (panel["total_output"] >= cfg.min_total_output_for_sample)
        & panel["junior_output_share"].notna()
    ).astype(int)

    panel = panel.sort_values(["team_id", "week_index"]).reset_index(drop=True)
    panel["calendar_week"] = pd.to_datetime(panel["calendar_week"]).dt.date

    metadata = {
        "data_type": "real_public_proxy",
        "source": "GH Archive",
        "ai_adoption_note": "AI adoption is proxy-based from public text keyword mentions; not direct seat/license telemetry.",
        "config": {
            "start_date": cfg.start_date.isoformat(),
            "end_date": cfg.end_date.isoformat(),
            "n_repos": len(cfg.repos),
            "hour_step": cfg.hour_step,
            "hour_offset": cfg.hour_offset,
            "max_hours": cfg.max_hours,
            "max_lines_per_hour": cfg.max_lines_per_hour,
            "junior_prior_contrib_threshold": cfg.junior_prior_contrib_threshold,
            "ai_intensity_threshold": cfg.ai_intensity_threshold,
            "ai_min_signal_events": cfg.ai_min_signal_events,
            "min_total_output_for_sample": cfg.min_total_output_for_sample,
            "ai_proxy_keywords": AI_PROXY_KEYWORDS,
            "adoption_week1_burn_in_to_week2": True,
        },
        "fetch_stats": fetch_stats,
        "summary": {
            "n_rows": int(len(panel)),
            "n_teams": int(panel["team_id"].nunique()),
            "n_weeks": int(panel["week_index"].nunique()),
            "analysis_sample_rows": int(panel["analysis_sample"].sum()),
            "adoption_rate_team_level": float(panel.groupby("team_id")["adoption_week"].first().notna().mean()),
            "treated_share": float(panel["treated"].mean()),
            "mean_junior_output_share": float(panel["junior_output_share"].mean(skipna=True)),
            "mean_ai_intensity": float(panel["ai_intensity"].mean()),
        },
    }

    return panel, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Build real repo-week panel from GH Archive + AI proxy")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--repos-file", required=True, help="Text file with owner/repo per line")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--tag", default="real", help="Suffix tag used in output filenames")
    parser.add_argument("--hour-step", type=int, default=24, help="Use every Nth hour from GH Archive")
    parser.add_argument("--hour-offset", type=int, default=0, help="Hour selection offset within step")
    parser.add_argument("--max-hours", type=int, default=None, help="Optional cap on number of GH Archive hours")
    parser.add_argument(
        "--max-lines-per-hour",
        type=int,
        default=120000,
        help="Read at most this many JSONL records per selected hour (sampling control)",
    )
    parser.add_argument("--junior-threshold", type=int, default=25, help="Junior proxy cutoff on prior coding contributions")
    parser.add_argument("--ai-intensity-threshold", type=float, default=0.02, help="Weekly AI-proxy intensity threshold")
    parser.add_argument("--ai-min-signal-events", type=int, default=2, help="Minimum AI-proxy events to trigger adoption")
    parser.add_argument("--min-total-output", type=int, default=3, help="analysis_sample threshold on total_output")
    parser.add_argument("--request-timeout-sec", type=int, default=120)
    args = parser.parse_args()

    start = date.fromisoformat(args.start_date)
    end = date.fromisoformat(args.end_date)
    if end < start:
        raise ValueError("end-date must be >= start-date")

    repos = read_repo_list(Path(args.repos_file))

    cfg = RealConfig(
        start_date=start,
        end_date=end,
        repos=repos,
        hour_step=args.hour_step,
        hour_offset=args.hour_offset,
        max_hours=args.max_hours,
        max_lines_per_hour=args.max_lines_per_hour,
        junior_prior_contrib_threshold=args.junior_threshold,
        ai_intensity_threshold=args.ai_intensity_threshold,
        ai_min_signal_events=args.ai_min_signal_events,
        min_total_output_for_sample=args.min_total_output,
        request_timeout_sec=args.request_timeout_sec,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    panel, metadata = build_real_panel(cfg)

    panel_path = output_dir / f"step2_real_repo_week_panel_{args.tag}.csv"
    dict_path = output_dir / f"step2_real_data_dictionary_{args.tag}.csv"
    meta_path = output_dir / f"step2_real_metadata_{args.tag}.json"

    panel.to_csv(panel_path, index=False)
    write_data_dictionary(dict_path)
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Wrote panel: {panel_path}")
    print(f"Wrote dictionary: {dict_path}")
    print(f"Wrote metadata: {meta_path}")


if __name__ == "__main__":
    main()
