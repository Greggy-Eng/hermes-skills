#!/usr/bin/env python3
"""Markdown -> .docx converter (proven on Loomstate assessment docs).

Why not docx_create.py specs: spec list items are plain strings (emphasis
flattened) and Word's List Number continues across sections. This script
parses MD directly and renders:
- headings (#..####) with markdown emphasis stripped
- numbered steps with MANUAL counters that restart at every heading
- two-level sub-bullets (• at indent>=3, – at indent>=5), hanging indents
- **bold** runs preserved; `code` de-ticked; *italic* -> plain
- pipe tables -> Table Grid with bold header row
- optional flags: --font Arial (also rewrites theme1.xml major/minor fonts,
  docDefaults and every style — style-only font setting misses theme fonts),
  --black (all runs black incl. footer/header/fields)

Usage: md2docx.py input.md output.docx [--footer TEXT] [--font NAME|none] [--black|--no-black] [--page-numbers]
Defaults: --font Arial --black (Greg's standing formatting defaults; override
explicitly when a doc needs otherwise).
"""
import argparse, re
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def code(t): return re.sub(r"`([^`]*)`", r"\1", t)

def plain(t):
    t = code(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    return re.sub(r"\*([^*]+)\*", r"\1", t).replace("*", "")

def add_runs(par, text):
    text = code(text)
    pos = 0
    def emit(chunk):
        par.add_run(re.sub(r"\*([^*]+)\*", r"\1", chunk).replace("*", ""))
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        if m.start() > pos: emit(text[pos:m.start()])
        r = par.add_run(plain(m.group(1))); r.bold = True
        pos = m.end()
    if pos < len(text): emit(text[pos:])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--footer", default=None)
    ap.add_argument("--font", default="Arial", help="'none' to keep template font")
    ap.add_argument("--black", action=argparse.BooleanOptionalAction, default=True,
                   help="all text black (default on); --no-black to keep theme colors")
    ap.add_argument("--page-numbers", action="store_true",
                   help="centered 'Page X of Y' field footer")
    a = ap.parse_args()

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(215.9), Mm(279.4)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Mm(20)
    if a.footer:
        f = sec.footer.paragraphs[0]; f.text = a.footer
        f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f.runs[0].font.size = Pt(8)

    normal = doc.styles["Normal"]
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(3)

    step_no = 0
    lines = open(a.src, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip(); s = raw.strip()
        if not s or s == "---":
            i += 1; continue
        if s.startswith("#"):
            lvl = len(s) - len(s.lstrip("#"))
            doc.add_heading(plain(re.sub(r"^#+\s*", "", s)), level=min(lvl, 4))
            step_no = 0; i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append([plain(c) for c in cells])
                i += 1
            t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
            for ri, row in enumerate(rows):
                for ci, cell in enumerate(row):
                    par = t.cell(ri, ci).paragraphs[0]; par.add_run(cell)
                    if ri == 0:
                        for r in par.runs: r.bold = True
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m and not raw.startswith(" "):
            step_no += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Mm(9); p.paragraph_format.first_line_indent = Mm(-6)
            r = p.add_run(f"{step_no}. "); r.bold = True
            add_runs(p, m.group(2))
            i += 1; continue
        m = re.match(r"^([-*])\s+(.*)$", s)
        if m:
            indent = len(raw) - len(raw.lstrip())
            p = doc.add_paragraph()
            if indent >= 5:
                p.paragraph_format.left_indent = Mm(15); p.paragraph_format.first_line_indent = Mm(-4)
                p.add_run("– ")
            elif indent >= 3:
                p.paragraph_format.left_indent = Mm(11); p.paragraph_format.first_line_indent = Mm(-4)
                p.add_run("• ")
            else:
                p.paragraph_format.left_indent = Mm(6); p.paragraph_format.first_line_indent = Mm(-4)
                p.add_run("• ")
            add_runs(p, m.group(2))
            i += 1; continue
        p = doc.add_paragraph(); add_runs(p, s); i += 1

    if a.font == "none":
        a.font = None

    if a.page_numbers:
        para = sec.footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        def field(par, instr):
            b = OxmlElement('w:fldSimple'); b.set(qn('w:instr'), instr)
            r = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = "1"; r.append(t); b.append(r)
            par._p.append(b)
        para.add_run("Page "); field(para, "PAGE"); para.add_run(" of "); field(para, "NUMPAGES")
        for r in para.runs: r.font.size = Pt(8)
        for fs in para._p.findall(qn('w:fldSimple')):
            for r in fs.findall(qn('w:r')):
                rPr = OxmlElement('w:rPr')
                sz = OxmlElement('w:sz'); sz.set(qn('w:val'), "16"); rPr.append(sz)
                r.insert(0, rPr)

    if a.font or a.black:
        apply_font_color(doc, a.font, a.black)
    doc.save(a.out)
    if a.font:
        rewrite_theme(a.out, a.font)
    print("saved:", a.out)

def rewrite_theme(path, font):
    """Rewrite theme major/minor fonts — without this, theme-resolved styles
    (headings) still render the template font."""
    import zipfile, os
    tmp = path + ".tmp"
    theme_re = re.compile(r"<a:(major|minor)Font>.*?</a:\1Font>", re.S)
    def repl(m):
        tag = m.group(1)
        return (f'<a:{tag}Font><a:latin typeface="{font}"/><a:ea typeface="{font}"/>'
                f'<a:cs typeface="{font}"/></a:{tag}Font>')
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"word/theme/theme\d+\.xml$", item.filename):
                data = theme_re.sub(repl, data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, path)

def apply_font_color(doc, font, black):
    def force(rPr_holder):
        rPr = rPr_holder.get_or_add_rPr() if hasattr(rPr_holder, "get_or_add_rPr") else None
        if rPr is None: return
        if font:
            rf = rPr.find(qn('w:rFonts'))
            if rf is None:
                rf = OxmlElement('w:rFonts'); rPr.insert(0, rf)
            for at in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(at), font)
        if black:
            c = rPr.find(qn('w:color'))
            if c is None:
                c = OxmlElement('w:color'); rPr.append(c)
            c.set(qn('w:val'), "000000")
    for s_ in doc.styles:
        try: force(s_.element)
        except Exception: pass
    elements = [doc.element] + [sec.footer._element for sec in doc.sections] + \
               [sec.header._element for sec in doc.sections]
    for el_root in elements:
        for r in el_root.iter(qn('w:r')): force(r)
    if font:
        # docDefaults
        sd = doc.styles.element
        dd = sd.find(qn('w:docDefaults'))
        if dd is not None:
            rpd = dd.find(qn('w:rPrDefault'))
            if rpd is not None:
                rpr = rpd.find(qn('w:rPr'))
                if rpr is None:
                    rpr = OxmlElement('w:rPr'); rpd.append(rpr)
                rf = OxmlElement('w:rFonts')
                for at in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(at), font)
                old = rpr.find(qn('w:rFonts'))
                if old is not None: rpr.remove(old)
                rpr.insert(0, rf)

if __name__ == "__main__":
    main()
