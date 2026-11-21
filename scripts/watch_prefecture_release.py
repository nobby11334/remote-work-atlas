#!/usr/bin/env python3
"""Detect newly published prefecture telework tables without inventing annual figures.
Checks e-Stat listing; a confirmed new annual table opens a tracking issue via CI.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

class Extract(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[]
    def handle_data(self,text):self.parts.append(text)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 ShibainuSokenAtlas/1.0"})
    with urllib.request.urlopen(req,timeout=30) as response:
        raw=response.read(4_000_000)
    parser=Extract();parser.feed(raw.decode("utf-8",errors="replace"))
    return re.sub(r"\s+"," "," ".join(parser.parts))

def main():
    # The 2025 survey is already represented in the Atlas.
    # The 2026 survey is expected to be published during 2027, not in Nov 2026.
    next_survey_year=2026
    url="https://www.e-stat.go.jp/stat-search/files?"+urllib.parse.urlencode({
        "toukei":"00200356","year":str(next_survey_year)+"0",
        "layout":"datalist","page":"1"})
    report={"checked_at":dt.datetime.now(dt.timezone.utc).isoformat(),"survey_year":next_survey_year,"url":url,"detected":False,"verification":"unavailable"}
    try:
        page=fetch(url)
        has_survey=("令和8年通信利用動向調査" in page or "令和８年通信利用動向調査" in page)
        has_table=bool(re.search(r"表番号\s*35\s*問[８8]（２）\s*テレワーク実施の有無",page))
        report["detected"]=bool(has_survey and has_table)
        report["verification"]="listing_contains_exact_year_and_table35" if report["detected"] else "not_found_or_page_incomplete"
    except Exception as exc:
        report["verification"]="fetch_failed";report["error"]=str(exc)[:300]
    print(json.dumps(report,ensure_ascii=False))
    if report["verification"]=="fetch_failed":sys.exit(0) # Fail open on monitoring, never report discovery.
    if report["detected"]:
        with open(os.environ.get("GITHUB_OUTPUT","/tmp/new_table_output"),"a") as f:f.write("found=true\n")
        with open("/tmp/remote-work-atlas-new-source.txt","w") as f:
            f.write("総務省『令和8年通信利用動向調査』世帯構成員編 表35の新規公開候補を検知しました。\n\n")
            f.write("確認ページ: "+url+"\n\n原CSVの取得、前年同設問・母集団との整合、47都道府県の検証が完了するまで自動で値を追加しないでください。\n")
    return 0

if __name__=="__main__":raise SystemExit(main())
