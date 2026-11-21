#!/usr/bin/env python3
"""Probe exact original e-Stat Excel content layout without publishing data."""
import io,urllib.request,zipfile,xml.etree.ElementTree as ET
URL="https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040407042&fileKind=0"
def main():
 req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 ShibainuSokenAtlas/1.0"})
 try:
  with urllib.request.urlopen(req,timeout=30) as r:
   blob=r.read(6_000_000);type_=r.headers.get("Content-Type");print("status",r.status,"type",type_,"bytes",len(blob))
 except Exception as e:
  print("DOWNLOAD_FAILED",repr(e));return
 if blob[:2]!=b"PK":
  print("NOT_EXCEL_ZIP",repr(blob[:130]));return
 z=zipfile.ZipFile(io.BytesIO(blob));files=z.namelist();print("ZIP_FILES",files[:12])
 ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
 shared=[]
 if "xl/sharedStrings.xml" in files:
  root=ET.fromstring(z.read("xl/sharedStrings.xml"))
  for si in root.findall("m:si",ns):
   shared.append("".join(t.text or "" for t in si.findall(".//m:t",ns)))
 for sheet in [f for f in files if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")][:2]:
  print("SHEET",sheet)
  root=ET.fromstring(z.read(sheet));rows=root.findall(".//m:sheetData/m:row",ns)
  for row in rows[:36]:
   parts=[]
   for cell in row.findall("m:c",ns):
    v=cell.find("m:v",ns);inline=cell.find("m:is",ns);value=v.text if v is not None else ("".join(t.text or "" for t in inline.findall(".//m:t",ns)) if inline is not None else "")
    if cell.attrib.get("t")=="s" and value.isdigit():value=shared[int(value)]
    if value:parts.append(cell.attrib.get("r","")+"="+value[:48])
   print("ROW",row.attrib.get("r")," ".join(parts[:22])[:650])
if __name__=="__main__":main()
