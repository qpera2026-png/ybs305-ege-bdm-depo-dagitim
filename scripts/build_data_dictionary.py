"""
Veri sözlüğünü (docs/veri_sozlugu.md) dbt manifest + catalog dosyalarından üretir.
Böylece sözlük, modellerle her zaman eşzamanlı kalır.

Ön koşul:  dbt docs generate  (dbt/target/manifest.json ve catalog.json)
Kullanım:  python scripts/build_data_dictionary.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "dbt" / "target"
OUT = ROOT / "docs" / "veri_sozlugu.md"

# Ham kaynak kolonları (CSV'ler dbt kataloğunda tip bilgisi taşımadığı için elle tanımlı)
HAM = {
    "perakende_satis": [("satis_id", "Satış satırı kimliği"), ("sepet_id", "Fiş/sepet kimliği"),
                        ("urun_id", "Ürün kimliği"), ("adet", "Adet (iadede negatif)"),
                        ("birim_fiyat", "Satış anındaki birim fiyat (₺)"), ("indirim_tutari", "Satır indirimi (₺)"),
                        ("islem_tipi", "SATIS / IADE")],
    "sepet": [("sepet_id", "Fiş kimliği"), ("musteri_id", "Sadakat kartı müşteri kimliği (boş = anonim)"),
              ("magaza_id", "Mağaza kimliği"), ("islem_zamani", "Fiş tarihi-saati"), ("odeme_tipi", "Ödeme yöntemi")],
    "musteri": [("musteri_id", "Anonim müşteri kimliği"), ("cinsiyet", "K / E / boş"), ("dogum_yili", "Doğum yılı"),
                ("il", "İkamet ili (ham, tutarsız yazımlar olabilir)"), ("ev_magaza_id", "En sık alışveriş yapılan mağaza"),
                ("sadakat_segmenti", "Standart / Gümüş / Altın"), ("kayit_tarihi", "Kart kayıt tarihi")],
    "urun": [("urun_id", "Ürün kimliği"), ("urun_adi", "Ürün adı"), ("kategori", "Ürün kategorisi"),
             ("sicaklik_tipi", "Ortam / Soğuk / Dondurulmuş"), ("birim_fiyat", "Liste fiyatı (₺, Ocak)"),
             ("birim_hacim_dm3", "Birim hacim (dm³ = litre)"), ("birim_agirlik_kg", "Birim ağırlık (kg)"),
             ("koli_ici_adet", "Bir kolideki adet")],
    "magaza": [("magaza_id", "Mağaza kimliği"), ("magaza_adi", "Mağaza adı"), ("il", "İl"), ("ilce", "İlçe"),
               ("enlem", "Enlem"), ("boylam", "Boylam"), ("magaza_tipi", "Büyük / Orta / Küçük"),
               ("satis_alani_m2", "Satış alanı (m²)"), ("acilis_tarihi", "Açılış tarihi")],
    "dagitim_merkezi": [("bdm_id", "BDM kimliği"), ("ad", "BDM adı"), ("enlem", "Enlem"), ("boylam", "Boylam")],
    "il_nufus_tuik": [("il_kodu", "Plaka kodu"), ("il_adi", "İl adı"), ("bolge", "Coğrafi bölge"),
                      ("nufus", "ADNKS nüfusu"), ("yil", "Nüfus yılı"), ("kaynak", "Kaynak")],
    "magaza_mesafe_osrm": [("bdm_id", "BDM kimliği"), ("magaza_id", "Mağaza kimliği"),
                           ("mesafe_m", "Karayolu mesafesi (m)"), ("sure_sn", "Sürüş süresi (sn)"),
                           ("kaynak", "OSRM API / yedek hesap"), ("cekilme_zamani", "API çağrı zamanı (UTC)")],
}

# yml'de açıklaması olmayan kolonlar için ortak açıklamalar
ORTAK = {
    "magaza_id": "Mağaza kimliği", "urun_id": "Ürün kimliği", "sepet_id": "Fiş/sepet kimliği",
    "satis_id": "Satış satırı kimliği", "musteri_id": "Anonim müşteri kimliği (NULL = kartsız)",
    "tarih": "İşlem günü", "hafta_baslangic": "Haftanın pazartesi tarihi (ISO hafta)",
    "il": "İl adı (standart)", "ilce": "İlçe", "kategori": "Ürün kategorisi",
    "sicaklik_tipi": "Ortam / Soğuk / Dondurulmuş", "islem_tipi": "SATIS / IADE",
    "adet": "Adet", "satis_adedi": "Satış adedi (iade hariç)", "birim_fiyat": "Satış birim fiyatı (₺)",
    "indirim_tutari": "İndirim tutarı (₺)", "brut_tutar": "Adet × birim fiyat (₺)",
    "net_tutar": "Brüt tutar − indirim (₺)", "net_ciro": "Net satış tutarı, iade hariç (₺)",
    "iade_tutari": "İade edilen tutar (₺, pozitif)", "hacim_dm3": "Satılan hacim (dm³)",
    "hacim_m3": "Satılan hacim (m³, örneklem)", "agirlik_kg": "Satılan ağırlık (kg)",
    "koli_esdegeri": "Adet / koli içi adet", "enlem": "Enlem", "boylam": "Boylam",
    "magaza_adi": "Mağaza adı", "magaza_tipi": "Büyük / Orta / Küçük", "urun_adi": "Ürün adı",
    "rota_kumesi": "BDM'ye göre yön kümesi (Kuzey/Doğu/Güney/Batı)", "mesafe_km": "BDM'den karayolu mesafesi (km)",
    "surus_suresi_dk": "BDM'den sürüş süresi (dk)", "sepet_sayisi": "Fiş sayısı",
    "kartli_sepet_sayisi": "Sadakat kartlı fiş sayısı", "nufus": "TÜİK ADNKS nüfusu",
    "il_nufusu": "Mağazanın bulunduğu ilin nüfusu", "il_kodu": "Plaka kodu",
    "tam_hafta_mi": "Hafta veri döneminin tamamen içinde mi", "gun_sayisi": "Haftadaki satış günü sayısı",
    "tahmini_toplam_hacim_m3": "Örneklem hacmi × talep_olcek_katsayisi (m³)",
    "tahmini_toplam_agirlik_kg": "Örneklem ağırlığı × talep_olcek_katsayisi (kg)",
    "toplam_adet": "Yıllık satış adedi", "toplam_ciro": "Yıllık net ciro (₺)", "toplam_hacim_m3": "Yıllık hacim (m³)",
    "satilan_magaza_sayisi": "Ürünün satıldığı mağaza sayısı", "haftalik_ort_adet": "Haftalık ortalama satış adedi",
    "toplama_payi": "Ürünün toplam toplama satırları içindeki payı", "hiz_sirasi": "Toplama sıklığına göre sıra (1 = en hızlı)",
    "abc_xyz": "Birleşik sınıf (örn. AX)", "onerilen_raf_seviyesi": "Önerilen raf seviyesi",
    "yerlesim_onceligi": "Yerleşim önceliği (1 = rampaya en yakın)", "yerlesim_gerekcesi": "Öneri gerekçesi",
    "ort_haftalik_hacim_m3": "Tam haftalarda ortalama haftalık hacim (m³, ölçekli)",
    "p90_haftalik_hacim_m3": "Haftalık hacmin %90'lık dilimi (m³, ölçekli)",
    "ort_haftalik_agirlik_kg": "Ortalama haftalık ağırlık (kg, ölçekli)", "talep_cv": "Haftalık hacmin varyasyon katsayısı",
    "onerilen_arac_tipi": "Önerilen araç tipi", "haftalik_sevkiyat_sayisi": "Önerilen haftalık sefer sayısı",
    "onerilen_sevkiyat_gunleri": "Önerilen sevkiyat günleri", "arac_hacim_kapasite_m3": "Araç hacim kapasitesi (m³)",
    "arac_agirlik_kapasite_kg": "Araç ağırlık kapasitesi (kg)", "sefer_basi_p90_hacim_m3": "P90 hacmin sefer başına düşen kısmı",
    "ort_hacim_doluluk_orani": "Ortalama hacim doluluğu", "ort_agirlik_doluluk_orani": "Ortalama ağırlık doluluğu",
    "sefer_maliyeti_tl": "Bir sefer maliyeti: sabit + 2 × mesafe × km maliyeti (₺)",
    "haftalik_tasima_maliyeti_tl": "Haftalık toplam taşıma maliyeti (₺)", "haftalik_km": "Haftalık toplam km",
    "m3_basi_tasima_maliyeti_tl": "m³ başına taşıma maliyeti (₺)", "magaza_sayisi": "Mağaza sayısı",
    "magaza_basina_nufus": "İl nüfusu / mağaza sayısı", "on_bin_kisi_basina_ciro": "10.000 kişi başına net ciro (₺, örneklem)",
    "ort_bdm_mesafesi_km": "İldeki mağazaların ortalama BDM mesafesi (km)", "yon_derece": "BDM'den pusula açısı (0 = Kuzey)",
    "abc_sinifi": "A / B / C (toplama sıklığı)", "xyz_sinifi": "X / Y / Z (talep düzenliliği)",
    "aciklama": "Kural açıklaması", "depo_bolgesi": "Depo bölgesi", "raf_seviyesi": "Raf seviyesi",
    "oncelik": "Yerleşim önceliği", "onerilen_depo_bolgesi": "Önerilen depo bölgesi (sıcaklık bölgesi dahil)",
    "acilis_tarihi": "Mağaza açılış tarihi", "satis_alani_m2": "Satış alanı (m²)",
    "arac_tipi": "Araç tipi", "hacim_kapasite_m3": "Hacim kapasitesi (m³)", "agirlik_kapasite_kg": "Ağırlık kapasitesi (kg)",
    "sefer_sabit_maliyet_tl": "Sefer başına sabit maliyet: şoför, yükleme (₺)", "km_maliyet_tl": "km başına değişken maliyet (₺)",
    "kucuk_magazaya_uygun": "Küçük (şehir içi) mağazaya girebilir mi",
    "ay": "Ay (1-12)", "ay_adi": "Ay adı", "yil": "Yıl", "ceyrek": "Çeyrek", "haftanin_gunu": "ISO gün (1 = Pzt)",
    "gun_adi": "Gün adı", "hafta_sonu_mu": "Cumartesi/Pazar mı", "sezon": "Yaz Sezonu (Haz-Eyl) / Normal Sezon",
    "bdm_id": "Bölgesel dağıtım merkezi kimliği", "bdm_adi": "BDM adı", "bolge": "Coğrafi bölge",
    "il_adi": "İl adı", "nufus_yili": "Nüfus verisinin yılı", "kaynak": "Veri kaynağı",
    "mesafe_kaynagi": "Mesafe kaynağı (OSRM API / yedek)", "cekilme_zamani": "API çağrı zamanı (UTC)",
    "birim_hacim_dm3": "Birim hacim (dm³)", "birim_agirlik_kg": "Birim ağırlık (kg)", "koli_ici_adet": "Koli içi adet",
    "koli_hacim_dm3": "Koli hacmi (dm³)", "koli_agirlik_kg": "Koli ağırlığı (kg)", "liste_fiyati": "Liste fiyatı (₺)",
    "cinsiyet": "Kadın / Erkek / Belirtilmemiş", "dogum_yili": "Doğum yılı", "yas_grubu": "Yaş grubu (2025'e göre)",
    "ev_magaza_id": "Müşterinin ana mağazası", "sadakat_segmenti": "Standart / Gümüş / Altın",
    "kayit_tarihi": "Sadakat kartı kayıt tarihi", "islem_zamani": "Fiş tarihi-saati", "odeme_tipi": "Ödeme yöntemi",
    "sadakat_karti_var_mi": "Fişte sadakat kartı kullanıldı mı",
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads((TARGET / "manifest.json").read_text(encoding="utf-8"))
    catalog = json.loads((TARGET / "catalog.json").read_text(encoding="utf-8"))

    satirlar = ["# Veri Sözlüğü", "",
                "_Bu dosya `scripts/build_data_dictionary.py` ile dbt manifest/catalog'dan otomatik üretilir._", "",
                "## 1. Ham ve dış kaynaklar", ""]
    for kaynak in sorted(manifest["sources"].values(), key=lambda s: (s["source_name"], s["name"])):
        satirlar += [f"### `{kaynak['source_name']}.{kaynak['name']}`", "", kaynak["description"].strip(), "",
                     "| Kolon | Açıklama |", "|---|---|"]
        satirlar += [f"| `{k}` | {a} |" for k, a in HAM.get(kaynak["name"], [])]
        satirlar.append("")

    katman_adi = {"staging": "2. Staging katmanı", "intermediate": "3. Intermediate katmanı", "marts": "4. Mart katmanı"}
    modeller = [n for n in manifest["nodes"].values() if n["resource_type"] in ("model", "seed")]
    for katman, baslik in [("staging", katman_adi["staging"]), ("intermediate", katman_adi["intermediate"]),
                           ("marts", katman_adi["marts"]), ("referans", "5. Referans (seed) tabloları")]:
        satirlar += [f"## {baslik}", ""]
        for n in sorted([m for m in modeller if m["schema"] == katman], key=lambda m: m["name"]):
            kat = catalog["nodes"].get(n["unique_id"], {}).get("columns", {})
            satirlar += [f"### `{katman}.{n['name']}`", "", (n.get("description") or "").strip(), "",
                         "| Kolon | Tip | Açıklama |", "|---|---|---|"]
            for kolon in sorted(kat.values(), key=lambda c: c["index"]):
                aciklama = n["columns"].get(kolon["name"], {}).get("description", "") or ORTAK.get(kolon["name"], "")
                satirlar.append(f"| `{kolon['name']}` | {kolon['type']} | {aciklama} |")
            satirlar.append("")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(satirlar), encoding="utf-8")
    print(f"Veri sözlüğü yazıldı: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
