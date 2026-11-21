#!/usr/bin/env python3
"""Inspect official 2024/2025 communications survey table-35 raw file shapes."""
from __future__ import annotations
import io,urllib.request,zipfile,xml.etree.ElementTree as ET
for year,id_ in [(2024,"000040278972"),(2025,"000040458853")]:
 url=f"https://www.e-stat.go.jp/stat-search/file-download?statInfId={id_}&fileKind=0"
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 try:
  with urllib.request.urlopen(req,timeout=25) as r:
   b=r.read(4_000_000);print(year,r.status,r.headers.get("Content-Type"),len(b),b[:10])
 except Exception as e:
  print(year,"DOWNLOAD_FAILED",repr(e));continue
 if b[:2]!=b"PK":
  print(year,"NOT_ZIP",b[:180]);continue
 z=zipfile.ZipFile(io.BytesIO(b));print(year,"ZIP",z.namelist()[:10])
 ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
 shared=[]
 if "xl/sharedStrings.xml" in z.namelist():
  root=ET.fromstring(z.read("xl/sharedStrings.xml"))
  shared=["".join(t.text or "" for t in si.findall(".//m:t",ns)) for si in root.findall("m:si",ns)]
 files=[f for f in z.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")]
 for sheet in files[:2]:
  root=ET.fromstring(z.read(sheet));rows=root.findall(".//m:sheetData/m:row",ns)
  print(year,"sheet",sheet,"rows",len(rows))
  for row in rows[:30]:
   cells=[]
   for c in row.findall("m:c",ns):
    val=c.find("m:v",ns)
    raw=val.text if val is not None and val.text is not None else ""
    if c.get("t")=="s" and raw.isdigit():raw=shared[int(raw)]
    if raw:cells.append(c.get("r")+"="+raw[:60])
   print(year,"ROW",row.get("r")," ".join(cells[:22])[:520])
