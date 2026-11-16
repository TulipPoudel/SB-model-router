import sys
from pathlib import Path
from pypdf import PdfReader

if len(sys.argv) != 3:
    sys.exit("usage: python scripts/pdf_to_txt.py <input.pdf> <output.txt>")
pdf, out = Path(sys.argv[1]).expanduser(), Path(sys.argv[2])
text = "\n\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
out.write_text(text.strip(), encoding="utf-8")
print(f"wrote {out} ({len(text.split())} words). Open it and trim to ~500-700 words from one section.")