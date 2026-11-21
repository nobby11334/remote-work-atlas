#!/usr/bin/env python3
"""Publish tidy reproducible 2024/2025 official age-sex migration CSV."""
import csv,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
output=BASE/"data/prefecture_youth_migration_2024_2025.csv"
rows=[]
for year in (2024,2025):
 d=json.loads((BASE/f"data/prefecture_youth_migration_{year}.json").read_text(encoding="utf-8"))
 assert d["year"]==year and len(d["prefectures"])==47
 for p in d["prefectures"]:
  rows.append({
   "year":year,
   "code":p["code"],
   "prefecture":p["prefecture"],
   "female_20_24_net":p["female_20_24"],
   "female_25_29_net":p["female_25_29"],
   "female_20s_net":p["female_20s"],
   "male_20_24_net":p["male_20_24"],
   "male_25_29_net":p["male_25_29"],
   "male_20s_net":p["male_20s"],
   "source_sha256":d["source_sha256"]
  })
fieldnames=list(rows[0])
import io
buf=io.StringIO(newline="")
writer=csv.DictWriter(buf,fieldnames=fieldnames,lineterminator="\n")
writer.writeheader();writer.writerows(rows)
text=buf.getvalue()
if output.exists() and output.read_text(encoding="utf-8-sig")==text:
 print("CSV unchanged")
else:
 output.write_text(text,encoding="utf-8-sig")
 print("Generated",len(rows),"rows")
