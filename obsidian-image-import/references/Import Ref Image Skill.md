# Updated: 2026-10-18 19:48:01 ET
# Updated: 2026-10-12 17:11:23 ET

## Import Reference Images (Import Ref Image Skill)

> **Note (2026-10-12):** This workflow was moved out of the `obsidian` skill into its own learned skill: **`obsidian-image-import`** (`~/.hermes/skills/note-taking/obsidian-image-import/`). Content below remains the canonical workflow.

Full workflow for importing images from a source folder into Obsidian Reference with date-marked folders, HEIC→JPG conversion, and auto-generated Master.md with embedded images and image count.

Pitfall: **Import destination vs source destination are separate directories.** Master.md and nested image folders go to **notetaker Reference** (`~/Greggy-AI/Reference/`); converted originals and moved source files go to **source folder** (`/Users/greggy/Documents/Reference/YYYY-MM-DD-source/`). Never confuse the two.

### Prerequisites
- **Obsidian vault path**: `~/Greggy-AI`
- **Reference folder (import destination)**: `~/Greggy-AI/Reference/` (capital R)
- **Source folder**: `/Users/greggy/Documents/Reference` (where images are found)
- **macOS tools**: `sips` (built-in, converts HEIC→JPG), `rsvg-convert` (librsvg, SVG→JPG), `magick` (ImageMagick, whitespace trimming)
- **Python**: `os`, `shutil`, `datetime` modules

### Step 1: Check Source Folder for Image Files

First, check if there are any image files in the source folder `/Users/greggy/Documents/Reference`:

```python
import os

source_dir = "/Users/greggy/Documents/Reference"
image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic', '.svg']

image_files = []
for item in os.listdir(source_dir):
    full = os.path.join(source_dir, item)
    if os.path.isfile(full):
        ext = os.path.splitext(item)[1].lower()
        if ext in image_extensions:
            image_files.append(item)

print(f"Found {len(image_files)} image files in {source_dir}")
```

**If zero image files are found**, stop the import process and report:

> "No image files found in /Users/greggy/Documents/Reference/. Import cancelled."

### Step 1.5: Present Import Plan and Source File Move Plan for Approval

Before executing, present a summary of both the import plan AND the source file move plan, then **wait for user approval**:

```python
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# Categorize files
heic_files = [f for f in image_files if f.lower().endswith('.heic')]
svg_files = [f for f in image_files if f.lower().endswith('.svg')]
png_files = [f for f in image_files if f.lower().endswith('.png')]
jpg_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg'))]
other_files = [f for f in image_files if f.lower().endswith(('.gif', '.webp'))]

# Show file details
print("\n=== IMPORT PLAN ===")
print(f"\nSource: /Users/greggy/Documents/Reference")
print(f"Date: {today}")

print(f"\n📁 File Summary:")
print(f"  HEIC files:    {len(heic_files)} → convert to JPG, move JPG to nested folder, keep original")
for f in sorted(heic_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print(f"  SVG files:     {len(svg_files)} → convert to JPG, move JPG to nested folder, keep original")
for f in sorted(svg_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print(f"  PNG files:     {len(png_files)} → copy to nested folder")
for f in sorted(png_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print(f"  JPG/JPEG files:{len(jpg_files)} → copy to nested folder")
for f in sorted(jpg_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print(f"  Other files:   {len(other_files)} → copy to nested folder")
for f in sorted(other_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print(f"  ─────────────────────────────")
print(f"  Total:         {len(image_files)} files")

print(f"\n📂 Import Destination:")
print(f"  Nested folder: ~/Greggy-AI/Reference/{today}/{today}+{len(image_files)}/")
print(f"  Master file:   ~/Greggy-AI/Reference/{today}/Master+{len(image_files)}.md")

print(f"\n📦 Source File Move Plan:")
print(f"  Move to: /Users/greggy/Documents/Reference/{today}-source/")
print(f"  All {len(image_files)} source image files will be moved from /Users/greggy/Documents/Reference/")
print(f"  ── Files to be moved ──")
for f in sorted(image_files):
    size = os.path.getsize(os.path.join(source_dir, f))
    print(f"    └─ {f} ({size:,} bytes)")

print("\n" + "=" * 40 + "\n")
```

**Wait for user approval before proceeding to Step 2.** If the user says "approve" or "proceed", continue. If the user says "cancel" or "no", stop the import process.

### Step 2: Convert HEIC to JPG and Move to Nested Folder

For each `.heic` file:
1. Convert to JPG: `sips -s format jpeg -s formatOptions best --out OUTPUT.jpg INPUT.heic`
2. **Move the converted JPG** to the nested folder (do NOT copy)
3. **DO NOT delete the original `.heic` file** — keep it in the source folder

```python
for heic_file in sorted(os.listdir(source_dir)):
    if heic_file.lower().endswith('.heic'):
        src = os.path.join(source_dir, heic_file)
        jpg_name = os.path.splitext(heic_file)[0] + '.jpg'
        jpg_dst = os.path.join(source_dir, jpg_name)
        
        # Convert
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', 'best',
                        '--out', jpg_dst, src], check=True)
        
        # Move JPG to nested folder
        shutil.move(jpg_dst, os.path.join(nested_path, jpg_name))
        
        # Do NOT delete original HEIC — leave it in source folder
```

### Step 3: Convert SVG to JPG and Move to Nested Folder

For each `.svg` file, convert to JPG using `rsvg-convert` (librsvg) or Inkscape:

**Option A: rsvg-convert (librsvg — recommended)**

```bash
rsvg-convert -w 1920 -h 1080 -o output.jpg input.svg
```

**Option B: Inkscape CLI**

```bash
inkscape -w 1920 -h 1080 -e output.jpg input.svg
```

**Option C: ImageMagick (fallback — may fail with SVGs containing text)**

```bash
magick input.svg -density 300 -depth 8 -quality 95 output.jpg
```

**IMPORTANT:** After successful SVG→JPG conversion:
1. **Move the converted JPG** to the nested folder (do NOT copy)
2. **DO NOT delete the original `.svg` file** — keep it in the source folder
3. **Do NOT copy the SVG into the nested folder** — only the JPG copy goes in

### Step 4: Trim Whitespace (SVG Only)
Trim whitespace/margins ONLY from SVG files that have been converted to JPG. Do not trim other image formats.

For SVG-converted JPGs with excessive whitespace, use `magick` (ImageMagick):
```bash
magick input.jpg -trim +repage output.jpg
```

This step does NOT apply to HEIC→JPG or other image conversions — only to images that originated as SVG files.

### Step 5: Create Date-Marked Folders
Create nested folders in the **notetaker Reference folder** (`~/Greggy-AI/Reference/`):
- Parent: `~/Greggy-AI/Reference/YYYY-MM-DD/`
- Nested: `~/Greggy-AI/Reference/YYYY-MM-DD/YYYY-MM-DD/`

Use today's date: `datetime.now().strftime("%Y-%m-%d")`

**If the parent date folder already exists**, append a sequential alphabetical letter:
- First attempt: `YYYY-MM-DD_a/`
- If `_a` exists: `YYYY-MM-DD_b/`
- And so on: `_c`, `_d`, `_e`, ...

```python
import os
from datetime import datetime

base = os.path.expanduser("~/Greggy-AI/Reference")
date_str = datetime.now().strftime("%Y-%m-%d")
parent_path = os.path.join(base, date_str)

# If parent already exists, find next available letter
letter_index = 0
parent_path = os.path.join(base, date_str)
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

Use the resolved `parent_path` and `nested_path` for all subsequent steps.

### Step 6: Copy Remaining Image Files
Copy only the remaining image files (PNG, GIF, WEBP, and existing JPGs) into the nested folder. 

**Do NOT copy `.heic` or `.svg` files** — they should have been converted and moved to the nested folder in Steps 2-3. If any `.heic` or `.svg` files remain, skip them (they were not processed).

Only files with extensions `.png`, `.gif`, `.webp`, `.jpg`, `.jpeg` should be copied.

### Step 7: Count Images
```python
image_count = sum(
    1 for item in os.listdir(nested_dir)
    if os.path.isfile(os.path.join(nested_dir, item))
    and os.path.splitext(item)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic']
)
```

### Step 8: Rename with Count
Rename both the nested folder and Master file to include the image count with a `+` prefix:
- Nested folder: `YYYY-MM-DD/YYYY-MM-DD+{count}/`
- Master file: `Master+{count}.md`
- Update ALL image links in Master.md to use the new directory name

### Step 9: Create Master.md
Create the master file in the PARENT folder (not nested) within the **notetaker Reference folder**:
- Path: `~/Greggy-AI/Reference/YYYY-MM-DD/Master+{count}.md`
- Content: `![filename](YYYY-MM-DD+{count}/filename)` for each image

### Step 10: Move Source Files to Date-Marked Folder
After the import process is complete, move ALL image files from the source folder (`/Users/greggy/Documents/Reference`) to a date-marked folder in that same directory.

Create a date-marked folder: `/Users/greggy/Documents/Reference/YYYY-MM-DD-source/`
- If it already exists, append alphabetical letter: `YYYY-MM-DD-source_a/`, `YYYY-MM-DD-source_b/`, etc.

Move all image files into this folder:
```python
import os
import shutil
from datetime import datetime

base = "/Users/greggy/Documents/Reference"
date_str = datetime.now().strftime("%Y-%m-%d")
source_folder = os.path.join(base, f"{date_str}-source")

# If source folder exists, find next available letter
letter_index = 0
if os.path.exists(source_folder):
    while True:
        letter = chr(ord('a') + letter_index)
        new_source = os.path.join(base, f"{date_str}-source_{letter}")
        if not os.path.exists(new_source):
            source_folder = new_source
            break
        letter_index += 1

os.makedirs(source_folder, exist_ok=True)

# Move all image files
image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic']
for item in os.listdir(base):
    full = os.path.join(base, item)
    if os.path.isfile(full):
        ext = os.path.splitext(item)[1].lower()
        if ext in image_extensions:
            # Skip the Master.md file and the +{count} image folder
            if item.startswith('Master+') or item.endswith(f'+{image_count}'):
                continue
            shutil.move(full, os.path.join(source_folder, item))
```

This keeps `/Users/greggy/Documents/Reference` clean — all source images are organized in date-marked folders, and the active import files stay in the `YYYY-MM-DD/YYYY-MM-DD+{count}/` structure.

### Final Structure
```
~/Greggy-AI/Reference/YYYY-MM-DD/                        # NOTETAKER Reference folder (import destination)
├── Master+{count}.md                                     # master file with image count
└── YYYY-MM-DD+{count}/                                   # nested folder with images
    ├── IMG_4551.PNG
    ├── IMG_4591.jpg (converted from HEIC, HEIC kept in source)
    ├── IMG_4592.PNG
    ├── logo.jpg (converted from logo.svg, SVG kept in source)
    └── trimmed_image.jpg (whitespace trimmed)

/Users/greggy/Documents/Reference/YYYY-MM-DD-source/      # SOURCE folder (moved source files)
├── IMG_4551.PNG
├── IMG_4591.HEIC
├── IMG_4592.PNG
└── ... (all original source images)
```

### Pitfalls
- **ALWAYS use `Reference/` (capital R)**
- **HEIC conversion**: Use `sips` (macOS built-in), NOT `heif-convert` or `magick`
- **SVG conversion**: Use `rsvg-convert` (librsvg) — convert to JPG, move JPG to nested folder, keep original SVG. Install with `brew install librsvg`. PIL/Pillow cannot read SVG files.
- **Trim whitespace (SVG only)**: Only trim whitespace from SVG-converted JPGs with excessive margins; use `-trim +repage` with ImageMagick. Do NOT trim HEIC→JPG or other image formats.
- **Skip transparent SVGs**: If SVG has transparency, convert to `RGBA` first, then to `RGB` before saving as JPG
- **Naming convention**: Nested folder is `YYYY-MM-DD+{count}/` (e.g., `2026-10-11+15/`), Master file is `Master+{count}.md` (e.g., `Master+15.md`), NOT `_{count}+` suffix
- **Master file placement**: Goes in PARENT folder, not nested
- **Update links**: After renaming, update ALL image links in Master.md to use `YYYY-MM-DD+{count}/` path
- **Count is accurate**: Count only image files that are actually in the nested folder (no SVGs — they were deleted)
- **Date format**: Use `%Y-%m-%d` format (e.g., `2026-10-11`)
- **Rename after copy**: Rename the folder and Master file AFTER copying images and creating Master.md

### Example
User says: "add the images from ~/reference to notetaker in folder Reference in a date marked folder with images organized in a file called Master and covert all HEIC images to JPG"

Response:
1. Check source folder `/Users/greggy/Documents/Reference` for image files — cancel if zero
2. Convert HEIC files to JPG using `sips`
3. Convert SVG files to JPG using `rsvg-convert` (librsvg)
   - **DO NOT DELETE the original SVG file** — keep it in the source folder
   - **Do NOT copy SVG files into the nested folder** — only the JPG copy goes in
4. Trim whitespace from SVG-converted JPGs using `magick -trim +repage` ONLY if needed (not for HEIC→JPG or other formats)
5. Create date-marked folders in **notetaker Reference** (`~/Greggy-AI/Reference/YYYY-MM-DD/`):
   - If `YYYY-MM-DD` exists, create `YYYY-MM-DD_a/`, then `YYYY-MM-DD_b/`, etc.
   - Create nested folder `YYYY-MM-DD/YYYY-MM-DD/`
6. Move HEIC-converted JPGs to nested folder (keep HEIC originals)
7. Move SVG-converted JPGs to nested folder (keep SVG originals)
8. Copy remaining PNG, GIF, WEBP, JPG files to nested folder
9. Count images (e.g., 10)
10. Rename: `YYYY-MM-DD/YYYY-MM-DD/` → `YYYY-MM-DD/YYYY-MM-DD+{count}/`
11. Create `Master+{count}.md` in `~/Greggy-AI/Reference/YYYY-MM-DD/`
12. Move source files from `/Users/greggy/Documents/Reference/` to `YYYY-MM-DD-source/` (or `_a`, `_b`, etc.)
13. **SYNC TO KNOWLEDGE**: Update `~/Greggy-AI/Knowledge/Import Ref Image Skill.md`
14. **TIMESTAMP**: Prepend `# Updated: YYYY-MM-DD HH:MM:SS ET` to the Knowledge note

### Auto-Sync Rule

Whenever any changes are made to this skill (the `Import Reference Images (Import Ref Image Skill)` section), you **MUST** also:
1. Extract the full Import Reference Images section from the skill
2. Write it to `~/Greggy-AI/Knowledge/Import Ref Image Skill.md`
3. Prepend a timestamp line at the top in **Eastern Time**: `# Updated: YYYY-MM-DD HH:MM:SS ET`

Done. Report: "Copied N images to ~/Greggy-AI/Reference/YYYY-MM-DD[_letter]/+{count}/ with Master+{count}.md (included HEIC→JPG, SVG→JPG conversions, and whitespace trimming)"
