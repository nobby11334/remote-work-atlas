#!/usr/bin/env python3
"""Parse original e-Stat Excel annual age×sex net migration into JSON.

Source: official annual migration table 3-3. No third-party data sources.
Fails closed if source format or count changes; never publishes partial data.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"data/prefecture_youth_migration_2025.json"
YEAR=2025
STAT_ID="000040407042"
URL="https://www.e-stat.go.jp/stat-search/file-download?statInfId="+STAT_ID+"&fileKind=0"
PREFIX="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS={"x":PREFIX}
COLPAT=re.compile(r"^([A-Z]+)")
PREF_NAMES="北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県".split()

def download():
 req=urllib.request.Request(URL,headers={"User-Agent":"ShibainuSokenAtlas/1.0 (+https://github.com/nobby11334/remote-work-atlas)"})
 with urllib.request.urlopen(req,timeout=35) as r:blob=r.read(8_000_000)
 if blob[:2]!=b"PK":raise ValueError("Original file not ZIP-based XLSX")
 return blob

def colname(cell):return COLPAT.match(cell).group(1)

def workbook_rows(blob):
 z=zipfile.ZipFile(io.BytesIO(blob))
 shared=[]
 if "xl/sharedStrings.xml" in z.namelist():
  root=ET.fromstring(z.read("xl/sharedStrings.xml"))
  for si in root.findall("x:si",NS):
   shared.append("".join((t.text or "") for t in si.findall(".//x:t",NS)))
 root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
 result={}
 for row in root.findall(".//x:sheetData/x:row",NS):
  cells={}
  for c in row.findall("x:c",NS):
   v=c.find("x:v",NS)
   inline=c.find("x:is",NS)
   value=v.text if v is not None and v.text is not None else (
    "".join((t.text or "") for t in inline.findall(".//x:t",NS)) if inline is not None else "")
   if c.get("t")=="s" and value.isdigit():value=shared[int(value)]
   cells[colname(c.attrib["r"])]=value.strip()
  result[int(row.attrib["r"])]=cells
 return result

def main():
 blob=download();rows=workbook_rows(blob)
 assert rows[2].get("B","").startswith("3-3"),"Unexpected table number"
 assert "転入超過" in rows[3].get("B",""),"Unexpected statistical variable"
 genders=rows[4];ages=rows[5]
 def locate(gender,age):
  hits=[col for col,a in ages.items() if a==age and genders.get(col)==gender]
  if len(hits)!=1:raise ValueError("Expected a single "+gender+" "+age+" column, found "+str(hits))
  return hits[0]
 columns={
  "male_20_24":locate("男","20歳～24歳"),
  "male_25_29":locate("男","25歳～29歳"),
  "female_20_24":locate("女","20歳～24歳"),
  "female_25_29":locate("女","25歳～29歳")
 }
 print("Validated columns",columns)
 data=[]
 for record in rows.values():
  code=record.get("F","")
  name=record.get("G","")
  # 01000..47000: prefectures, excluding 00000 nationwide and cities.
  if record.get("B")!="60000" or record.get("E")!=str(YEAR)+"年" or not re.fullmatch(r"(0[1-9]|[1-3][0-9]|4[0-7])000",code):
   continue
  if name!=PREF_NAMES[int(code[:2])-1]:
   raise ValueError("Code/name mismatch: "+code+" "+name)
  item={"code":code,"prefecture":name}
  for key,col in columns.items():
   value=record.get(col)
   if value is None or not re.fullmatch(r"-?\d+",value):
    raise ValueError("Not an integer: "+name+" "+key+" "+str(value))
   item[key]=int(value)
  item["male_20s"]=item["male_20_24"]+item["male_25_29"]
  item["female_20s"]=item["female_20_24"]+item["female_25_29"]
  data.append(item)
 data.sort(key=lambda x:x["code"])
 if len(data)!=47:raise ValueError("Expected 47 prefectures, got "+str(len(data)))
 if len(set(x["code"] for x in data))!=47:raise ValueError("Duplicate prefecture")
 # Net migration between prefectures must cancel out for each age/sex group.
 for key in columns:
  net=sum(p[key] for p in data)
  if net!=0:raise ValueError("Prefecture net migration does not balance for "+key+": "+str(net))
 source_sha=hashlib.sha256(blob).hexdigest()
 output={
  "dataset":f"住民基本台帳人口移動報告・{YEAR}年年報 表3-3",
  "year":YEAR,
  "population":"移動者（日本人・外国人の合計）",
  "unit":"人",
  "meaning":"転入超過数＝他都道府県からの転入者数－他都道府県への転出者数。負数は転出超過。20代は20〜24歳と25〜29歳を合算。",
  "source_url":"https://www.e-stat.go.jp/stat-search/files?layout=dataset&stat_infid="+STAT_ID+"&toukei=00200523",
  "excel_download_url":URL,
  "source_sha256":source_sha,
  "verified":"official_xlsx_auto_parsed_with_47_prefecture_and_zero_sum_checks",
  "extracted_at":dt.datetime.now(dt.timezone.utc).date().isoformat(),
  "limits":"出生率、婚姻、リモートワークの利用状況、勤務先の所在地、転居の理由は含まれない。県間移動の転入超過の集計である。",
  "prefectures":data
 }
 # If the original Excel and extracted numbers are unchanged, do not update timestamps.
 if OUTPUT.exists():
  old=json.loads(OUTPUT.read_text(encoding="utf-8"))
  if old.get("source_sha256")==source_sha and old.get("prefectures")==data:
   print("Source and numbers unchanged; no rewrite");return
 OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Wrote",len(data),"prefectures; top net female 20s:",sorted([(p["prefecture"],p["female_20s"]) for p in data],key=lambda p:p[1],reverse=True)[:5])

if __name__=="__main__":main()
