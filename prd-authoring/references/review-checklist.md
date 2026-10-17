# PRD Review Checklist

Used by refine mode (critique pass) and proof mode (report) — keep them consistent by reading everything here.

## Requirements quality
1. Testable: each FR/NFR verifiable by a test or observation. 🔴 if not.
2. Atomic: no "and/or" compounds. 🟡.
3. Unambiguous: one reading only; no "should probably", "as much as possible". 🟡.
4. No weasel words: robust, seamless, intuitive, scalable, easy, modern, fast, reliable (unquantified). 🟡.
5. What not how: implementation dictated inside a requirement. 🟡 (🔴 if it forecloses a better solution).
6. Numbered & citable: FR-x / NFR-x / NG-x scheme present and consistent. 🔵.
7. Traceable: each requirement maps to a goal (G-x) or a stated user job. Orphan requirements: 🟡.

## Completeness
8. Non-goals section present and meaningful (not empty, not "none"). 🔵.
9. Success metrics have baseline → target → timeframe → source. Naked numbers: 🟡.
10. Users/personas defined with jobs, not demographics. 🔵.
11. Constraints & dependencies stated (time, tech, legal). 🔵.
12. Assumptions declared where information was missing. 🔵.
13. Open questions list exists (a PRD with none means nobody read it). 🔵.

## Consistency
14. No contradictions between sections (goal says realtime, NFR allows 5-min lag). 🔴.
15. Numbers agree wherever repeated (dates, targets, counts). 🟡.
16. Terminology stable — one name per concept throughout. ⚪.
17. Status/owner/date header current. ⚪.

## Scope sanity
18. Every goal achievable within stated constraints. 🔴 if arithmetic doesn't work.
19. Must-haves distinguished from nice-to-haves; if everything is P1, nothing is. 🟡.
20. Solution section doesn't outgrow the problem section (solution-first smell). 🟡.

## Severity → ship gate
- Any 🔴 = no-ship until resolved or explicitly accepted by owner.
- 🟡 = fix before approval meeting; ⚪ = cosmetic.
