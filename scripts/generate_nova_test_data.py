"""
NovaPerakende TEST verisi üreticisi.

Gerçek NovaPerakende veri seti henüz paylaşılmadığı için, aynı omurgayı
(perakende_satis, musteri, sepet) taklit eden sentetik bir veri seti üretir.
Ege Bölgesi'ndeki mağazaların talebi TÜİK il nüfuslarıyla orantılıdır
(data/external/il_nufus_tuik.csv).

Gerçek veri geldiğinde data/raw/ altındaki CSV'ler değiştirilir; dbt staging
katmanı kolon eşlemesini üstlenir.

Kullanım:  python scripts/generate_nova_test_data.py [--seed 42]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXT = ROOT / "data" / "external"

BASLANGIC = "2025-01-01"
BITIS = "2025-12-31"

# Bölgesel Dağıtım Merkezi (BDM): Kemalpaşa OSB, İzmir
BDM = {"bdm_id": "BDM-EGE", "ad": "Ege Bölgesel Dağıtım Merkezi (Kemalpaşa)", "enlem": 38.4270, "boylam": 27.4170}

# İlçe merkezleri (yaklaşık koordinatlar). Her ildeki mağaza sayısı nüfusla orantılı seçilir.
ILCELER = {
    "İzmir": [("Konak", 38.4189, 27.1287), ("Bornova", 38.4697, 27.2211), ("Karşıyaka", 38.4594, 27.1150),
              ("Buca", 38.3886, 27.1750), ("Bayraklı", 38.4622, 27.1667), ("Çiğli", 38.4950, 27.0700),
              ("Gaziemir", 38.3200, 27.1300), ("Torbalı", 38.1556, 27.3631), ("Menemen", 38.6075, 27.0697),
              ("Ödemiş", 38.2297, 27.9708), ("Bergama", 39.1214, 27.1799), ("Çeşme", 38.3236, 26.3031),
              ("Tire", 38.0897, 27.7350)],
    "Manisa": [("Şehzadeler", 38.6191, 27.4289), ("Akhisar", 38.9186, 27.8400), ("Turgutlu", 38.4950, 27.7000),
               ("Salihli", 38.4828, 28.1389), ("Soma", 39.1856, 27.6097)],
    "Aydın": [("Efeler", 37.8444, 27.8458), ("Nazilli", 37.9125, 28.3206), ("Kuşadası", 37.8579, 27.2610),
              ("Söke", 37.7486, 27.4067), ("Didim", 37.3756, 27.2675)],
    "Muğla": [("Bodrum", 37.0383, 27.4292), ("Menteşe", 37.2153, 28.3636), ("Fethiye", 36.6217, 29.1164),
              ("Marmaris", 36.8550, 28.2742), ("Milas", 37.3164, 27.7839)],
    "Denizli": [("Merkezefendi", 37.7765, 29.0864), ("Pamukkale", 37.8100, 29.1100), ("Çivril", 38.3014, 29.7386)],
    "Afyonkarahisar": [("Merkez", 38.7569, 30.5433), ("Sandıklı", 38.4647, 30.2683), ("Dinar", 38.0650, 30.1656)],
    "Kütahya": [("Merkez", 39.4167, 29.9833), ("Tavşanlı", 39.5428, 29.4936)],
    "Uşak": [("Merkez", 38.6823, 29.4082), ("Banaz", 38.7372, 29.7517)],
}
TURISTIK_ILCELER = {"Çeşme", "Kuşadası", "Didim", "Bodrum", "Fethiye", "Marmaris"}

# kategori: (sku_sayisi, sicaklik, fiyat_aralik, hacim_dm3_aralik, kg_per_dm3, koli_ici, yaz_etkisi, temel_urunler)
KATEGORILER = {
    "Temel Gıda": (60, "Ortam", (20, 150), (0.5, 2.5), 0.8, 12, 0.00,
                   ["Makarna 500g", "Pirinç 1kg", "Bulgur 1kg", "Un 2kg", "Şeker 1kg", "Ayçiçek Yağı 1L", "Mercimek 1kg",
                    "Salça 830g", "Nohut 1kg", "Zeytinyağı 1L", "Tuz 750g", "Çay 1kg"]),
    "Süt ve Kahvaltılık": (40, "Soğuk", (25, 200), (0.3, 1.5), 1.0, 12, 0.05,
                           ["Süt 1L", "Yoğurt 1kg", "Beyaz Peynir 500g", "Kaşar 400g", "Tereyağı 250g", "Yumurta 15'li",
                            "Ayran 1L", "Zeytin 500g"]),
    "İçecek": (40, "Ortam", (10, 80), (0.5, 6.0), 1.0, 12, 0.35,
               ["Su 5L", "Su 0.5L 6'lı", "Kola 2.5L", "Meyve Suyu 1L", "Maden Suyu 6'lı", "Gazoz 1L", "Soğuk Çay 1L",
                "Enerji İçeceği"]),
    "Atıştırmalık": (45, "Ortam", (10, 60), (0.2, 1.0), 0.4, 24, 0.05,
                     ["Cips", "Çikolata", "Bisküvi", "Kraker", "Gofret", "Kuruyemiş 200g", "Kek"]),
    "Temizlik": (35, "Ortam", (40, 250), (1.0, 6.0), 0.9, 6, 0.00,
                 ["Çamaşır Deterjanı 4kg", "Bulaşık Deterjanı 1L", "Yüzey Temizleyici", "Çamaşır Suyu 2L",
                  "Tuvalet Kağıdı 16'lı", "Kağıt Havlu 6'lı", "Yumuşatıcı 3L"]),
    "Kişisel Bakım": (35, "Ortam", (30, 200), (0.2, 1.0), 0.7, 12, 0.05,
                      ["Şampuan", "Diş Macunu", "Duş Jeli", "Deodorant", "Sabun 4'lü", "Güneş Kremi", "Islak Mendil"]),
    "Dondurulmuş": (25, "Dondurulmuş", (40, 180), (0.5, 2.5), 0.6, 8, 0.50,
                    ["Dondurma 1L", "Donuk Pizza", "Donuk Sebze 1kg", "Donuk Patates 1kg", "Mantı 1kg"]),
    "Ev ve Yaşam": (20, "Ortam", (50, 400), (2.0, 15.0), 0.3, 4, 0.00,
                    ["Saklama Kabı Seti", "Çöp Poşeti", "Alüminyum Folyo", "Pil 4'lü", "Ampul", "Mutfak Bezi"]),
}
MARKALAR = ["Nova", "Ege", "Anadolu", "Lezzet", "Doğa", "Kardelen", "Yıldız", "Mavi"]


def il_nufus() -> pd.DataFrame:
    return pd.read_csv(EXT / "il_nufus_tuik.csv")


def uret_magazalar(rng, nufus: pd.DataFrame, toplam=30) -> pd.DataFrame:
    pay = nufus.set_index("il_adi")["nufus"]
    pay = pay / pay.sum()
    adet = np.maximum(1, np.floor(pay * toplam)).astype(int)
    # kalan mağazaları en büyük kesirli paya göre dağıt (largest remainder)
    kalan = toplam - adet.sum()
    for il in (pay * toplam - np.floor(pay * toplam)).sort_values(ascending=False).index[:max(kalan, 0)]:
        adet[il] += 1

    satirlar, no = [], 1
    for il, n in adet.items():
        for ilce, lat, lon in ILCELER[il][:n]:
            # ilk mağaza il merkezinde büyük olsun; diğerleri karışık
            tip = rng.choice(["Büyük", "Orta", "Küçük"], p=[0.3, 0.45, 0.25])
            if il == "İzmir" and ilce in ("Bornova", "Karşıyaka", "Buca"):
                tip = "Büyük"
            m2 = {"Büyük": rng.integers(1800, 3200), "Orta": rng.integers(800, 1600), "Küçük": rng.integers(300, 700)}[tip]
            satirlar.append({
                "magaza_id": f"MGZ{no:02d}",
                "magaza_adi": f"Nova {il} Merkez" if ilce == "Merkez" else f"Nova {ilce}",
                "il": il, "ilce": ilce,
                "enlem": round(lat + rng.normal(0, 0.004), 5),
                "boylam": round(lon + rng.normal(0, 0.004), 5),
                "magaza_tipi": tip, "satis_alani_m2": int(m2),
                "acilis_tarihi": str(pd.Timestamp("2012-01-01") + pd.Timedelta(days=int(rng.integers(0, 4000))))[:10],
            })
            no += 1
    return pd.DataFrame(satirlar)


def uret_urunler(rng) -> pd.DataFrame:
    satirlar, no = [], 1
    for kat, (n, sic, (fmin, fmax), (hmin, hmax), yogunluk, koli, _, temeller) in KATEGORILER.items():
        for i in range(n):
            temel = temeller[i % len(temeller)]
            marka = MARKALAR[(i // len(temeller) + no) % len(MARKALAR)]
            hacim = round(float(rng.uniform(hmin, hmax)), 2)
            satirlar.append({
                "urun_id": f"U{no:04d}",
                "urun_adi": f"{marka} {temel}",
                "kategori": kat,
                "sicaklik_tipi": sic,
                "birim_fiyat": round(float(rng.uniform(fmin, fmax)), 2),
                "birim_hacim_dm3": hacim,
                "birim_agirlik_kg": round(hacim * yogunluk * float(rng.uniform(0.8, 1.2)), 3),
                "koli_ici_adet": int(koli),
            })
            no += 1
    return pd.DataFrame(satirlar)


def uret_musteriler(rng, magazalar: pd.DataFrame, n=9000) -> pd.DataFrame:
    agirlik = magazalar["magaza_tipi"].map({"Büyük": 3, "Orta": 2, "Küçük": 1}).to_numpy(float)
    ev_magaza = rng.choice(magazalar.index, size=n, p=agirlik / agirlik.sum())
    il = magazalar.loc[ev_magaza, "il"].to_numpy().astype(object)
    # Kirli veri: il adlarında büyük/küçük harf ve boşluk tutarsızlıkları
    kirli = rng.random(n)
    il = np.where(kirli < 0.05, np.char.upper(il.astype(str)), il)
    il = np.where((kirli >= 0.05) & (kirli < 0.08), np.char.add(np.char.lower(il.astype(str)), "  "), il)
    dogum = rng.integers(1950, 2007, size=n).astype(float)
    dogum[rng.random(n) < 0.04] = np.nan
    cinsiyet = rng.choice(["K", "E", ""], size=n, p=[0.52, 0.45, 0.03])
    kayit = pd.Timestamp("2018-01-01") + pd.to_timedelta(rng.integers(0, 2900, size=n), unit="D")
    return pd.DataFrame({
        "musteri_id": [f"M{i:05d}" for i in range(1, n + 1)],
        "cinsiyet": cinsiyet,
        "dogum_yili": pd.array(dogum, dtype="Int64"),
        "il": il,
        "ev_magaza_id": magazalar.loc[ev_magaza, "magaza_id"].to_numpy(),
        "sadakat_segmenti": rng.choice(["Standart", "Gümüş", "Altın"], size=n, p=[0.65, 0.25, 0.10]),
        "kayit_tarihi": kayit.strftime("%Y-%m-%d"),
    })


def uret_sepet_ve_satis(rng, magazalar, urunler, musteriler):
    gunler = pd.date_range(BASLANGIC, BITIS, freq="D")
    m = magazalar.reset_index(drop=True)
    temel = m["magaza_tipi"].map({"Büyük": 42, "Orta": 24, "Küçük": 12}).to_numpy(float)
    turistik = m["ilce"].isin(TURISTIK_ILCELER).to_numpy()

    gun_carpani = np.array([0.9, 0.88, 0.92, 0.95, 1.05, 1.3, 1.15])[gunler.day_of_week]
    yaz = gunler.month.isin([6, 7, 8, 9])
    trend = 1 + 0.08 * np.arange(len(gunler)) / len(gunler)
    lam = temel[:, None] * gun_carpani[None, :] * trend[None, :]
    lam = lam * np.where(turistik[:, None] & yaz[None, :], 1.6, 1.0)
    lam = lam * np.where(turistik[:, None] & gunler.month.isin([1, 2, 12])[None, :], 0.75, 1.0)
    sepet_sayisi = rng.poisson(lam)  # (magaza, gun)

    mi, gi = np.nonzero(sepet_sayisi >= 0)
    tekrar = sepet_sayisi[mi, gi]
    s_magaza = np.repeat(mi, tekrar)
    s_gun = np.repeat(gi, tekrar)
    n_sepet = len(s_magaza)
    saat = np.clip(rng.normal(15.5, 3.2, n_sepet), 8, 21.99)
    zaman = gunler[s_gun] + pd.to_timedelta((saat * 3600).astype(int), unit="s")

    # Müşteri ataması: %70 sadakat kartı (ev mağazasından), %30 anonim
    musteri_id = np.full(n_sepet, "", dtype=object)
    kartli = rng.random(n_sepet) < 0.70
    for idx, mid in enumerate(m["magaza_id"]):
        aday = musteriler.loc[musteriler["ev_magaza_id"] == mid, "musteri_id"].to_numpy()
        sec = (s_magaza == idx) & kartli
        if len(aday) and sec.any():
            musteri_id[sec] = rng.choice(aday, size=sec.sum())

    sepet = pd.DataFrame({
        "sepet_id": np.arange(1, n_sepet + 1),
        "musteri_id": musteri_id,
        "magaza_id": m["magaza_id"].to_numpy()[s_magaza],
        "islem_zamani": zaman.strftime("%Y-%m-%d %H:%M:%S"),
        "odeme_tipi": rng.choice(["Kredi Kartı", "Nakit", "Banka Kartı", "Mobil"], size=n_sepet, p=[0.48, 0.18, 0.24, 0.10]),
    })

    # --- Satış satırları -------------------------------------------------
    n_urun = len(urunler)
    kat = urunler["kategori"].to_numpy()
    yaz_etkisi = urunler["kategori"].map({k: v[6] for k, v in KATEGORILER.items()}).to_numpy()
    # Pareto benzeri popülerlik (Zipf) -> ABC sınıfları doğal olarak oluşur
    populerlik = 1 / (rng.permutation(n_urun) + 1) ** 1.1
    populerlik *= np.where(kat == "Ev ve Yaşam", 0.4, 1.0)
    # Kampanyaya yatkın ürünler -> düzensiz talep (XYZ'de Z)
    kampanyali = rng.random(n_urun) < 0.15
    hafta_no = ((gunler - gunler[0]).days // 7).to_numpy()
    n_hafta = hafta_no.max() + 1
    # Yalnızca yaz sezonunda satılan ürünler (Mayıs-Eylül) -> güçlü mevsimsellik, Z sınıfı adayı
    sadece_yaz = urunler["urun_adi"].str.contains("Dondurma|Güneş Kremi").to_numpy()
    kampanya = np.ones((n_urun, n_hafta))
    for u in np.nonzero(kampanyali)[0]:
        kampanya[u, rng.choice(n_hafta, size=4, replace=False)] = 8.0

    satir_sayisi = 1 + rng.poisson(2.8, n_sepet)
    l_sepet = np.repeat(np.arange(n_sepet), satir_sayisi)
    l_hafta = hafta_no[s_gun][l_sepet]
    l_turistik = turistik[s_magaza][l_sepet]
    l_ay = gunler.month.to_numpy()[s_gun][l_sepet]
    l_urun = np.empty(len(l_sepet), dtype=int)

    for h in range(n_hafta):
        ay = int(gunler[min(h * 7, len(gunler) - 1)].month)
        mevsim = 1 + yaz_etkisi * np.cos((ay - 7.5) / 12 * 2 * np.pi)
        mevsim = np.where(sadece_yaz, 2.0 if 5 <= ay <= 9 else 0.02, mevsim)
        for t in (False, True):
            sec = (l_hafta == h) & (l_turistik == t)
            if not sec.any():
                continue
            w = populerlik * mevsim * kampanya[:, h]
            if t and ay in (6, 7, 8, 9):
                w = w * np.where(np.isin(kat, ["İçecek", "Dondurulmuş", "Kişisel Bakım"]), 1.5, 1.0)
            l_urun[sec] = rng.choice(n_urun, size=sec.sum(), p=w / w.sum())

    adet = 1 + rng.poisson(np.where(kat[l_urun] == "İçecek", 1.0, 0.35))
    enflasyon = 1.025 ** (l_ay - 1)  # aylık ~%2.5 fiyat artışı
    birim_fiyat = np.round(urunler["birim_fiyat"].to_numpy()[l_urun] * enflasyon, 2)
    kampanyada = kampanya[l_urun, l_hafta] > 1
    indirim = np.round(np.where(kampanyada, 0.20, 0.0) * birim_fiyat * adet, 2)

    satis = pd.DataFrame({
        "satis_id": np.arange(1, len(l_sepet) + 1),
        "sepet_id": l_sepet + 1,
        "urun_id": urunler["urun_id"].to_numpy()[l_urun],
        "adet": adet,
        "birim_fiyat": birim_fiyat,
        "indirim_tutari": indirim,
        "islem_tipi": "SATIS",
    })

    # Kirli veri: ~%1 iade satırı (negatif adet), ~%0.3 tekrarlı kayıt
    iade = satis.sample(frac=0.01, random_state=1).copy()
    iade["adet"] = -iade["adet"]
    iade["indirim_tutari"] = -iade["indirim_tutari"]
    iade["islem_tipi"] = "IADE"
    iade["satis_id"] = np.arange(len(satis) + 1, len(satis) + len(iade) + 1)
    tekrar = satis.sample(frac=0.003, random_state=2)
    satis = pd.concat([satis, iade, tekrar]).sort_values(["sepet_id", "satis_id"]).reset_index(drop=True)
    return sepet, satis


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    rng = np.random.default_rng(ap.parse_args().seed)
    RAW.mkdir(parents=True, exist_ok=True)

    magazalar = uret_magazalar(rng, il_nufus())
    urunler = uret_urunler(rng)
    musteriler = uret_musteriler(rng, magazalar)
    sepet, satis = uret_sepet_ve_satis(rng, magazalar, urunler, musteriler)

    magazalar.to_csv(RAW / "magaza.csv", index=False)
    pd.DataFrame([BDM]).to_csv(RAW / "dagitim_merkezi.csv", index=False)
    urunler.to_csv(RAW / "urun.csv", index=False)
    musteriler.to_csv(RAW / "musteri.csv", index=False)
    sepet.to_csv(RAW / "sepet.csv", index=False)
    satis.to_csv(RAW / "perakende_satis.csv", index=False)
    print(f"magaza={len(magazalar)} urun={len(urunler)} musteri={len(musteriler)} "
          f"sepet={len(sepet):,} satis_satiri={len(satis):,}")


if __name__ == "__main__":
    main()
