# Import Reference Images

Import images from `/Users/greggy/Documents/Reference/` into the vault `~/Greggy-AI/Reference/` with date-marked nested folders, HEIC→JPG conversion, SVG→JPG conversion, whitespace trimming, and auto-generated Master.md.

## Prerequisites

- **Obsidian vault path**: `~/Greggy-AI`
- **Reference folder**: `~/Greggy-AI/Reference/` (capital R — do NOT use lowercase)
- **macOS tools**: `sips` (HEIC→JPG), `rsvg-convert` (librsvg, SVG→JPG), `magick` (ImageMagick, whitespace trimming)
- **Python**: `os`, `shutil`, `datetime` modules

## Pitfalls

- **Import destination vs source are separate**: Master.md and image folders go to `~/Greggy-AI/Reference/`; moved source files go to `/Users/greggy/Documents/Reference/YYYY-MM-DD-source/`
- **ALWAYS use `Reference/` (capital R)** — user's vault uses capital R
- **HEIC conversion**: Use `sips` (macOS built-in), NOT `heif-convert` or `magick`
- **SVG conversion**: Use `rsvg-convert` (librsvg) — convert to JPG, move to nested folder, **keep original SVG**. PIL/Pillow cannot read SVG files. Install with `brew install librsvg`
- **Trim whitespace (SVG only)**: Only trim SVG-converted JPGs with `-trim +repage`. Do NOT trim HEIC→JPG or other formats
- **Skip transparent SVGs**: Convert to `RGBA` first, then `RGB` before saving as JPG
- **Naming convention**: Nested folder is `YYYY-MM-DD+{count}/`, Master file is `Master+{count}.md`
- **Master file placement**: Goes in PARENT folder (`YYYY-MM-DD/Master+{count}.md`), NOT inside image folder
- **Update links**: All image links in Master.md use `YYYY-MM-DD+{count}/filename` format
- **Count accuracy**: Count only image files actually in the nested folder (includes converted JPGs and PNGs)
- **Date format**: Use `%Y-%m-%d` format (e.g., `2026-10-11`)
- **Empty source check**: If Step 1 finds zero image files in `/Users/greggy/Documents/Reference/`, stop and report "No image files found"
- **Source file move**: After import, move all source images from `/Users/greggy/Documents/Reference/` to `YYYY-MM-DD-source/` folder. Skip `Master+{count}.md` and `YYYY-MM-DD+{count}/` folders
- **Timestamp format**: When syncing to Knowledge note, use Eastern Time: `# Updated: YYYY-MM-DD HH:MM:SS ET`

## Workflow

### Step 1: Check Source Folder for Image Files

Check if there are any image files in `/Users/greggy/Documents/Reference/`. Supported formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.heic`, `.svg`.

If zero image files are found, stop and report: "No image files found in /Users/greggy/Documents/Reference/. Import cancelled."

### Step 2: Convert HEIC to JPG and Move

For each `.heic` file:
```bash
sips -s format jpeg -s formatOptions best --out OUTPUT.jpg INPUT.heic
```
- **Move** the converted JPG to the nested folder (do NOT copy)
- **Keep** the original `.heic` file in the source folder

### Step 3: Convert SVG to JPG and Move

For each `.svg` file, convert to JPG using `rsvg-convert`:
```bash
rsvg-convert -w 1920 -h 1080 -o output.jpg input.svg
```
- **Move** the converted JPG to the nested folder (do NOT copy)
- **Keep** the original SVG file in the source folder

Fallback: ImageMagick may fail with SVGs containing text:
```bash
magick input.svg -density 300 -depth 8 -quality 95 output.jpg
```

### Step 4: Trim Whitespace (SVG Only)

Trim whitespace/margins ONLY from SVG-converted JPGs:
```bash
magick input.jpg -trim +repage output.jpg
```
Do NOT trim HEIC→JPG or other image formats.

### Step 5: Create Date-Marked Nested Folders

Create nested folders in `~/Greggy-AI/Reference/`:
- Parent: `~/Greggy-AI/Reference/YYYY-MM-DD/`
- Nested: `~/Greggy-AI/Reference/YYYY-MM-DD/YYYY-MM-DD/`

If parent date folder already exists, append alphabetical letter: `YYYY-MM-DD_a/`, `YYYY-MM-DD_b/`, etc.

```python
import os
from datetime import datetime

base = os.path.expanduser("~/Greggy-AI/Reference")
date_str = datetime.now().strftime("%Y-%m-%d")
parent_path = os.path.join(base, date_str)

letter_index = 0
if os.path.exists(parent_path):
    while True:
        letter = chr(ord('a') + letter_index)
        new_parent = os.path.join(base, f"{date_str}_{letter}")
        if not os.path.exists(new_parent):
            parent_path = new_parent
            break
        letter_index += 1

nested_path = os.path.join(parent_path, date_str)
os.makedirs(nested_path, exist_ok=True)
```

### Step 6: Copy Remaining Image Files

Copy only PNG, GIF, WEBP, and existing JPG files into the nested folder.

**Do NOT copy `.heic` or `.svg` files** — they should have been converted and moved in Steps 2-3. If any `.heic` or `.svg` files remain, skip them (they were not processed).

### Step 7: Count Images

```python
image_count = sum(
    1 for item in os.listdir(nested_dir)
    if os.path.isfile(os.path.join(nested_dir, item))
    and os.path.splitext(item)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic']
)
```

### Step 8: Rename with Count

Rename nested folder: `YYYY-MM-DD/YYYY-MM-DD/` → `YYYY-MM-DD/YYYY-MM-DD+{count}/`
Master file: `Master+{count}.md`

### Step 9: Create Master.md

Path: `~/Greggy-AI/Reference/YYYY-MM-DD/Master+{count}.md`
Content: `![filename](YYYY-MM-DD+{count}/filename)` for each image

### Step 10: Move Source Files to Date-Marked Folder

Move ALL image files from `/Users/greggy/Documents/Reference/` to `YYYY-MM-DD-source/` (or `YYYY-MM-DD-source_a/`, etc. if exists). Skip `Master+{count}.md` and `YYYY-MM-DD+{count}/` folders.

## Final Structure

```
~/Greggy-AI/Reference/YYYY-MM-DD/                        # NOTETAKER (import destination)
├── Master+{count}.md
└── YYYY-MM-DD+{count}/
    ├── IMG_4551.PNG
    ├── IMG_4591.jpg (converted from HEIC, HEIC kept in source)
    └── ...

/Users/greggy/Documents/Reference/YYYY-MM-DD-source/      # SOURCE (moved files)
├── IMG_4551.PNG
├── IMG_4591.HEIC
└── ...
```

## Auto-Sync Rule

Whenever changes are made to this skill, update `~/Greggy-AI/Knoweldge/Import Ref Image Skill.md` with a timestamp at the top: `# Updated: YYYY-MM-DD HH:MM:SS ET`
