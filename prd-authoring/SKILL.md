---
name: prd-authoring
description: "Draft, refine, and proofread product requirements docs."
version: 0.2.0
author: Greggy (Hermes Agent)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prd, product, requirements, writing, review, proofreading]
---

# PRD Authoring

Expert discipline for Product Requirements Documents in three modes: **origin** (idea → full draft), **refine** (draft → sharper draft), **proof** (final pass, report only). This skill is the writing/review spec — document mechanics (docx, pdf, obsidian) live in those skills.

## When to Use
- "Write me a PRD for…" / "spec out this feature" → origin mode
- "Review/refine/tighten this PRD" / pasted draft asking for improvement → refine mode
- "Proof/read this before I send it" / final check, changes not wanted yet → proof mode
- Don't use for: engineering design docs (how, not what), meeting notes → meeting-action-items, emails about a PRD → business-email-drafting.

## Delivery (Greg)
PRDs for company work are saved into the Obsidian vault (see obsidian skill) at `Companies/<Company>/Dev Specs/<name>.md`. Keep user-given filenames verbatim (e.g. `3PL_flow.md`) — do not normalize case or separators.

## Standing spec (the bar)
- **Every requirement is testable.** "Fast load" fails; "p95 < 1.5s on mid-tier mobile" passes. If a sentence can't be verified by a test or an observation, it isn't a requirement.
- **Metrics are baseline → target → timeframe.** No naked numbers.
- **Non-goals are mandatory.** A PRD without them has unbounded scope; if the author left them out, infer them and mark *inferred*.
- **No weasel words**: robust, seamless, intuitive, scalable, easy, modern. Either quantify or cut.
- **One requirement per statement.** "and/or" = split into separate numbered requirements.
- **Specs say *what*, not *how*.** Implementation choices baked into requirement statements get flagged and rewritten to behavior level.
- **Requirements are numbered** (FR-x / NFR-x / NG-x) so reviews can cite them unambiguously.
- **Assumptions are declared, never smuggled.** Anything assumed goes in an Assumptions section, flagged for confirmation.

## Origin mode
0. Harvest context before asking: search the vault/repo/workspace for the company and project so interrogation covers only genuine gaps.
1. Open with the **work statement**: ask for 1–3 sentences in the requester's own words — who, what, outcome — of what this needs to accomplish (one open-ended ask, no choices; skip it if the request plus harvest already make it obvious, and restate for confirmation instead). Quote it verbatim in the doc header. It is the base of the whole PRD: every later question, requirement, and metric must trace back to it.
2. Interrogate once with ≤6 questions via `clarify`, **derived from the work statement's gaps**: problem evidence, target users, success metrics, constraints (time/tech/legal), non-goals, scope horizon. Skip anything the work statement already answers (offering choices gets faster, fuller answers) — do not drip-feed follow-ups.
3. Unanswered items become explicit Assumptions in the draft, not blank sections.
4. Fill `templates/prd-template.md` section by section. Never invent requirements to fill space — "not specified" beats plausible fiction.
5. Self-review before delivering: run the whole draft past `references/review-checklist.md`, fix your own red flags.
6. Deliver the PRD + a short "open questions for stakeholders" list (this is what makes origin output feel expert).

## Refine mode
1. Critique pass first, edits second: score each section against `references/review-checklist.md`; list gaps and violations with requirement IDs.
2. Rewrite applying the standing spec. Convert vague claims using `references/metric-patterns.md`.
3. Deliver: revised doc + "what changed & why" bullet list (requirement ID → violation → fix). The reasoning is part of the deliverable — Greg learns the reviewer's bar.
4. Add missing mandatory sections (Non-goals, Success metrics, Open questions) even if inferring their contents; label inferred content.

## Proof mode
1. Report only — no silent fixes, no rewrite.
2. Walk requirement by requirement and issue a verdict per item; never "looks good overall."
3. Output a severity-graded table:
   - 🔴 unmeasurable, contradictory, or ambiguous-in-a-costly-way requirement
   - 🟡 ambiguous / weasel word / compound requirement
   - 🔵 missing mandatory section
   - ⚪ style, numbering, consistency
4. End with a single ship/no-ship line: number of reds blocks ship.

## Pitfalls
- Don't pad interrogations past one round; an expert proceeds on declared assumptions rather than stalling for perfect information.
- Don't let the solution section smuggle architecture into requirements ("use Redis for the cache" → "repeat lookups served in <Xms").
- Don't confuse user wants with user needs — requirements trace to a user job, not a feature request from a stakeholder.
- Proof mode findings without requirement IDs are useless in a review meeting; always cite FR-x.
- When refining, don't preserve structure that caused the ambiguity — collapse and renumber, updating cross-references.
- When an answer promises detail it never delivers ("I'll name them"), don't stall or fire a second interrogation round — write the doc with explicit TBDs routed to Open Questions and ask for the missing names in the delivery reply.

## Verification
- Origin: work statement present in the header and quoted in the requester's own words; every template section present and non-empty; every FR/NFR traceable to the work statement or a goal and testable per the standing spec; assumptions section exists if any question went unanswered.
- Refine: every 🔴/🟡 found in the critique pass is either fixed in the rewrite or listed in open questions.
- Proof: every numbered requirement has a verdict; severity table complete; ship/no-ship line present.
