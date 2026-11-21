#!/usr/bin/env python3
"""Conservative monitor for Cabinet Office youth-gender migration figures.

Re-check 2026 White Paper and update only if both the anchored text and its
explicit prior-year comparison are unambiguous. Check the next White Paper for
publication but never merge future-year figures automatically.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import urllib.request
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "youth_migration_gender.json"
OLD_URL = "https://www.gender.go.jp/about_danjo/whitepaper/r08/zentai/html/honpen/b1_s03_00.html"
NEXT_URL = "https://www.gender.go.jp/about_danjo/whitepaper/r09/zentai/html/honpen/b1_s03_00.html"
NEXT_YEAR = 2026

class StripHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.out=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ("script","style"):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip:self.out.append(data)

def get_text(url):
    request=urllib.request.Request(url,headers={"User-Agent":"ShibainuSokenAtlas/1.0 (+https://github.com/nobby11334/remote-work-atlas)"})
    with urllib.request.urlopen(request,timeout=25) as response:
        enc=response.headers.get_content_charset() or "utf-8"
        blob=response.read(2_000_000).decode(enc,errors="replace")
    parser=StripHTML();parser.feed(blob)
    return re.sub(r"\s+"," "," ".join(parser.out)).replace("％","%").replace("．",".")

def detect_publication(text):
    # Look for the 2026 reporting year and the specific figure on the same official page.
    return bool(re.search(r"(令和8|令和８|2026).{0,120}(10[～〜~-]20代|10～20代).{0,80}転出超過",text))

def check_existing():
    current=json.loads(TARGET.read_text(encoding="utf-8"))
    try:
        txt=get_text(OLD_URL)
    except Exception as exc:
        print("WARNING existing White Paper unavailable:",exc,file=sys.stderr);return
    # Narrow exact sentence of the White Paper: year, female %, prior point increase, male %, and unchanged comparison.
    pat=(r"令和[７7]（2025）年の10[～〜]20代女性の転出超過数の割合は"
         r"\s*([0-9]+\.[0-9]+)%（前年比([0-9]+\.[0-9]+)%ポイント増）、"
         r"同年代男性の転出超過数の割合は([0-9]+\.[0-9]+)%（前年と同様）")
    m=re.search(pat,txt)
    if not m:
        print("WARNING explicit 2025 gender comparison not found; retain reviewed baseline.")
        return
    female=float(m.group(1));increase=float(m.group(2));male=float(m.group(3))
    prev_female=round(female-increase,2)
    # Safety bounds + anchor to same-edition reviewed estimates.
    if not all(0<=x<=5 for x in (female,prev_female,male,increase)):
        print("WARNING out-of-range values",file=sys.stderr);return
    if abs(current["female"][-1]-female)>0.2 or abs(current["male"][-1]-male)>0.2:
        print("WARNING unexpected source change requires manual review",file=sys.stderr);return
    vals=[prev_female,female]
    males=[male,male]
    if current["years"]==[2024,2025] and (current["female"]!=vals or current["male"]!=males):
        print("VERIFIED same-edition correction",current["female"],"=>",vals)
        current["female"]=vals;current["male"]=males
        current["updated_at"]=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat()
        current["verified"]="official_text_auto_reverified"
        TARGET.write_text(json.dumps(current,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:print("Current White Paper unchanged.")

def check_next_year():
    try:txt=get_text(NEXT_URL)
    except Exception as exc:
        print("Next-year White Paper not retrievable (not necessarily unpublished):",exc)
        return
    if not detect_publication(txt):
        print("No independently verifiable 2026 figure on 2027 White Paper page.")
        return
    print("2026 annual update candidate detected. Human verification required.")
    path=os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path,"a",encoding="utf-8") as o:o.write("new_report=true\n")
    with open("/tmp/migration-report-issue.md","w",encoding="utf-8") as o:
        o.write("新しい内閣府男女共同参画白書の『地域における10～20代転出超過割合』公表候補を検知。\n")
        o.write("確認ページ: "+NEXT_URL+"\n\n- [ ] 公表年・対象地域・分母・男女・年齢階級の定義を確認\n")
        o.write("- [ ] 2025年との比較可能性を審査\n- [ ] 公表CSVまたは本文と全数値を照合\n")
        o.write("- [ ] data/youth_migration_gender.json に検証済みの新年度値を追加\n")
        o.write("注意：数値を新しい年度として自動追記しない。\n")

def main():
    check_existing()
    check_next_year()

if __name__=="__main__":main()
