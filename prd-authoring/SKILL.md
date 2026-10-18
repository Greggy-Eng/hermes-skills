---
name: prd-authoring
description: "Draft, refine, and proofread product requirements docs."
version: 0.7.1
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
- "Merge my changes from <file> into the PRD" → refine mode, merge procedure (step 5)
- "Build/update the workflow diagram" for a PRD → `references/diagrams.md`
- Don't use for: engineering design docs (how, not what), meeting notes → meeting-action-items, emails about a PRD → business-email-drafting.

## Delivery (Greg)
PRDs for company work are saved into the Obsidian vault (see obsidian skill) at `Companies/<Company>/Dev Specs/<name>.md`. Keep user-given filenames verbatim (e.g. `3PL_flow.md`) — do not normalize case or separators.
- Version-control mirror: after each PRD version, copy it to GitHub `Greggy-Eng/PRD` (clone `~/Greggy-Eng/PRD`) at `<company>/<name>.md`, commit `<name> vX.Y.Z: <what changed>`, push. Vault is the working copy; the repo is history.
- Timestamp stamps: every artifact edit refreshes an `**Updated:** YYYY-MM-DD HH:MM TZ` line under the doc title (get time via `date`; never guess). PRDs stamp it with the version; companion diagrams stamp it with the PRD version they are synced to.
- File hygiene: one source file per artifact by default — an extra export (PNG/SVG) counts as clutter unless Greg asks for it; send renders in chat as preview, keep Mermaid `.md` as the vault source. Add image embeds only when he says "post to the vault".

## Standing spec (the bar)
- **Every requirement is testable.** "Fast load" fails; "p95 < 1.5s on mid-tier mobile" passes. If a sentence can't be verified by a test or an observation, it isn't a requirement.
- **Metrics are baseline → target → timeframe.** No naked numbers.
- **Non-goals are mandatory.** A PRD without them has unbounded scope; if the author left them out, infer them and mark *inferred*.
- **No weasel words**: robust, seamless, intuitive, scalable, easy, modern. Either quantify or cut.
- **One requirement per statement.** "and/or" = split into separate numbered requirements.
- **Succinct throughout.** Every aspect of the doc — problem, solution, rationale, assumptions: one idea per sentence, sections ≤5 lines, each rule defined once and cited by ID (G1, FR3) thereafter. A sentence that changes no behavior gets cut.
- **Specs say *what*, not *how*.** Implementation choices baked into requirement statements get flagged and rewritten to behavior level.
- **Requirements are numbered** (FR-x / NFR-x / NG-x) so reviews can cite them unambiguously.
- **Assumptions are declared, never smuggled.** Anything assumed goes in an Assumptions section, flagged for confirmation.

## Origin mode
0. Harvest context before asking: search vault/repo/workspace — plus any live connector named in the work statement (e.g. NetSuite MCP, netsuite-mcp) for real records. If connector tools aren't injected in this chat, say so at delivery; never draft ungrounded in silence.
1. Open with the **work statement**: 1–3 of the requester's own words — who, what, outcome. One open-ended ask, no choices; if request + harvest already make it obvious, restate for confirmation. Quote verbatim in the header — every question, requirement, and metric traces to it.
2. Interrogate once with ≤5 questions (hard `clarify` cap) **derived from the work statement's gaps**: problem evidence, target users, success metrics, constraints (time/tech/legal), non-goals, scope horizon. Skip anything the work statement already answers (offering choices gets faster, fuller answers) — do not drip-feed follow-ups.
3. Unanswered items become explicit Assumptions in the draft, not blank sections.
4. Fill `templates/prd-template.md` section by section. Never invent requirements to fill space — "not specified" beats plausible fiction.
5. Self-review before delivering: run the draft past `references/review-checklist.md`, fix your own flags, then cut wordiness.
6. Deliver the PRD + a short "open questions for stakeholders" list (this is what makes origin output feel expert).

## Refine mode
1. Critique pass first, edits second: score each section against `references/review-checklist.md`; list gaps and violations with requirement IDs.
2. Rewrite applying the standing spec. Convert vague claims using `references/metric-patterns.md`.
3. Deliver: revised doc + "what changed & why" bullet list (requirement ID → violation → fix). The reasoning is part of the deliverable — Greg learns the reviewer's bar.
4. Add missing mandatory sections (Non-goals, Success metrics, Open questions) even if inferring their contents; label inferred content.
5. Merging an author-supplied revision file (a "Mod"/annotated copy dropped beside the PRD): diff it against the current version, merge only the deltas into a new version, keep the author's requirement numbering verbatim even when nonstandard (FR6.5), and check every change against existing assumptions — one that conflicts supersedes the old assumption in place (marked, per the contradiction pitfall) and spawns a fresh Open Question if it opens policy doubt (e.g. print gate vs mandatory audit artifact). Deliver the merge as a "folded in / flagged" pair.

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
- Don't re-explain a rule at each use — bloat at the reader's expense; define once, cite the ID.
- When refining, don't preserve structure that caused the ambiguity — collapse and renumber, updating cross-references.
- When an answer promises detail it never delivers ("I'll name them"), don't stall or fire a second interrogation round — write the doc with explicit TBDs routed to Open Questions and ask for the missing names in the delivery reply.
- When later stakeholder answers contradict an assumption in the draft, replace the assumption in place and mark it revised with what it supersedes — two contradictory assumptions must never coexist in the doc, and the change belongs in the delivery report as a flagged item.

## Verification
- Origin: work statement quoted verbatim in the header; every template section present, non-empty, and succinct; every FR/NFR traceable and testable; assumptions exist where questions went unanswered.
- Refine: every 🔴/🟡 found in the critique pass is either fixed in the rewrite or listed in open questions.
- Proof: every numbered requirement has a verdict; severity table complete; ship/no-ship line present.
