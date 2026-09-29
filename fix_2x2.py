#!/usr/bin/env python3
"""Fix 2x2 layout: add 4th trust item + make 3rd tip full-width."""
import re, os

ARTICLE_DIR = "/tmp/biosavvy-github"

# ---- 1. Trust strip: add 4th item ----
OLD_TRUST_3 = """ <div class="trust-strip">
  <div class="trust-item">
   <span class="trust-icon">&#x1F50D;</span>
   <span><strong>Research-Backed</strong> &mdash; We analyze specs, materials &amp; real user reviews</span>
  </div>
  <div class="trust-item">
   <span class="trust-icon">&#x1F4B0;</span>
   <span><strong>Price Tracked</strong> &mdash; Updated regularly to catch the best deals</span>
  </div>
  <div class="trust-item">
   <span class="trust-icon">&#x2B50;</span>
   <span><strong>Zero Sponsors</strong> &mdash; We accept no sponsorship from any brand</span>
  </div>
 </div>"""

NEW_TRUST_4 = """ <div class="trust-strip">
  <div class="trust-item">
   <span class="trust-icon">&#x1F50D;</span>
   <span><strong>Research-Backed</strong> &mdash; We analyze specs, materials &amp; real user reviews</span>
  </div>
  <div class="trust-item">
   <span class="trust-icon">&#x1F4B0;</span>
   <span><strong>Price Tracked</strong> &mdash; Updated regularly to catch the best deals</span>
  </div>
  <div class="trust-item">
   <span class="trust-icon">&#x2B50;</span>
   <span><strong>Zero Sponsors</strong> &mdash; We accept no sponsorship from any brand</span>
  </div>
  <div class="trust-item">
   <span class="trust-icon">&#x1F504;</span>
   <span><strong>Independently Rated</strong> &mdash; Every pick is based on our own evaluation</span>
  </div>
 </div>"""

# ---- 2. Trust strip CSS: back to 2x2 grid ----
OLD_TRUST_CSS = """  .trust-strip {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--white) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    display: flex;
    gap: 24px;
    align-items: center;
    flex-wrap: wrap;
  }"""

NEW_TRUST_CSS = """  .trust-strip {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--white) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px 20px;
  }"""

# ---- 3. Trust responsive ----
OLD_TRUST_RESP = "    .trust-strip { gap: 16px; }"
NEW_TRUST_RESP = "    .trust-strip { grid-template-columns: 1fr; }"

# ---- 4. Tips: remove centering rule, add full-width for last odd item ----
OLD_TIPS_CENTER = """  .tips-grid .tip-card:last-child:nth-child(odd) {
    grid-column: 1 / -1;
    max-width: 50%;
    justify-self: center;
  }"""

NEW_TIPS_FULLWIDTH = """  .tips-grid .tip-card:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }"""

for i in list(range(1, 18)):
    fname = os.path.join(ARTICLE_DIR, f"article{i}.html")
    if not os.path.exists(fname):
        continue
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # Trust strip HTML
    if OLD_TRUST_3 in html:
        html = html.replace(OLD_TRUST_3, NEW_TRUST_4)

    # Trust strip CSS
    if OLD_TRUST_CSS in html:
        html = html.replace(OLD_TRUST_CSS, NEW_TRUST_CSS)

    # Trust responsive
    if OLD_TRUST_RESP in html:
        html = html.replace(OLD_TRUST_RESP, NEW_TRUST_RESP)

    # Tips centering -> full-width
    if OLD_TIPS_CENTER in html:
        html = html.replace(OLD_TIPS_CENTER, NEW_TIPS_FULLWIDTH)

    if html != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ article{i}.html")
    else:
        print(f"  — article{i}.html (no changes)")

print("\nDone.")
