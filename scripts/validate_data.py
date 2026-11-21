#!/usr/bin/env python3
"""Fail closed when published numbers or their provenance become inconsistent."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def load(path):return json.loads((BASE/path).read_text(encoding="utf-8"))
def check():
 p=load("data/prefectures_2025.json")
 names=[r["name"] for r in p["prefectures"]]
 assert len(names)==47 and len(set(names))==47,"47 prefectures required"
 assert all(isinstance(x["rate"],(int,float)) and 0<=x["rate"]<=100 for x in p["prefectures"])
 assert all(isinstance(x["respondents"],int) and x["respondents"]>0 for x in p["prefectures"])
 assert "secondary" in p["status"] and p["primary_source"].startswith("https://www.e-stat.go.jp")
 a=load("data/company_adoption_regions_2019_2024.json")
 n=len(a["survey_years"]);assert n>=2 and all(len(v)==n for v in a["groups"].values())
 assert sorted(a["survey_years"])==a["survey_years"]
 assert all(0<=v<=100 for values in a["groups"].values() for v in values)
 d=load("data/indicators.json")
 ids=[x["id"] for x in d["indicators"]];assert len(ids)==len(set(ids))
 assert {x["source"] for x in d["indicators"]}<={x["id"] for x in d["sources"]}
 for i in d["indicators"]:
  assert 0<=i["value"]<=100
  if "prior_value" in i:assert i["prior_year"]<i["year"] and 0<=i["prior_value"]<=100
 c=load("data/research_coverage.json")
 assert len(c["streams"])>=6
 assert all(x["status"] in {"published","secondary_transcribed","awaiting_raw_data_validation","not_collected"} for x in c["streams"])
 for name in ["school_employment","relocation","job_posts"]:
  assert next(x for x in c["streams"] if x["id"]==name)["status"]=="not_collected"
 migration=load("data/youth_migration_gender.json")
 assert migration["years"]==[2024,2025]
 assert len(migration["female"])==len(migration["male"])==len(migration["years"])
 assert all(0<=v<=5 for k in ("female","male") for v in migration[k])
 assert migration["source"].startswith("https://www.gender.go.jp/")
 assert migration["verified"].startswith("official_text")
 print("PASS: 47 distinct prefectures, sources, bounds, timeseries, evidence-gap labels")
if __name__=="__main__":check()
