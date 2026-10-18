# PRD Companion Diagrams

Mermaid diagrams as PRD companions, stored beside the PRD in the vault folder as a single `.md` (renders natively in Obsidian).

## Two views
- **Business flow** (`<name>_diagram.md`): flowchart TD — triggers → decision gates → workflow subgraphs → digest/log terminal. Cite FR/NFR/TBD IDs inside nodes so review meetings can point at the picture.
- **Technical sequence** (`<name>_diagram_tech.md`): sequenceDiagram per workflow — one participant per component (trigger job, gate script, external API, record store, log record), `rect` around transactional units, `alt` for refusal paths. Plus a data-model table (field → record → purpose → provisioning phase) and an explicit "open build-blockers" list mapping each TBD to the sequence step it blocks.

## Style conventions (technical UX Greg accepted)
classDef color code: gates yellow, process blue, success/no-op green, refused red, datastore gray cylinder `[(...)]`, **TBD blockers purple dashed** (`stroke-dasharray:5 4`). Include a legend subgraph (`direction LR`, `~~~` links between legend chips). Real record/field names on gates (`custrecord_cf_*`). Purple nodes = "not specced yet" — the diagram must make unknowns visible, never hide them in a confident-looking node.

## Validation loop (before saving to vault — never ship unvalidated)
1. Write the mermaid block to a scratch file first.
2. `curl -s -X POST https://kroki.io/mermaid/svg -H 'Content-Type: text/plain' --data-binary @file.mmd -o out.svg -w 'http:%{http_code}'` → 200 + SVG bytes = valid; 400 body carries `Parse error on line N`.
3. Kroki throws intermittent HTTP 500 on valid input — retry once after a few seconds before suspecting the diagram.
4. Always prepend the white-background init header: `%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","primaryColor":"#ffffff","primaryBorderColor":"#888888","lineColor":"#555555","secondaryColor":"#f5f5f5","tertiaryColor":"#ffffff","background":"#ffffff"}}}%%` — Obsidian dark themes render default mermaid as black-on-black.
5. Kroki PNGs come back transparent (alpha) even with background set — before storing a PNG, flatten onto white: Pillow `Image.alpha_composite(white_bg, im).convert("RGB")`. (JXA NSBitmapImageRep fails on the NULL planes arg — use Pillow; pip install pillow.)
4. Only then write the `.md` to the vault; render PNG through the same endpoint for chat preview.

## Mermaid syntax traps (each cost a debug round)
- `;` inside labels/notes is a statement terminator — parse error at the next line. Use `·` or parens instead.
- Parentheses/colons inside `{...}` decision labels: quote the label (`{"FR6 gate: checkbox?"}`).
- Rebuilding file content from `read_file` transcript output: strip line-number prefixes with `^\s*\d+\|` per line — the `N|` markers are display, not file content, and leak into rendered diagrams/scripts.

## Delivery
Every diagram note carries `**Updated:** <YYYY-MM-DD HH:MM TZ> — synced to PRD vX.Y` under the title; refresh it on every diagram edit (live `date` output, never guessed).
Preview PNG in chat (scratch path, not the vault). Vault keeps the `.md` sources; PNG only when Greg explicitly asks to "post to the vault" (then embed `![[name.png]]` under the note header).
