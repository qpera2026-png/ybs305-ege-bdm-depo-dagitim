"""
Uçtan uca veri hattını çalıştırır:
  1) NovaPerakende test verisini üret (gerçek veri gelince --veri-uretme ile atlanır)
  2) OSRM API'den mesafeleri çek
  3) dbt build (seed + model + test)
  4) dbt docs generate (+ docs/dbt_docs.html statik kopya)
  5) Mart tablolarını Parquet'e aktar (dashboard girdisi)

Kullanım:  python scripts/run_pipeline.py [--veri-uretme]
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = ROOT / "dbt"
BIN = Path(sys.executable).parent


def calistir(komut, cwd=ROOT):
    print(f"\n>>> {' '.join(map(str, komut))}", flush=True)
    # Windows konsolunda Türkçe karakterler için UTF-8 zorunlu
    subprocess.run(komut, cwd=cwd, check=True, env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri-uretme", action="store_true", help="data/raw'daki mevcut (gerçek) veriyi kullan")
    args = ap.parse_args()

    py = sys.executable
    dbt = str(BIN / "dbt")
    if not args.veri_uretme:
        calistir([py, "scripts/generate_nova_test_data.py"])
    calistir([py, "scripts/fetch_external.py"])
    calistir([dbt, "build", "--profiles-dir", "."], cwd=DBT_DIR)
    calistir([dbt, "docs", "generate", "--static", "--profiles-dir", "."], cwd=DBT_DIR)
    (ROOT / "docs").mkdir(exist_ok=True)
    shutil.copy(DBT_DIR / "target" / "static_index.html", ROOT / "docs" / "dbt_docs.html")
    calistir([py, "scripts/build_data_dictionary.py"])
    calistir([py, "scripts/export_marts.py"])
    print("\nTamamlandı. Dashboard: streamlit run app/dashboard.py")


if __name__ == "__main__":
    main()
