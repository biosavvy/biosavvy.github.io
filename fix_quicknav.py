#!/usr/bin/env python3
"""Fix product quick nav: clean 3+2 layout + add id anchors for jump links."""
import re, os

ARTICLE_DIR = "/tmp/biosavvy-github"

# ---- 1. Fix CSS: replace messy 3+2 nth-child tricks with clean grid ----
OLD_CSS = """  .pq-nav-list {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .pq-nav-list .pq-nav-item:last-child:nth-child(3n-1) {
    grid-column: 1 / -1;
    max-width: calc(50% - 5px);
    justify-self: center;
  }
  .pq-nav-list .pq-nav-item:last-child:nth-child(3n-2) {
    grid-column: 2;
  }"""

NEW_CSS = """  .pq-nav-list {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .pq-nav-list .pq-nav-item:nth-child(4) {
    grid-column: 1;
    grid-row: 2;
    margin-left: calc(50% + 5px);
  }
  .pq-nav-list .pq-nav-item:nth-child(5) {
    grid-column: 2;
    grid-row: 2;
    margin-left: calc(50% + 5px);
  }"""

# ---- 2. Fix pq-nav-item: remove flex:1 that breaks grid widths ----
OLD_ITEM = """  .pq-nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    text-decoration: none;
    color: var(--text);
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.15s ease;
    flex: 1;
    min-width: 160px;
  }"""

NEW_ITEM = """  .pq-nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    text-decoration: none;
    color: var(--text);
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.15s ease;
    min-height: 44px;
    overflow: hidden;
  }"""

for i in list(range(1, 18)):
    fname = os.path.join(ARTICLE_DIR, f"article{i}.html")
    if not os.path.exists(fname):
        continue
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    # Fix CSS: grid layout
    if OLD_CSS in html:
        html = html.replace(OLD_CSS, NEW_CSS)
        changed = True

    # Fix CSS: item style
    if OLD_ITEM in html:
        html = html.replace(OLD_ITEM, NEW_ITEM)
        changed = True

    # Fix HTML: add id to product card articles
    # <article class="product-card product-N"> -> <article id="product-N" class="product-card product-N">
    pattern = r'<article class="product-card (product-\d+)">'
    replacement = r'<article id="\1" class="product-card \1">'
    new_html = re.sub(pattern, replacement, html)
    if new_html != html:
        html = new_html
        changed = True

    if changed:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ {fname}")
    else:
        print(f"  — {fname} (no changes)")

print("\nDone. All files processed.")
