#!/usr/bin/env python3
"""
Insert a demo live photo into one article so we can prove the component
works on the real blog before anything goes live.

    python3 demo_inject.py add     # insert into posts/56549
    python3 demo_inject.py remove  # take it back out
"""
import sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
TARGET = ROOT / "posts/56549/index.html"
MARK = "<!-- lp-demo -->"

BLOCK = f"""{MARK}
<div style="max-width:520px;margin:24px 0">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
       data-live-pvt="/img/livephoto-demo.pvt"
       alt="实况照片演示 - 泳池边的青柠饮品"
       width="520" height="390"
       style="width:100%;height:auto;border-radius:10px;display:block">
</div>
{MARK}"""


def add():
    s = TARGET.read_text(encoding="utf-8")
    if MARK in s:
        print("already present")
        return
    # insert right after the article-container opening tag's header end,
    # simplest reliable anchor: the first "</header>" inside the article
    i = s.find('id="article-container"')
    j = s.find("</header>", i)
    if j == -1:
        print("anchor not found")
        return
    j += len("</header>")
    s = s[:j] + "\n" + BLOCK + s[j:]
    TARGET.write_text(s, encoding="utf-8")
    print("inserted demo live photo into", TARGET)


def remove():
    s = TARGET.read_text(encoding="utf-8")
    if MARK not in s:
        print("not present")
        return
    s = re.sub(re.escape(MARK) + r".*?" + re.escape(MARK), "", s, flags=re.S)
    TARGET.write_text(s, encoding="utf-8")
    print("removed")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "add"
    {"add": add, "remove": remove}.get(cmd, add)()
