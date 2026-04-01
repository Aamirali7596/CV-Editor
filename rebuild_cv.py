#!/usr/bin/env python3
"""
rebuild_cv.py  -  ATS-friendly rebuild of AamirAli_Resume_GEN2025.docx

What it does:
  1. Replaces all 3 tables with plain paragraphs  (same content, bold/italic preserved)
  2. Changes every font in the document to Calibri (body, header, footer, styles)
  3. Saves as AamirAli_Resume_ATS.docx  (original is untouched)

Run: python rebuild_cv.py
Then verify: python tailor_resume.py --mode check --doc AamirAli_Resume_ATS.docx
"""

from pathlib import Path
from lxml import etree
from docx import Document
from docx.oxml import OxmlElement

INPUT  = Path("AamirAli_Resume_GEN2025.docx")
OUTPUT = Path("AamirAli_Resume_ATS.docx")
FONT   = "Calibri"

W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"


def wq(name: str) -> str:
    return f"{{{W}}}{name}"


def xq(name: str) -> str:
    return f"{{{XML}}}{name}"


# ─── Font replacement ─────────────────────────────────────────────────────────

def fix_run_el(run_el, font: str):
    """
    Set an explicit font on a w:r element and remove any theme-font
    overrides (asciiTheme etc.) that would silently win over our setting.
    """
    rPr = run_el.find(wq("rPr"))
    if rPr is None:
        rPr = etree.Element(wq("rPr"))
        run_el.insert(0, rPr)

    rFonts = rPr.find(wq("rFonts"))
    if rFonts is None:
        rFonts = etree.SubElement(rPr, wq("rFonts"))

    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        rFonts.set(wq(attr), font)

    # Remove theme-font attrs – they silently override explicit fonts
    for attr in list(rFonts.attrib.keys()):
        if "Theme" in attr or "theme" in attr:
            del rFonts.attrib[attr]


def fix_all_fonts(doc: Document, font: str):
    """Walk every run in body, headers, footers and set font to Calibri."""

    # Body paragraphs
    for para in doc.paragraphs:
        for run in para.runs:
            fix_run_el(run._r, font)

    # Also walk every w:r that python-docx might not expose as a Run
    # (e.g. runs inside list-continuation paragraphs with no style)
    for r_el in doc.element.body.iter(wq("r")):
        fix_run_el(r_el, font)

    # Headers & footers for every section
    for section in doc.sections:
        for hf in (
            section.header, section.footer,
            section.even_page_header, section.even_page_footer,
            section.first_page_header, section.first_page_footer,
        ):
            if hf is None:
                continue
            try:
                for r_el in hf._element.iter(wq("r")):
                    fix_run_el(r_el, font)
            except Exception:
                pass

    # Normal / Default Paragraph style
    try:
        doc.styles["Normal"].font.name = font
    except Exception:
        pass

    # Update theme-level font definitions so Word doesn't re-apply them
    # (walk the styles part XML)
    try:
        styles_el = doc.styles.element
        for rFonts in styles_el.iter(wq("rFonts")):
            for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
                rFonts.set(wq(attr), font)
            for attr in list(rFonts.attrib.keys()):
                if "Theme" in attr or "theme" in attr:
                    del rFonts.attrib[attr]
    except Exception:
        pass


# ─── Run element builder ──────────────────────────────────────────────────────

def build_run(text: str, bold: bool = False, italic: bool = False,
              size_pt: int = 10, font: str = FONT) -> etree._Element:
    """Return a fully-formed w:r element."""
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")

    rFonts = OxmlElement("w:rFonts")
    rFonts.set(wq("ascii"),    font)
    rFonts.set(wq("hAnsi"),    font)
    rFonts.set(wq("cs"),       font)
    rFonts.set(wq("eastAsia"), font)
    rPr.append(rFonts)

    if bold:
        rPr.append(OxmlElement("w:b"))
        rPr.append(OxmlElement("w:bCs"))

    if italic:
        rPr.append(OxmlElement("w:i"))
        rPr.append(OxmlElement("w:iCs"))

    sz = OxmlElement("w:sz")
    sz.set(wq("val"), str(size_pt * 2))
    rPr.append(sz)

    szCs = OxmlElement("w:szCs")
    szCs.set(wq("val"), str(size_pt * 2))
    rPr.append(szCs)

    r.append(rPr)

    t = OxmlElement("w:t")
    t.text = text
    t.set(xq("space"), "preserve")
    r.append(t)

    return r


# ─── Table → paragraph ───────────────────────────────────────────────────────

def table_row_to_para_el(tbl_el) -> etree._Element:
    """
    Convert a 1-row 5-col table XML element into a w:p.

    Column layout in the original tables:
      [0] role / degree   [1] blank   [2] org   [3] location   [4] dates

    Output paragraph:
      <role>   <org>   <location italic>   <dates>
    """
    # Get all cells from the first row directly from XML
    tc_els = tbl_el.findall(f".//{wq('tc')}")

    def extract_from_tc(tc):
        """Pull text + run formatting from a table cell element."""
        # Collect all text
        texts = [t.text or "" for t in tc.iter(wq("t"))]
        txt = "".join(texts).strip()
        if not txt:
            return None, False, False, 10
        # Get formatting from first run
        first_r = tc.find(f".//{wq('r')}")
        b, i, sz = False, False, 10
        if first_r is not None:
            rPr = first_r.find(wq("rPr"))
            if rPr is not None:
                b  = rPr.find(wq("b"))  is not None
                i  = rPr.find(wq("i"))  is not None
                sz_el = rPr.find(wq("sz"))
                if sz_el is not None:
                    val = sz_el.get(wq("val"))
                    sz = int(val) // 2 if val else 10
        return txt, b, i, sz

    # Map cells by index (skip blank cell[1])
    cols = [extract_from_tc(tc) for tc in tc_els]

    # Pad to 5 if fewer cells extracted
    while len(cols) < 5:
        cols.append((None, False, False, 10))

    col0 = cols[0]   # role / degree
    col2 = cols[2]   # company / university
    col3 = cols[3]   # location
    col4 = cols[4]   # dates

    # Build paragraph element
    p = OxmlElement("w:p")

    pPr = OxmlElement("w:pPr")
    spacing = OxmlElement("w:spacing")
    spacing.set(wq("before"), "0")
    spacing.set(wq("after"),  "0")
    pPr.append(spacing)
    p.append(pPr)

    SEP = "     "   # 5 spaces — visual gap between sections
    first = True

    for txt, bold, italic, sz in (col0, col2, col3, col4):
        if not txt:
            continue
        if not first:
            p.append(build_run(SEP, size_pt=sz))
        p.append(build_run(txt, bold=bold, italic=italic, size_pt=sz))
        first = False

    return p


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not INPUT.exists():
        print(f"[ERR]  Not found: {INPUT}")
        return

    print(f"  Input : {INPUT}")
    print(f"  Output: {OUTPUT}\n")

    doc  = Document(str(INPUT))
    body = doc.element.body

    # ── Step 1: replace tables ────────────────────────────────────────────────
    tbl_elements = body.findall(wq("tbl"))
    print(f"  Step 1  Replacing {len(tbl_elements)} table(s) with plain paragraphs...")

    for i, tbl_el in enumerate(tbl_elements):
        first_tc = tbl_el.find(f".//{wq('tc')}")
        label = "".join(t.text or "" for t in first_tc.iter(wq("t"))).strip()[:45]
        new_p = table_row_to_para_el(tbl_el)

        idx = list(body).index(tbl_el)
        body.remove(tbl_el)
        body.insert(idx, new_p)

        print(f"          Table {i + 1}: '{label}'")

    # ── Step 2: change all fonts ──────────────────────────────────────────────
    print(f"\n  Step 2  Setting all fonts to {FONT}...")
    fix_all_fonts(doc, FONT)
    print(f"          Done.")

    # ── Step 3: save ──────────────────────────────────────────────────────────
    doc.save(str(OUTPUT))
    print(f"\n  [OK]  Saved: {OUTPUT.resolve()}")
    print()
    print("  Next: run the ATS check on the new file:")
    print(f"        python tailor_resume.py --mode check --doc {OUTPUT}")
    print()
    print("  To use this as your new tailoring template, update TEMPLATE_CV in")
    print("  tailor_resume.py to point to AamirAli_Resume_ATS.docx")


if __name__ == "__main__":
    print("=" * 60)
    print("   CV REBUILD  -  ATS-Friendly Conversion")
    print("=" * 60)
    print()
    main()
