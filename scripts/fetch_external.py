"""
Dış kaynak: OSRM (Open Source Routing Machine) açık API'si ile
Bölgesel Dağıtım Merkezi -> mağaza karayolu mesafe ve sürelerini çeker.

API: https://router.project-osrm.org/table/v1/driving/{koordinatlar}
     (OpenStreetMap verisi, ücretsiz demo sunucusu)

API'ye ulaşılamazsa haversine mesafesi x 1.3 (karayolu dolambaç katsayısı)
yedek değer olarak yazılır ve `kaynak` kolonunda belirtilir.

Kullanım:  python scripts/fetch_external.py
Çıktı:     data/external/magaza_mesafe_osrm.csv
"""
import math
from datetime import datetime, timezone
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXT = ROOT / "data" / "external"
OSRM_URL = "https://router.project-osrm.org/table/v1/driving/{coords}"


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def osrm_tablo(bdm, magazalar):
    noktalar = [(bdm.boylam, bdm.enlem)] + list(zip(magazalar.boylam, magazalar.enlem))
    coords = ";".join(f"{lon:.5f},{lat:.5f}" for lon, lat in noktalar)
    r = requests.get(
        OSRM_URL.format(coords=coords),
        params={"sources": "0", "annotations": "distance,duration"},
        headers={"User-Agent": "YBS305-ders-projesi"},
        timeout=30,
    )
    r.raise_for_status()
    js = r.json()
    if js.get("code") != "Ok":
        raise RuntimeError(js)
    return js["distances"][0][1:], js["durations"][0][1:]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bdm = pd.read_csv(RAW / "dagitim_merkezi.csv").iloc[0]
    magazalar = pd.read_csv(RAW / "magaza.csv")
    zaman = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        mesafe_m, sure_s = osrm_tablo(bdm, magazalar)
        kaynak = "OSRM API"
        print("OSRM API'den mesafeler alındı.")
    except Exception as e:  # ağ yoksa yedek hesap
        print(f"OSRM'e ulaşılamadı ({e}); haversine yedeği kullanılıyor.")
        km = [haversine_km(bdm.enlem, bdm.boylam, a, b) * 1.3 for a, b in zip(magazalar.enlem, magazalar.boylam)]
        mesafe_m = [k * 1000 for k in km]
        sure_s = [k / 60 * 3600 for k in km]  # ortalama 60 km/sa
        kaynak = "Haversine x1.3 (yedek)"

    cikti = pd.DataFrame({
        "bdm_id": bdm.bdm_id,
        "magaza_id": magazalar.magaza_id,
        "mesafe_m": [round(x, 1) for x in mesafe_m],
        "sure_sn": [round(x, 1) for x in sure_s],
        "kaynak": kaynak,
        "cekilme_zamani": zaman,
    })
    EXT.mkdir(parents=True, exist_ok=True)
    cikti.to_csv(EXT / "magaza_mesafe_osrm.csv", index=False)
    print(cikti.head())


if __name__ == "__main__":
    main()
