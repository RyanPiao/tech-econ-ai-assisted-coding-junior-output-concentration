# Step 1 — Problem Framing

## Topic
**AI-assisted coding adoption and junior-developer output concentration**

## Core causal question
Does team-level adoption of AI coding assistance change how output is distributed between junior and senior developers?

## Variables
- **Outcome variable:** the share of merged commits or completed tickets attributable to junior developers at the team-week level
- **Treatment variable:** adoption of AI coding assistance at the team level

## Why this matters
The labor-market debate around AI in software development often assumes that productivity gains are either broadly shared or primarily captured by already-strong senior contributors. This project asks a more operational question: when a team adopts AI coding assistance, does measured output become more concentrated in senior developers, or does the tooling lower execution barriers enough to increase the relative contribution of junior developers?

For firms, this matters for staffing, onboarding, promotion, and training design. For labor economists, it offers a clean way to study whether AI acts more like a skill amplifier or a capability equalizer inside teams.

## Framing and empirical direction
For this week’s cycle, the project will use a **Synthetic** team-week panel in line with the required A/B data rotation rule. The preferred baseline design is a compact difference-in-differences or fixed-effects panel model where teams adopt AI coding assistance at different times and output concentration is tracked before and after adoption.

A useful starting estimand is the change in junior-share output after adoption, relative to teams not yet adopting in the same period. The model can later be expanded to test heterogeneity by team composition, codebase complexity, or task type.

## Assumptions challenged
1. **AI always helps junior developers proportionally more.** It may instead increase review throughput for seniors and deepen concentration.
2. **Commit counts cleanly capture productivity.** They may reflect task slicing, review norms, or automation artifacts rather than economically meaningful output.
3. **Adoption timing is exogenous.** Teams may adopt because of pre-existing performance differences, delivery pressure, or managerial quality.
4. **Junior versus senior categories are behaviorally stable.** Role definitions may shift over time or differ across teams.

## Key risks
- **Measurement risk:** commit or ticket-share metrics may not map cleanly onto value creation.
- **Selection risk:** adopting teams may differ systematically from non-adopting teams.
- **Behavioral adaptation risk:** AI tools may change review, delegation, and task granularity in ways that distort the outcome measure.
- **Synthetic-design risk:** a diagnostic synthetic build is useful for workflow testing, but external validity is limited until the design is paired with real data.

## Recommendation
Proceed with a small synthetic panel build for this cycle. The topic is well suited to a reproducible Step 1–Step 7 workflow because it supports a transparent treatment definition, a plausible team-week outcome, and an interpretable labor-allocation question with direct product and management relevance.
