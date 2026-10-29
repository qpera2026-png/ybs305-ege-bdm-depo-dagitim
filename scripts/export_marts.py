"""
dbt mart tablolarını Parquet olarak dışa aktarır (dashboard bu dosyaları okur).

Kullanım:  python scripts/export_marts.py
Girdi:     dbt/nova.duckdb (dbt run çıktısı)
Çıktı:     data/marts/*.parquet
"""
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "dbt" / "nova.duckdb"
OUT = ROOT / "data" / "marts"

TABLOLAR = [
    ("marts", "dim_magaza"),
    ("marts", "dim_urun"),
    ("marts", "mart_urun_abc_xyz"),
    ("marts", "mart_magaza_haftalik_talep"),
    ("marts", "mart_dagitim_plani"),
    ("marts", "mart_il_talep_ozeti"),
    ("marts", "mart_gunluk_kategori_satis"),
    ("marts", "mart_gunluk_magaza_ozet"),
    ("marts", "dim_dagitim_merkezi"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)
    for sema, tablo in TABLOLAR:
        hedef = OUT / f"{tablo}.parquet"
        con.execute(f"copy {sema}.{tablo} to '{hedef.as_posix()}' (format parquet)")
        n = con.execute(f"select count(*) from {sema}.{tablo}").fetchone()[0]
        print(f"{tablo:32s} {n:>8,} satır -> {hedef.relative_to(ROOT)}")
    con.close()


if __name__ == "__main__":
    main()
