#!/usr/bin/env python3
"""Inject (or remove) the Liquid Glass stylesheet link into every page.

Usage:
  python3 apply_lg.py inject   # add <link ... liquid-glass.css> after css/index.css
  python3 apply_lg.py revert   # remove it (full rollback to original UI)
  python3 apply_lg.py check    # report counts
Idempotent.
"""
import sys, glob, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = '<link rel="stylesheet" href="/css/liquid-glass.css?v=12">'
ANCHOR = '<link rel="stylesheet" href="/css/index.css">'
LG_PAT = re.compile(r'<link rel="stylesheet" href="/css/liquid-glass\.css(\?v=\d+)?">')


def pages():
    for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        yield p


def inject():
    added = already = 0
    for p in pages():
        s = open(p, encoding='utf-8').read()
        s = LG_PAT.sub('', s)
        if TAG in s:
            already += 1
            continue
        if ANCHOR in s:
            s = s.replace(ANCHOR, ANCHOR + TAG, 1)
        else:
            s = s.replace('</head>', TAG + '</head>', 1)
        open(p, 'w', encoding='utf-8').write(s)
        added += 1
    print(f'injected: {added}, already-present: {already}')


def revert():
    removed = 0
    for p in pages():
        s = open(p, encoding='utf-8').read()
        if 'liquid-glass' not in s:
            continue
        open(p, 'w', encoding='utf-8').write(LG_PAT.sub('', s))
        removed += 1
    print(f'reverted: {removed}')


def check():
    have = sum(1 for p in pages() if TAG in open(p, encoding='utf-8').read())
    total = sum(1 for _ in pages())
    print(f'pages with liquid-glass: {have}/{total}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    {'inject': inject, 'revert': revert, 'check': check}[cmd]()
