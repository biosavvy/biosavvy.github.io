#!/usr/bin/env python3
"""Fix trust strip (4 items 2x2) + tighten global spacing across all articles."""
import re, os

ARTICLE_DIR = "/tmp/biosavvy-github"

# ---- 1. Trust strip HTML: 3 items -> 4 items ----
OLD_TRUST_HTML = """ <div class="trust-strip">
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
   <span><strong>Independently Rated</strong> &mdash; No brand sponsorships influence our picks</span>
  </div>
 </div>"""

NEW_TRUST_HTML = """ <div class="trust-strip">
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
   <span class="trust-icon">&#x1F4B3;</span>
   <span><strong>Same Price For You</strong> &mdash; Affiliate links never increase your cost</span>
  </div>
 </div>"""

# ---- 2. CSS replacements (with enough context to be unique) ----
CSS_REPLACEMENTS = [
    # Trust strip: flex -> 2x2 grid, tighter padding
    (
        """  .trust-strip {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--white) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 28px;
    margin-bottom: 32px;
    display: flex;
    gap: 28px;
    align-items: center;
    flex-wrap: wrap;
  }""",
        """  .trust-strip {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--white) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px 20px;
  }"""
    ),
    # Trust item: tighten
    (
        """  .trust-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    color: var(--text-light);
    font-weight: 500;
  }""",
        """  .trust-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--text-light);
    font-weight: 500;
  }"""
    ),
    # Body line-height
    (
        """  body {
   font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
   color: var(--text);
   background: var(--bg);
   line-height: 1.65;""",
        """  body {
   font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
   color: var(--text);
   background: var(--bg);
   line-height: 1.55;"""
    ),
    # Hero padding
    (
        """  .hero {
   background: linear-gradient(135deg, #042F2E 0%, #0D9488 45%, #0F766E 100%);
   color: var(--white);
   padding: 70px 0 60px;""",
        """  .hero {
   background: linear-gradient(135deg, #042F2E 0%, #0D9488 45%, #0F766E 100%);
   color: var(--white);
   padding: 45px 0 35px;"""
    ),
    # Hero responsive
    (".hero { padding: 50px 0 40px; }", ".hero { padding: 35px 0 30px; }"),
    # Intro padding
    (
        """  .intro {
   padding: 50px 0 30px;
  }""",
        """  .intro {
   padding: 30px 0 20px;
  }"""
    ),
    # Intro p margin
    (
        """  .intro p {
   font-size: 1.08rem;
   color: var(--text-light);
   max-width: 780px;
   margin-bottom: 16px;
  }""",
        """  .intro p {
   font-size: 1.08rem;
   color: var(--text-light);
   max-width: 780px;
   margin-bottom: 10px;
  }"""
    ),
    # Comparison section
    (
        """  .comparison-section {
   padding: 50px 0 30px;
  }""",
        """  .comparison-section {
   padding: 30px 0 20px;
  }"""
    ),
    # Products section
    (
        """  .products-section {
   padding: 30px 0 60px;
  }""",
        """  .products-section {
   padding: 20px 0 40px;
  }"""
    ),
    # Product card gap
    (
        """   box-shadow: var(--shadow);
   margin-bottom: 32px;
   border: 1px solid var(--border);""",
        """   box-shadow: var(--shadow);
   margin-bottom: 22px;
   border: 1px solid var(--border);"""
    ),
    # Card header padding
    (
        """  .card-header {
   color: var(--white);
   padding: 24px 28px;
  }""",
        """  .card-header {
   color: var(--white);
   padding: 18px 22px;
  }"""
    ),
    # Card body padding
    (
        """  .card-body {
   padding: 10px 20px 24px;
  }""",
        """  .card-body {
   padding: 8px 20px 18px;
  }"""
    ),
    # Card badge row padding
    (
        """  .card-badge-row {
   padding: 0 28px;""",
        """  .card-badge-row {
   padding: 0 22px;"""
    ),
    # Science section
    (
        """  .science-section {
   padding: 20px 0 50px;
  }""",
        """  .science-section {
   padding: 16px 0 35px;
  }"""
    ),
    # FAQ section
    (
        """  .faq-section {
   padding: 20px 0 60px;
  }""",
        """  .faq-section {
   padding: 16px 0 40px;
  }"""
    ),
    # Quick tips section
    (".quick-tips-section { padding: 0 0 30px; }", ".quick-tips-section { padding: 0 0 20px; }"),
    # Trust strip responsive
    (
        "    .trust-strip { flex-direction: column; gap: 12px; }",
        "    .trust-strip { grid-template-columns: 1fr; }"
    ),
]

for i in list(range(1, 18)):
    fname = os.path.join(ARTICLE_DIR, f"article{i}.html")
    if not os.path.exists(fname):
        continue
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # Trust strip HTML
    if OLD_TRUST_HTML in html:
        html = html.replace(OLD_TRUST_HTML, NEW_TRUST_HTML)

    # CSS replacements
    for old, new in CSS_REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)

    if html != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ article{i}.html")
    else:
        print(f"  — article{i}.html (no changes)")

print("\nDone.")
