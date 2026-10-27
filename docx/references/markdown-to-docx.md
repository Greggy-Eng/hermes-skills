# Markdown → .docx Conversion & Polish

Convert `.md` notes to styled `.docx` with python-docx when pandoc is absent (`command -v pandoc` first). Prefer a direct generator script over `docx_create.py` spec when formatting fidelity matters — the spec's list items are plain strings and cannot carry bold.

## Parser rules (line-by-line)
- `#`…`####` → `add_heading(level)`; strip `**x**` and `*x*` from heading text (emphasis markers in headings survive as stray asterisks otherwise).
- `|` blocks → `Table Grid` table, header row bold.
- Column-0 `^\d+\.\s` → numbered step (see manual-counter rule below).
- Bullets: match with regex `^[-*]\s` only — never `startswith(("-","*"))`, or a paragraph starting with `**bold**` is misclassified as a list item and loses its bold.
- Indent depth sets sub-level: indent ≥3 spaces → `•` first-level sub-bullet; ≥5 → `–` second-level. Never fold nested bullets into the parent item's text with em-dashes — keep them as separate indented paragraphs.
- Emphasis: only paragraph runs can carry bold — split on `**` into runs (`bold=True`); de-tick backticks; for list items/cells strip `**x**` and `*x*` to plain.
- After generating, assert zero leftover `*` and backtick chars across all runs (walk body paragraphs + table cells); mid-paragraph italics are the usual survivors — strip them in the run-emitter itself, not as a later find-replace.

## Numbering that restarts per topic
Word `List Number` continues across lists in one document, so steps run 1..N document-wide — rejected by Greg ("should start new on each topic"). Render steps as manual-counter paragraphs: bold `"{n}. "` run + hanging indent (left 9mm, first-line −6mm), counter reset to 0 at every heading. Sub-bullets: `•` left 11mm, `–` left 15mm. Verify by extracting numbered lines and confirming each section restarts at 1.

## Polish passes
`md2docx.py` does these natively via `--font` (default Arial) and `--black`
(default on) — apply them at generation, not post-hoc. Manual polish on an
existing file:
- **All-black font:** set `font.color.rgb = RGBColor(0,0,0)` on Normal/Heading 1-4/Footer/Header styles AND every run in body, tables, headers, footers — Word headings use theme blue unless directly formatted.
- **Font swap (e.g. Arial):** set `font.name` plus explicit `w:rFonts` attributes `ascii/hAnsi/cs/eastAsia` on styles AND runs AND runs inside `w:fldSimple` fields AND docDefaults `w:rPrDefault/w:rPr` — AND rewrite `word/theme/theme1.xml` `<a:majorFont>/<a:minorFont>` latin/ea/cs typeface (unzip → regex-sub → rezip; the one safe XML text edit). Without the theme rewrite, Greg had to ask twice: headings resolving through theme fonts still rendered Calibri. Verify by unzipping and grepping the OLD font name across `word/document.xml`, `styles.xml`, `footer*.xml`, `theme/*.xml` — the only acceptable leftover is `fontTable.xml` (font *declarations*, not applied to text).
- **Centered page-number footer:** append a second footer paragraph, `alignment=CENTER`, containing `Page ` + `w:fldSimple instr="PAGE"` + ` of ` + `w:fldSimple instr="NUMPAGES"`; style literal runs and the field's inner runs (rPr sz/color) manually. Tell the user numbers populate when Word opens — fields are codes, not text.

## Versioning habit
A structural redo ("make a new revised document") → save `… v2.docx` beside the original and keep v1. Subsequent small tweaks (font color, page numbers, typeface) are applied in place to the latest version.

## Verification checklist
`docx_validate.py` passes; `--structure` shows expected heading outline and table shape; numbered-line count per section confirms restarts; zero emphasis markers and zero old-font references in the package XML.
