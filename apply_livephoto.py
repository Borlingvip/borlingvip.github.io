#!/usr/bin/env python3
"""
Install / remove the HeoLivePhoto (实况图) component on the blog.

    python3 apply_livephoto.py inject     # add script tag to every page
    python3 apply_livephoto.py revert     # remove it again
    python3 apply_livephoto.py check      # report coverage

Why a boot snippet instead of a bare <script src>:
  the theme runs on PJAX (pages swap without a full reload), so a
  library that only scans on DOMContentLoaded would enhance the images
  on the first page and then silently do nothing after every in-site
  navigation. The inline loader below bootstraps once and re-scans on
  both pjax:complete and the fallback DOM events.
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT_SRC = "/js/heolivephoto/heolivephoto.js"
MARK_BEGIN = "<!-- heolivephoto:begin -->"
MARK_END = "<!-- heolivephoto:end -->"
VERSION = "?v=1"

SNIPPET = f"""{MARK_BEGIN}
<script>
/* HeoLivePhoto 实况图 — PJAX-safe loader.
   The theme swaps page content without a full reload, so we bootstrap
   the library once and re-scan after each navigation. */
(function () {{
  var SRC = '{SCRIPT_SRC}{VERSION}';

  function scan() {{
    if (window.HeoLivePhoto && window.HeoLivePhoto.scan) {{
      try {{ window.HeoLivePhoto.scan(document); }} catch (e) {{}}
    }}
  }}

  function boot() {{
    if (window.HeoLivePhoto) {{ scan(); return; }}
    if (document.querySelector('script[data-heolivephoto]')) return;
    var s = document.createElement('script');
    s.src = SRC;
    s.async = true;
    s.setAttribute('data-heolivephoto', '1');
    s.onload = scan;
    document.head.appendChild(s);
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', boot);
  }} else {{
    boot();
  }}

  ['pjax:complete', 'pjax:success'].forEach(function (ev) {{
    document.addEventListener(ev, function () {{ setTimeout(scan, 60); }});
  }});
}})();
</script>
{MARK_END}"""


def pages():
    return sorted(p for p in ROOT.rglob("*.html")
                  if "js/heolivephoto" not in p.as_posix())


def inject():
    added = already = 0
    for p in pages():
        s = p.read_text(encoding="utf-8", errors="ignore")
        if MARK_BEGIN in s:
            already += 1
            continue
        if "</body>" in s:
            s = s.replace("</body>", SNIPPET + "\n</body>", 1)
        else:
            s += "\n" + SNIPPET
        p.write_text(s, encoding="utf-8")
        added += 1
    print(f"injected: {added}, already-present: {already}")


def revert():
    removed = 0
    for p in pages():
        s = p.read_text(encoding="utf-8", errors="ignore")
        if MARK_BEGIN not in s:
            continue
        i = s.find(MARK_BEGIN)
        j = s.find(MARK_END, i)
        if j == -1:
            continue
        s = s[:i] + s[j + len(MARK_END):]
        p.write_text(s, encoding="utf-8")
        removed += 1
    print(f"reverted: {removed}")


def check():
    total = with_lp = 0
    for p in pages():
        total += 1
        if MARK_BEGIN in p.read_text(encoding="utf-8", errors="ignore"):
            with_lp += 1
    print(f"pages with heolivephoto: {with_lp}/{total}")
    js = ROOT / SCRIPT_SRC.lstrip("/")
    print("library present:", js.exists(), f"({js.stat().st_size} bytes)" if js.exists() else "")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"inject": inject, "revert": revert, "check": check}.get(cmd, check)()
