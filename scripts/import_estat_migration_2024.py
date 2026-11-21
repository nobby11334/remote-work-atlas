#!/usr/bin/env python3
"""Import the independently identified official 2024 table 3-3 Excel."""
import import_estat_migration as importer
importer.YEAR=2024
importer.STAT_ID="000040243450"
importer.URL="https://www.e-stat.go.jp/stat-search/file-download?statInfId="+importer.STAT_ID+"&fileKind=0"
importer.OUTPUT=importer.ROOT/"data/prefecture_youth_migration_2024.json"
if __name__=="__main__":importer.main()
