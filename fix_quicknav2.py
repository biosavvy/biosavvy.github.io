#!/usr/bin/env python3
"""Remove quick-nav module + enhance price column in comparison table."""
import re, os

ARTICLE_DIR = "/tmp/biosavvy-github"

# ---- CSS to remove: entire product-quick-nav block ----
CSS_BLOCK = """  .product-quick-nav {
    background: var(--white);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 20px 28px;
    margin-bottom: 32px;
  }
  .product-quick-nav h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 14px;
  }
  .pq-nav-list {
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
  }
  .pq-nav-item {
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
  }
  .pq-nav-item:hover {
    border-color: var(--primary);
    background: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }
  .pq-nav-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    background: var(--primary);
    color: white;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  .pq-nav-emoji { font-size: 1.1rem; flex-shrink: 0; }
  .pq-nav-text { line-height: 1.2; }
  .pq-nav-price {
    margin-left: auto;
    font-weight: 700;
    color: var(--primary);
    font-size: 0.85rem;
    white-space: nowrap;
  }"""

# ---- Responsive CSS line to remove ----
RESP_LINE = "    .pq-nav-item { min-width: 130px; }\n"

# ---- HTML section to remove (with comment + blank lines) ----
HTML_SECTION_PATTERN = re.compile(
    r'\n*<!-- ============ QUICK PRODUCT NAVIGATION ============ -->\n'
    r'<section class="quick-nav-section">\n.*?</section>\n',
    re.DOTALL
)

# ---- Enhanced price-cell CSS ----
OLD_PRICE_CSS = """  .price-cell {
   font-weight: 700;
   color: var(--primary);
   font-size: 1rem;
  }"""

NEW_PRICE_CSS = """  .price-cell {
   font-weight: 800;
   color: var(--primary);
   font-size: 1.1rem;
   letter-spacing: -0.01em;
  }"""

for i in list(range(1, 18)):
    fname = os.path.join(ARTICLE_DIR, f"article{i}.html")
    if not os.path.exists(fname):
        continue
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # Remove CSS block
    if CSS_BLOCK in html:
        html = html.replace(CSS_BLOCK, "")
    # Also try the version with slight whitespace differences
    css_re = re.compile(r'\n  \.product-quick-nav \{\n.*?\n  \}', re.DOTALL)
    if '.product-quick-nav {' in html:
        html = css_re.sub('', html)

    # Remove responsive pq-nav line
    if RESP_LINE in html:
        html = html.replace(RESP_LINE, "")

    # Remove HTML section
    html = HTML_SECTION_PATTERN.sub('\n', html)

    # Enhance price-cell CSS
    if OLD_PRICE_CSS in html:
        html = html.replace(OLD_PRICE_CSS, NEW_PRICE_CSS)

    if html != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ article{i}.html")
    else:
        print(f"  — article{i}.html (no changes)")

print("\nDone.")
