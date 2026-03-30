import os
import io
import re
import uuid
import base64
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_file, send_from_directory

import markdown2
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

# ── CONFIG ──────────────────────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_IMAGE_MB = 10

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_MB * 1024 * 1024


# ── SYNTAX HIGHLIGHTING ──────────────────────────────────────────────────────

# Matches fenced code blocks in raw markdown: ```lang\n...\n```
_FENCE_RE = re.compile(
    r'^```([^\n]*)\n(.*?)^```',
    re.MULTILINE | re.DOTALL,
)

_FORMATTER = HtmlFormatter(
    style="one-dark",
    noclasses=True,
    nowrap=False,
    cssclass="highlight",
)

def _highlight_block(lang: str, code: str) -> str:
    lang = lang.strip()
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except ClassNotFound:
        lexer = guess_lexer(code)
    return highlight(code, lexer, _FORMATTER)


def build_highlighted_html(md_text: str) -> str:
    # Step 1: pull out every fenced block, replace with a placeholder
    # This runs BEFORE markdown2 so it never touches the code
    blocks = {}

    def stash(m):
        lang = m.group(1)
        code = m.group(2)
        key  = f"\x02CODEBLOCK_{len(blocks)}\x03"
        blocks[key] = _highlight_block(lang, code)
        return key

    md_processed = _FENCE_RE.sub(stash, md_text)

    # Step 2: render remaining markdown (no fenced-code-blocks extra needed)
    html = markdown2.markdown(
        md_processed,
        extras=[
            "tables",
            "strike",
            "task_list",
            "header-ids",
            "footnotes",
        ],
    )

    # Step 3: put highlighted blocks back
    for key, highlighted in blocks.items():
        html = html.replace(key, highlighted)

    return html


# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/preview", methods=["POST"])
def preview():
    data = request.get_json(force=True)
    html = build_highlighted_html(data.get("markdown", ""))
    return jsonify({"html": html})


@app.route("/upload-image", methods=["POST"])
def upload_image():
    # multipart upload
    if "image" in request.files:
        f   = request.files["image"]
        ext = Path(f.filename).suffix.lower() if f.filename else ".png"
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "File type not allowed"}), 400
        filename = f"{uuid.uuid4().hex}{ext}"
        f.save(UPLOAD_DIR / filename)
        return jsonify({"url": f"/uploads/{filename}", "filename": filename})

    # base64 / data-URL (paste)
    data     = request.get_json(force=True)
    data_url = data.get("dataUrl", "")
    if not data_url.startswith("data:image/"):
        return jsonify({"error": "Invalid data URL"}), 400

    header, b64 = data_url.split(",", 1)
    mime = header.split(";")[0].split(":")[1]
    ext  = "." + mime.split("/")[1].replace("jpeg", "jpg")
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "File type not allowed"}), 400

    filename = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / filename).write_bytes(base64.b64decode(b64))
    return jsonify({"url": f"/uploads/{filename}", "filename": filename})


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    try:
        from weasyprint import HTML
    except ImportError:
        return jsonify({"error": "weasyprint not installed"}), 500

    data      = request.get_json(force=True)
    html_body = build_highlighted_html(data.get("markdown", ""))
    pygments_css = HtmlFormatter(style="one-dark").get_style_defs(".highlight")

    full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
{pygments_css}
body{{font-family:Georgia,serif;font-size:14px;line-height:1.75;color:#1a1a2e;max-width:800px;margin:0 auto;padding:48px 44px}}
h1,h2,h3,h4{{font-family:Georgia,serif;color:#0d0d1a;margin-top:1.6em;margin-bottom:.35em}}
h1{{font-size:2em;border-bottom:2px solid #e0e0f0;padding-bottom:8px}}
h2{{font-size:1.5em;border-bottom:1px solid #e0e0f0;padding-bottom:4px}}
code{{font-family:'Courier New',monospace;background:#f4f4f8;padding:2px 6px;border-radius:3px;font-size:.87em}}
.highlight{{border-radius:6px;margin:1.2em 0;font-size:.84em;line-height:1.55}}
.highlight pre{{margin:0;padding:18px 22px;overflow:hidden}}
blockquote{{border-left:4px solid #6c63ff;margin:1em 0;padding:8px 20px;background:#f8f8ff;color:#555;font-style:italic}}
table{{border-collapse:collapse;width:100%;margin:1.2em 0}}
th{{background:#1a1a2e;color:#fff;padding:10px 14px;text-align:left;font-size:.85em}}
td{{padding:9px 14px;border-bottom:1px solid #e0e0f0}}
tr:nth-child(even) td{{background:#f8f8ff}}
a{{color:#6c63ff}}
hr{{border:none;border-top:2px solid #e0e0f0;margin:2em 0}}
img{{max-width:100%;border-radius:4px}}
ul,ol{{padding-left:1.5em;margin-bottom:.9em}}
li{{margin:.3em 0}}
</style></head>
<body>{html_body}</body></html>"""

    pdf_bytes = HTML(string=full_html, base_url=f"file://{os.path.abspath('.')}").write_pdf()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"document_{timestamp}.pdf",
    )


if __name__ == "__main__":
    print("✦  Markdown Editor  →  http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)