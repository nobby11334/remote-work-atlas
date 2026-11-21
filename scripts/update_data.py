#!/usr/bin/env python3
"""Conservative automatic refresh of reviewed, same-edition public statistics.

No LLM, no scraping guessed figures, no cross-survey joining.
If an official source changes layout or a metric cannot be anchored, keep existing value.
"""
from __future__ import annotations
import datetime as dt
import html
import json
import pathlib
import re
import sys
import urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "indicators.json"
PERSOL = "https://www.persol-group.co.jp/news/20260827_prc01/"
MLIT = "https://www.mlit.go.jp/report/press/toshikankyoteleworkr7.html"

class Plain(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.suppress = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script","style"}:
            self.suppress += 1
    def handle_endtag(self, tag):
        if tag in {"script","style"}:
            self.suppress = max(0,self.suppress-1)
    def handle_data(self, data):
        if not self.suppress:
            self.parts.append(data)

def get(url):
    req = urllib.request.Request(url,headers={"User-Agent":"ShibainuSoken-ResearchAtlas/1.0 (+https://github.com/nobby11334/remote-work-atlas)"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(4_000_000)
        enc=r.headers.get_content_charset() or "utf-8"
    parser=Plain()
    parser.feed(raw.decode(enc,errors="replace"))
    text=html.unescape(" ".join(parser.parts))
    return re.sub(r"\s+"," ",text).replace("％","%").replace("．",".")

# Only capture a percentage when anchored to the indicator's exact label.
# Values in unrelated sections must never be treated as revisions.
PATTERNS={
    "persol_usage": (r"テレワーク実施率は\s*([0-9]{1,2}\.\d)%",PERSOL),
    "persol_office": (r"原則出社.{0,25}?([0-9]{1,2}\.\d)%",PERSOL),
    "persol_wish": (r"継続希望は\s*([0-9]{1,2}\.\d)%",PERSOL),
    "persol_it": (r"情報通信業が\s*([0-9]{1,2}\.\d)%",PERSOL),
    "persol_kanto": (r"関東が\s*([0-9]{1,2}\.\d)%",PERSOL),
    "persol_tokyo": (r"東京都は\s*([0-9]{1,2}\.\d)%",PERSOL),
    "persol_frequency_down": (r"減った[」\s]*が\s*([0-9]{1,2}\.\d)%",PERSOL),
    "mlit_last_year": (r"直近[１1]年間のテレワーク実施率は.{0,75}?([0-9]{1,2}\.\d)%",MLIT),
    "mlit_ever": (r"雇用型テレワーカー.{0,50}?割合は.{0,25}?([0-9]{1,2}\.\d)%",MLIT),
}
# Snapshot is reviewed; changes over 15 points in the same dated release are
# treated as suspicious rather than automatically accepted.
def main():
    d=json.loads(DATA.read_text(encoding="utf-8"))
    sources={}
    for url in {item[1] for item in PATTERNS.values()}:
        try:
            sources[url]=get(url)
            print("Retrieved",url,len(sources[url]))
        except Exception as e:
            print(f"WARNING: Failed to read {url}: {e}", file=sys.stderr)
    changed=[]
    for item in d["indicators"]:
        pair=PATTERNS.get(item["id"])
        if not pair or pair[1] not in sources:
            continue
        match=re.search(pair[0],sources[pair[1]])
        if not match:
            print("WARN: No reliable match for",item["id"])
            continue
        number=float(match.group(1))
        if not (0<=number<=100) or abs(number-item["value"])>15:
            print("WARN: Outlier ignored",item["id"],number)
            continue
        if number!=item["value"]:
            print("Revised",item["id"],item["value"],"->",number)
            item["value"]=number
            changed.append(item["id"])
    if changed:
        d["updated_at"]=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat()
        d["data_status"]="auto_refreshed_same_edition"
        d["last_changed_indicator_ids"]=changed
        DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Changed metrics:",changed or "none; baseline retained")

if __name__=="__main__":
    main()
