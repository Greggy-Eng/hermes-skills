---
name: obsidian-image-import
description: "Use for Obsidian image imports: dated folders, HEIC/SVG."
version: 1.0.7
author: Greggy (Hermes Agent)
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Obsidian, images, import, HEIC, Reference]
    related_skills: [obsidian]
---

# Obsidian Image Import

Import images from `/Users/greggy/Documents/Reference/` into the vault's `Reference/` folder with date-marked nested folders, HEIC→JPG and SVG→JPG conversion, whitespace trimming (SVG only), and an auto-generated `Master+{count}.md`.

## When to Use
Requests like: "add the images from ~/reference to notetaker", "import images to Reference in a date marked folder", "organize with Master file", "convert HEIC images to JPG" — any vault image-import/organization job.

## Prerequisites
- **Vault path**: `~/Greggy-AI` (capital 'I' — Greggy's vault; vault-path resolution per the obsidian skill)
- **Import destination**: `~/Greggy-AI/Reference/` — capital R, never lowercase
- **Source folder**: `/Users/greggy/Documents/Reference/`
- **macOS tools**: `sips` (HEIC→JPG, built-in), `rsvg-convert` (librsvg, SVG→JPG — `brew install librsvg`), `magick` (ImageMagick, whitespace trim)
- **Python**: `os`, `shutil`, `datetime`

## Workflow

### Step 1: Scan source folder
Check `/Users/greggy/Documents/Reference/` for `.png .jpg .jpeg .gif .webp .heic .svg`. If zero files: stop and report "No image files found in /Users/greggy/Documents/Reference/. Import cancelled."

### Step 2: Present import + move plan, get user approval
Before touching anything, print a summary: file counts by type, conversion plan, destination `~/Greggy-AI/Reference/YYYY-MM-DD/YYYY-MM-DD+{count}/`, Master path, and the source move target `/Users/greggy/Documents/Reference/YYYY-MM-DD-source/`. **Wait for approval.**

### Step 3: Convert HEIC → JPG
`sips -s format jpeg -s formatOptions best --out OUT.jpg IN.heic`
Move the converted JPG to the nested folder (move, not copy). **Delete the original `.heic` from source once the JPG is confirmed in the vault** (magic-byte check `\xff\xd8\xff` first — never delete before the JPG lands).

### Step 4: Convert SVG → JPG
`rsvg-convert -w 1920 -h 1080 -o output.jpg input.svg` (fallback: `magick input.svg -density 300 -depth 8 -quality 95 output.jpg` — may fail on text).
Move converted JPG to nested folder. **Keep original SVG in source.** Never copy raw SVGs into the nested folder.

### Step 5: Trim whitespace — SVG-derived JPGs only
`magick input.jpg -trim +repage output.jpg`. Do NOT trim HEIC→JPG or other formats.

### Step 6: Create date-marked folders
Parent `~/Greggy-AI/Reference/YYYY-MM-DD/`, nested `.../YYYY-MM-DD/`. If parent exists, append `_a`, `_b`, … then create the nested folder.

### Step 7: Copy remaining images
Copy PNG/GIF/WEBP/JPG into the nested folder. Skip unprocessed `.heic`/`.svg`.

### Step 8: Count images (files actually in nested folder) and rename
Nested folder → `YYYY-MM-DD+{count}/`; Master file → `Master+{count}.md`. Update all links accordingly.

### Step 9: Create Master.md
At `~/Greggy-AI/Reference/YYYY-MM-DD/Master+{count}.md` (PARENT folder, not nested): one Obsidian embed per image. Use **bare-filename embeds** `![[filename.ext]]` when filenames are unique vault-wide (verify with `find "$VAULT" -name <f>` before writing); otherwise full-vault-path embeds `![[Reference/YYYY-MM-DD/YYYY-MM-DD+{count}/filename.ext]]`. NEVER plain `![]()` Markdown links (spaces break them) and NEVER note-relative paths like `![[folder/file]]` — Obsidian wikilink paths resolve from the vault root only (both cost live fixes 2026-10-18).

### Step 10: Move source files
Move all source images from `/Users/greggy/Documents/Reference/` into `/Users/greggy/Documents/Reference/YYYY-MM-DD-source/` (or `_a`, `_b`, …). This keeps the active source folder clean.

### Final structure
```
~/Greggy-AI/Reference/YYYY-MM-DD/
├── Master+{count}.md
└── YYYY-MM-DD+{count}/   (images incl. converted JPGs)

/Users/greggy/Documents/Reference/YYYY-MM-DD-source/
└── originals incl. .heic/.svg
```

### Step 11: Auto-sync to Knowledge
Whenever this skill changes, rewrite `~/Greggy-AI/Knowledge/Import Ref Image Skill.md` with first line `# Updated: YYYY-MM-DD HH:MM:SS ET`. (The folder is `Knowledge` — an older misspelling circulated; do not resurrect it.)

### Step 12: Verify visibility before reporting completion
Before telling the user images are visible, run one script asserting ALL of: (a) every embed target in `Master+{count}.md` exists in the nested folder; (b) every file passes magic-byte validation (`\x89PNG` / `\xff\xd8\xff`); (c) every filename is ASCII-only; (d) zero `.heic` among embeds. Report success only when all four pass; name failures explicitly. Never claim "visible" on inference.

## Pitfalls
- Obsidian cannot display HEIC inline — a `.heic` sitting in the vault is a guaranteed "image not visible" complaint. Scan the DESTINATION root for stray `.heic` too: convert via `sips` into the dated nested folder, embed the JPG, move the HEIC original to the source `-source` folder.
- If the vault's prior dated folder vanished but the source `YYYY-MM-DD-source/` survives, rebuild the vault import from that folder — it is the source of record.
- Import destination (`~/Greggy-AI/Reference/`) and source move destination (`/Users/greggy/Documents/Reference/…-source/`) are SEPARATE — never confuse them
- Capital `Reference/` always
- HEIC via `sips` only (not heif-convert/magick); HEIC originals ARE deleted after verified JPG placement (changed 2026-10-18 by Greg — replaces old keep-original rule)
- SVG originals never enter the nested folder; JPG derivative only
- Transparency in SVGs: convert RGBA → RGB before saving JPG
- Naming uses `+` before count: `+15` folder, `Master+15.md` — not `_15+`
- Master.md lives in the PARENT date folder
- Embed syntax: bare-filename wikilinks `![[file.png]]` (unique names) or full vault path `![[Reference/date/date+N/file.png]]`. NOT `![alt](path)` (spaces break), NOT note-relative `![[date+N/file]]` (wikilinks resolve from vault root only)
- **Sanitize filenames on vault copy**: macOS screenshots use U+202F narrow no-break space before AM/PM — replace `\u202f`/`\u00a0` with plain space when copying into the vault (Obsidian link resolution normalizes the character and then fails to find the file). Keep originals untouched in the source -source folder.
- Filename-uniqueness check before writing bare embeds: `find ~/Greggy-AI -name "<file>"` must return exactly one hit
- Rename folder/file with count AFTER copying, then rewrite every link in Master.md
- Date format `%Y-%m-%d`; Knowledge-note timestamps in Eastern Time

See `references/import-ref-images.md` for full code snippets.
