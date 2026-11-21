#!/usr/bin/env python3
"""Watch annual e-Stat age/sex migration table 3-3.

2025 annual table is already published, so avoid repeatedly opening an issue.
For 2026 the table normally becomes available only after the year ends.
This is a publication candidate detector, not a data parser.
"""
import os
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

URL="https://www.e-stat.go.jp/stat-search/files?cycle=7&layout=datalist&month=0&tclass1=000001148746&toukei=00200523&tstat=000000070001&year=20260"
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,t):self.parts.append(t)

def main():
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"ShibainuSokenAtlas/1.0"})
        with urllib.request.urlopen(req,timeout=25) as r:
            charset=r.headers.get_content_charset() or "utf-8"
            html=r.read(3_000_000).decode(charset,errors="replace")
        t=Text();t.feed(html);body=re.sub(r"\s+"," "," ".join(t.parts))
    except Exception as exc:
        print("Could not inspect e-Stat listing, not proof of nonpublication:",exc)
        return
    match=bool(re.search(r"(表番号\s*3-3).{0,180}年齢（５歳階級）、男女別転入超過数.{0,300}2026年",body))
    print("2026 annual table 3-3 candidate:",match)
    if match:
        if os.getenv("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"],"a") as out:out.write("found=true\n")
        Path("/tmp/migration-estat.md").write_text(
            "総務省『住民基本台帳人口移動報告』2026年年報・表3-3が公開候補として検知されました。\n\n"
            "出典: "+URL+"\n\n"
            "- [ ] 公式Excelの原表を取得しハッシュ保存\n"
            "- [ ] 移動者／日本人移動者の区分を確定\n"
            "- [ ] 男女、20-24歳、25-29歳の47都道府県の転入超過数を抽出\n"
            "- [ ] 全国・地域合計の整合性を確認\n"
            "- [ ] 前年と同じ分類・地理範囲か検証\n"
            "- [ ] 個人のテレワーク経験率との相関を論ずる際は交絡を注記\n",
            encoding="utf-8")

if __name__=="__main__":main()
