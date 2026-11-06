"""Render the default social sharing image to static/og.png with headless Chrome.

Run once, or when the text changes: python tools/make_og.py [path-to-chrome]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHROME = sys.argv[1] if len(sys.argv) > 1 else r"C:\Program Files\Google\Chrome\Application\chrome.exe"

HTML = """<!doctype html><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#14171a;color:#ecebe6;display:flex;flex-direction:column;
justify-content:center;padding:0 88px;box-sizing:border-box;font-family:'Palatino Linotype',Georgia,serif}
h1{font-size:84px;margin:0 0 20px;font-weight:600}
p{font-size:38px;margin:0;line-height:1.3}
small{font:26px Consolas,monospace;color:#5cc8bf;margin-top:44px}
</style><h1>Dr. Arbab Latif</h1>
<p>Applied AI engineer: RAG, LLM agents<br>and signal processing</p>
<small>arbablatif.github.io</small>"""

with tempfile.TemporaryDirectory() as folder:
    page = Path(folder) / "og.html"
    page.write_text(HTML, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1200,630", f"--screenshot={ROOT / 'static' / 'og.png'}",
                    page.as_uri()], check=True, capture_output=True)
print("Wrote static/og.png")
