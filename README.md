# Bölgesel Dağıtım Merkezinde Talep Odaklı Depo Yerleşimi ve Mağaza Dağıtım Planlaması

**YBS305 – İş Zekâsı ve Veri Madenciliği · Dönem Projesi · Bölüm 1 (Veri + dbt ETL + Dashboard)**

> ⚠️ **Not:** NovaPerakende veri seti henüz paylaşılmadığı için proje şu an aynı omurgaya
> (`perakende_satis`, `sepet`, `musteri`) sahip **sentetik test verisiyle** çalışmaktadır.
> Gerçek veri geldiğinde yalnızca `data/raw/` değiştirilir (bkz. [Gerçek veriye geçiş](#gerçek-veriye-geçiş)).

## 1. İş problemi

NovaPerakende'nin Ege Bölgesi'ndeki 30 mağazası, İzmir Kemalpaşa'daki **Ege Bölgesel Dağıtım
Merkezi (BDM)** tarafından besleniyor. İki karar sorusu:

1. **Depo yerleşimi (slotting):** BDM'de hangi ürün hangi bölgeye / raf seviyesine konmalı ki
   toplama (picking) yolu ve süresi azalsın?
2. **Mağaza dağıtım planlaması:** Her mağazaya hangi araç tipiyle, haftada kaç kez sevkiyat
   yapılmalı ki talep karşılansın ve taşıma maliyeti en aza insin?

Her iki karar da **mağaza satış talebinden** türetilir (talep odaklı yaklaşım).

## 2. Mimari

```
 NovaPerakende CSV (test)   TÜİK ADNKS il nüfusu   OSRM rota API'si
          │                        │                      │
          └──────────── data/raw ──┴── data/external ─────┘
                                   │
                         dbt + DuckDB (nova.duckdb)
            staging (8 view) → intermediate (2 view) → marts (11 tablo)
                     │   76 veri testi · dbt docs
                                   │
                    scripts/export_marts.py → data/marts/*.parquet
                                   │
                       Streamlit dashboard (app/dashboard.py)
```

| Aşama | Araç | Gerekçe |
|---|---|---|
| Veri toplama | Python (`numpy`, `pandas`, `requests`) | Test verisi üretimi + OSRM API çağrısı |
| Depo | DuckDB | Kurulumsuz, yerel, hızlı analitik veritabanı (el kitabı önerisi) |
| ETL | dbt Core + dbt-duckdb | Katmanlı modeller, test ve dokümantasyon |
| Görselleştirme | **Streamlit + Plotly** | Power BI yerine seçildi: (1) harita, Pareto ve ABC-XYZ matrisi gibi lojistiğe özel görseller kodla tam kontrol edilir, (2) aynı uygulama Bölüm 2'de model arayüzüyle birleştirilip Streamlit Community Cloud'a tek ürün olarak yayınlanacak, (3) macOS/Linux'ta da çalışır ve sürüm kontrolüne uygun (`.pbix` ikili dosyası yerine kod). |

## 3. Veri kaynakları

| Kaynak | Tür | İçerik | Kullanım |
|---|---|---|---|
| **NovaPerakende** (`data/raw/`) | Sağlanan veri seti (şimdilik test verisi) | 1,34 M satış satırı, 347 B sepet, 9 B müşteri, 300 ürün, 30 mağaza (2025) | Talep, ürün hızı, hacim/ağırlık |
| **TÜİK ADNKS 2023** (`data/external/il_nufus_tuik.csv`) | Açık veri | Ege'deki 8 ilin nüfusu | Mağaza dağılımı, 10.000 kişi başına talep yoğunluğu |
| **OSRM Table API** (`scripts/fetch_external.py`) | Açık API (OpenStreetMap) | BDM → 30 mağaza karayolu mesafe ve süresi | Sefer maliyeti, rota kümesi |

**Test verisinin özellikleri** (`scripts/generate_nova_test_data.py`, `seed=42`):
mağaza sayısı il nüfusuyla orantılı; Zipf dağılımlı ürün popülerliği (Pareto etkisi); yaz sezonu
(İçecek, Dondurulmuş) ve turistik ilçe (Bodrum, Çeşme, Kuşadası…) etkisi; kampanya haftaları;
aylık ~%2,5 fiyat artışı. Staging katmanının temizlik işini göstermek için **bilinçli kirli veri**
eklenmiştir: %0,3 çift kayıt, %1 iade satırı (negatif adet), tutarsız il adları (`"İZMIR"`,
`"izmir  "`), boş müşteri kimliği / cinsiyet / doğum yılı.

## 4. Kurulum ve çalıştırma

Gereksinim: Python 3.11+

```bash
git clone <repo-url> && cd YBS305_proje
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python scripts/run_pipeline.py      # veri üret → OSRM → dbt build → dbt docs → parquet
streamlit run app/dashboard.py      # http://localhost:8501
```

Adım adım çalıştırmak isterseniz:

```bash
python scripts/generate_nova_test_data.py
python scripts/fetch_external.py
cd dbt
dbt build --profiles-dir .          # seed + run + test
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .
cd ..
python scripts/export_marts.py
```

dbt dokümantasyonunun statik kopyası: [`docs/dbt_docs.html`](docs/dbt_docs.html) (tarayıcıda açın).

## 5. dbt projesi

```
dbt/
├── dbt_project.yml        # değişkenler: ölçek katsayısı, hedef doluluk, ABC/XYZ sınırları
├── profiles.yml           # DuckDB bağlantısı (nova.duckdb)
├── seeds/                 # arac_tipleri, depo_yerlesim_kurallari (iş kuralları)
├── macros/                # il_anahtari, özel testler (pozitif_deger, benzersiz_kombinasyon)
├── tests/                 # 5 tekil (singular) iş kuralı testi
└── models/
    ├── staging/           # stg_nova__* , stg_dis__*  (temizlik, tip dönüşümü)
    ├── intermediate/      # int_satis_satirlari, int_magaza_ikmal_siparisleri
    └── marts/             # dim_*, fct_satis, mart_*
```

### Modeller

| Katman | Model | Açıklama |
|---|---|---|
| staging | `stg_nova__satis` | Tip dönüşümü, **çift kayıt ayıklama** (`qualify row_number()`), brüt/net tutar |
| staging | `stg_nova__musteri` | **İl adı standardizasyonu** (TÜİK listesine eşleme), yaş grubu, boş değer temizliği |
| staging | `stg_nova__sepet`, `_urun`, `_magaza`, `_dagitim_merkezi` | Tip dönüşümü, boş string → NULL |
| staging | `stg_dis__il_nufus`, `stg_dis__magaza_mesafe` | Dış kaynaklar (m → km, sn → dk) |
| intermediate | `int_satis_satirlari` | Satır + sepet + ürün lojistik özellikleri (hacim, ağırlık, koli) |
| intermediate | `int_magaza_ikmal_siparisleri` | **Koli bazlı ikmal** varsayımıyla BDM toplama satırları |
| marts | `dim_tarih`, `dim_urun`, `dim_magaza`, `dim_dagitim_merkezi`, `fct_satis` | Yıldız şema |
| marts | **`mart_urun_abc_xyz`** | ABC (toplama sıklığı) × XYZ (talep düzenliliği), COI, **depo bölgesi önerisi** |
| marts | `mart_magaza_haftalik_talep` | Mağaza × hafta hacim/ağırlık/koli profili |
| marts | **`mart_dagitim_plani`** | Mağaza başına **araç tipi + haftalık sefer sayısı + sevkiyat günleri + maliyet** |
| marts | `mart_il_talep_ozeti` | İl bazında 10.000 kişi başına ciro (TÜİK ile) |
| marts | `mart_gunluk_kategori_satis`, `mart_gunluk_magaza_ozet` | Dashboard filtreleri için özetler |

### Testler (76 adet, hepsi geçiyor)

- **Generic:** `unique`, `not_null`, `relationships`, `accepted_values`
- **Özel generic (macro):** `pozitif_deger`, `benzersiz_kombinasyon`
- **Singular (iş kuralı):**
  - `assert_iade_haric_satis_adedi_pozitif`: SATIS > 0, IADE < 0
  - `assert_abc_pareto_tutarli`: A sınıfı ≥ %70 pay ve A→B→C sıralaması tutarlı
  - `assert_sevkiyat_kapasitesi_yeterli`: plan P90 talebi kapasiteyle karşılıyor
  - `assert_mesafe_makul`: 0 < mesafe ≤ 600 km
  - `assert_satis_toplami_korunuyor`: dönüşümde ciro kaybı yok

## 6. Yöntem

**ABC (hız):** Mağazaların BDM'den koli bazında ikmal yaptığı varsayılır. Mağazadaki kümülatif satış
yeni bir koli eşiğini geçtiği gün BDM'de bir **toplama satırı** oluşur. Ürünler toplama satırı
sayısına göre sıralanır: kümülatif %80 → **A**, %95 → **B**, kalan → **C**.

**XYZ (düzenlilik):** Tam haftalardaki haftalık satış adedinin varyasyon katsayısı
(CV = σ/μ): ≤0,5 → **X**, ≤1,0 → **Y**, >1,0 → **Z**.

**Yerleşim kuralı** (`seeds/depo_yerlesim_kurallari.csv`): AX/AY → *Altın Bölge* (rampaya
yakın, bel hizası); AZ → *Ön Bölge (esnek)*; B → *Orta Bölge*; C → *Arka Bölge / üst raf*.
Soğuk ve dondurulmuş ürünler kendi sıcaklık bölgelerinde aynı mantıkla yerleşir.
**COI** (Cube-per-Order Index = haftalık raf hacmi / haftalık toplama) bölge içi sıralama içindir.

**Dağıtım planı:** Her mağaza için haftalık talebin **P90** değeri (hacim ve ağırlık), araç
kapasitesinin %85'ini aşmayacak şekilde karşılanır. Her araç tipi için gereken sefer sayısı
hesaplanır ve en düşük haftalık maliyetli seçenek seçilir. Maliyet = sefer sayısı × (sabit sefer
maliyeti + 2 × mesafe × km maliyeti). Haftada en az 2 sevkiyat yapılır (tazelik); tır küçük
mağazalara atanmaz. Mağazalar BDM'ye göre yönlerine (pusula açısı) göre 4 **rota kümesine**
ayrılır.

> Veri, mağaza işlemlerinin örneklemi olarak kabul edilir. Dağıtım hacimleri
> `var('talep_olcek_katsayisi') = 20` ile toplam talebe ölçeklenir.

## 7. Dashboard

`streamlit run app/dashboard.py`

| Gereksinim | Karşılık |
|---|---|
| **≥3 KPI** | Net ciro, sepet sayısı, ort. sepet tutarı, haftalık sevk hacmi, haftalık taşıma maliyeti, A sınıfı ürün sayısı ve toplama payı, ort. BDM mesafesi, haftalık sefer, ort. araç doluluğu |
| **≥3 görsel** | Haftalık talep (kategori kırılımı), il talep yoğunluğu, gün dağılımı, Pareto eğrisi, ABC-XYZ ısı matrisi, depo bölgesi akış hacmi, mağaza/rota haritası, mağaza maliyet grafiği, araç tipi dağılımı, mağaza talep profili + P90 |
| **≥1 filtre** | Tarih aralığı, il, rota kümesi, kategori, ABC sınıfı, mağaza seçici |

Sekmeler: **Talep · Depo Yerleşimi · Mağaza Dağıtımı · Veri ve Yöntem**

## 8. Test verisinden ilk bulgular

*(Bunlar sentetik veriden çıktığı için sadece yöntemin çalıştığını gösterir.)*

- 300 ürünün **90'ı (%30) toplama satırlarının %80'ini** oluşturuyor. Bu ürünler Altın Bölge'ye
  alınırsa toplayıcıların yürüme mesafesi kısalır.
- Z sınıfı (düzensiz) ürünler dondurma, güneş kremi ve kampanyalı içecekler. Bunlar için sabit göz
  yerine **esnek / mevsimsel yerleşim** öneriliyor.
- Tüm mağazalarda **bağlayıcı kısıt ağırlık** (içecek ve temel gıda ağır). Planlama hacme göre değil
  ağırlığa göre yapılmalı.
- Önerilen plan haftada **82 sefer** (24 mağazaya tır, 6 küçük mağazaya 12 t kamyon) ve yaklaşık
  **₺886 B/hafta** taşıma maliyeti öngörüyor.

## 9. Varsayımlar ve sınırlılıklar

- Seferler doğrudan, yani BDM → mağaza → BDM (çok duraklı rota optimizasyonu/VRP yok). Rota
  kümeleri, birleştirme fırsatlarını göstermek için var.
- Araç maliyetleri ve kapasiteleri yaklaşık piyasa değerleridir (`seeds/arac_tipleri.csv`).
- Mağaza koordinatları ilçe merkezlerine yakındır.
- TÜİK verisi 2023 yılına aittir (8 il için tutarlı son yıl).

## 10. Gerçek veriye geçiş

1. NovaPerakende CSV'lerini `data/raw/` altına aynı adlarla koyun.
2. Kolon adları farklıysa yalnızca `dbt/models/staging/stg_nova__*.sql` dosyalarını güncelleyin.
   Üst katmanlar staging kolonlarına bağlıdır.
3. Ürün hacim/ağırlık veya mağaza koordinatı yoksa ek bir ana veri dosyası gerekir. Gerekirse
   eğitmen onayıyla tahmini değer kullanılır.
4. `python scripts/run_pipeline.py --veri-uretme`

## 11. Etik ve KVKK

Müşteri verisinde ad, telefon veya adres yoktur. Yalnızca anonim kimlik, cinsiyet, doğum yılı ve
il bulunur. Analizler mağaza/ürün düzeyinde toplulaştırılmıştır, kişi düzeyinde çıktı üretilmez.

## 12. Ekip

| Üye | Sorumluluk |
|---|---|
| _Ad Soyad_ | Veri toplama, dış kaynaklar |
| _Ad Soyad_ | dbt modelleri ve testler |
| _Ad Soyad_ | Dashboard |

## Kaynaklar

- TÜİK, Adrese Dayalı Nüfus Kayıt Sistemi Sonuçları 2023: https://data.tuik.gov.tr
- OSRM, Open Source Routing Machine: https://project-osrm.org (veri © OpenStreetMap katkıcıları)
- dbt-duckdb: https://github.com/duckdb/dbt-duckdb
- Frazelle, E. (2002). *World-Class Warehousing and Material Handling* (ABC slotting, COI)
