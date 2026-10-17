# Vague → Measurable Conversion Patterns

Pattern: **<subject> <verb> <metric> <target> under <conditions> within <timeframe>**.

| Vague | Bad rewrite (still fails) | Measurable |
|---|---|---|
| "Fast" | "Loads quickly" | "p95 page load < 1.5s on mid-tier mobile (Moto G class), 4G" |
| "Easy to use" | "Intuitive UI" | "New user completes core task unassisted in < 3 min; ≥ 80% in usability test" |
| "Reliable" | "High uptime" | "99.9% monthly availability, measured by external synthetic checks" |
| "Scalable" | "Handles growth" | "Sustains 10k concurrent users at p95 < 500ms without arch change" |
| "Secure" | "Bank-grade security" | "SOC 2 Type II; OWASP ASVS L2; no criticals open > 7 days" |
| "Real-time" | "Live updates" | "State change visible to other clients < 2s end-to-end" |
| "Accurate" | "Smart matching" | "Match precision ≥ 90%, recall ≥ 85% on labeled eval set v1" |
| "Wide integration" | "Connects to tools" | "Native integrations with X, Y, Z; generic REST webhook for others" |

## Rules of thumb
- No number? Ask what a skeptic would measure. That's the metric.
- Missing baseline → "measure baseline in first 2 weeks" is itself an acceptable first target.
- Percentages need denominators; latency needs percentiles (p50/p95/p99) and device/network conditions.
- Behavioral claims (adoption, retention) need a cohort and a window: "≥ 40% of activated users, within 30 days".
- When converting during refine, preserve intent — if the original author's intent is unknowable, keep the vagueness out and log it as an open question instead of guessing a number.
