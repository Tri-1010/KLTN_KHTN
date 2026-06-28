"""Check if VnExpress listing carries a date anywhere (attr/json) to avoid per-article fetch."""
import sys
for _s in (sys.stdout, sys.stderr):
    rc = getattr(_s, "reconfigure", None)
    if rc:
        try:
            rc(encoding="utf-8", errors="replace")
        except Exception:
            pass
import re, requests
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip, deflate"}
r = requests.get("https://vnexpress.net/kinh-doanh/chung-khoan", headers=H, timeout=20)
s = BeautifulSoup(r.text, "html.parser")
art = s.select_one("article.item-news")
print("ITEM HTML (first 1500 chars):")
print(str(art)[:1500])
# Look for any timestamp-like attribute across items
print("\nAttributes containing 'time' or digits that look like epoch:")
for el in art.find_all(True):
    for k, v in el.attrs.items():
        if "time" in k.lower() or (isinstance(v, str) and re.fullmatch(r"\d{10}", v)):
            print(f"  <{el.name}> {k}={v}")
