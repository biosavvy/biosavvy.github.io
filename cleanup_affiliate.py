#!/usr/bin/env python3
"""Remove all visible affiliate/commission/sponsor mentions from the site."""
import re, os

ARTICLE_DIR = "/tmp/biosavvy-github"

# ---- 1. Trust strip: remove 4th item, revert to 3 items single row ----
OLD_TRUST_4 = """ <div class="trust-strip">
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

NEW_TRUST_3 = """ <div class="trust-strip">
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

# ---- 2. Trust strip CSS: 2x2 grid back to single row flex ----
OLD_TRUST_CSS = """  .trust-strip {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--white) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px 20px;
  }"""

NEW_TRUST_CSS = """  .trust-strip {
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

# ---- 3. Trust responsive CSS ----
OLD_TRUST_RESP = "    .trust-strip { grid-template-columns: 1fr; }"
NEW_TRUST_RESP = "    .trust-strip { gap: 16px; }"

# ---- 4. Commission spec rows (entire spec-item div) ----
COMMISSION_SPEC_RE = re.compile(
    r'\n\s*<div class="spec-item">\n\s*<div class="spec-label">Commission</div>\n\s*<div class="spec-value">[^<]*</div>\n\s*</div>',
    re.MULTILINE
)

# ---- 5. Commission sentences in product descriptions ----
# Match sentences containing "commission" inside <p class="card-description">
COMMISSION_SENTENCE_RE = re.compile(
    r'\s*[A-Z][^.]*?commission[^.]*\.\s*',
    re.IGNORECASE
)

# ---- 6. Disclaimer cleanups ----
DISCLAIMER_FIXES = [
    # Article16-style disclaimer
    (
        "Some listings contain affiliate links &mdash; we may earn a small commission at no extra cost. Specs and prices subject to change.",
        "Specs and prices subject to change."
    ),
    # Article17-style disclaimer
    (
        "Affiliate links may earn a commission. Consult a healthcare professional before use.",
        "Consult a healthcare professional before use."
    ),
    # Article8-style disclaimer
    (
        "We may earn affiliate commissions from qualifying purchases at no additional cost to you.",
        "All product recommendations are made independently."
    ),
    # Index.html disclaimer
    (
        "We may earn a commission from purchases made through affiliate links, at no extra cost to you. We do not guarantee the accuracy of product information; always verify details before buying.",
        "We do not guarantee the accuracy of product information; always verify details before buying. All recommendations are made independently."
    ),
]

def clean_commission_from_description(match):
    """Remove commission sentences from card-description paragraphs."""
    text = match.group(0)
    # Remove sentences containing 'commission'
    cleaned = re.sub(r'\s*[A-Z][^.]*?commission[^.]*\.', '', text, flags=re.IGNORECASE)
    # Clean up double spaces
    cleaned = re.sub(r'  +', ' ', cleaned)
    return cleaned

files_to_process = []
for i in list(range(1, 18)):
    fname = os.path.join(ARTICLE_DIR, f"article{i}.html")
    if os.path.exists(fname):
        files_to_process.append(fname)
# Also index.html
idx = os.path.join(ARTICLE_DIR, "index.html")
if os.path.exists(idx):
    files_to_process.append(idx)

for fname in files_to_process:
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # 1. Trust strip HTML (articles only)
    if "article" in fname:
        if OLD_TRUST_4 in html:
            html = html.replace(OLD_TRUST_4, NEW_TRUST_3)

        # 2. Trust strip CSS
        if OLD_TRUST_CSS in html:
            html = html.replace(OLD_TRUST_CSS, NEW_TRUST_CSS)

        # 3. Trust responsive CSS
        if OLD_TRUST_RESP in html:
            html = html.replace(OLD_TRUST_RESP, NEW_TRUST_RESP)

        # 4. Commission spec rows
        html = COMMISSION_SPEC_RE.sub('', html)

        # 5. Commission sentences in card descriptions
        # Process each card-description block
        def fix_desc(m):
            full = m.group(0)
            inner = m.group(1)
            cleaned = re.sub(r'\s+[A-Z][^.]*?commission[^.]*\.', '', inner, flags=re.IGNORECASE)
            cleaned = re.sub(r'  +', ' ', cleaned).strip()
            return f'<p class="card-description">{cleaned}</p>'

        html = re.sub(
            r'<p class="card-description">([^<]*(?:commission|Commission)[^<]*)</p>',
            fix_desc,
            html
        )

        # 6. Disclaimers
        for old, new in DISCLAIMER_FIXES:
            if old in html:
                html = html.replace(old, new)

    elif "index" in fname:
        # Index.html disclaimer only
        for old, new in DISCLAIMER_FIXES:
            if old in html:
                html = html.replace(old, new)

    if html != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ {os.path.basename(fname)}")
    else:
        print(f"  — {os.path.basename(fname)} (no changes)")

print("\nDone.")
