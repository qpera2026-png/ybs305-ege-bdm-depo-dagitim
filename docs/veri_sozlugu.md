# Veri Sözlüğü

_Bu dosya `scripts/build_data_dictionary.py` ile dbt manifest/catalog'dan otomatik üretilir._

## 1. Ham ve dış kaynaklar

### `dis_kaynak.il_nufus_tuik`

TÜİK Adrese Dayalı Nüfus Kayıt Sistemi (ADNKS) 2023 il nüfusları — Ege Bölgesi.

| Kolon | Açıklama |
|---|---|
| `il_kodu` | Plaka kodu |
| `il_adi` | İl adı |
| `bolge` | Coğrafi bölge |
| `nufus` | ADNKS nüfusu |
| `yil` | Nüfus yılı |
| `kaynak` | Kaynak |

### `dis_kaynak.magaza_mesafe_osrm`

OSRM açık rota API'sinden çekilen BDM → mağaza karayolu mesafe ve süreleri.

| Kolon | Açıklama |
|---|---|
| `bdm_id` | BDM kimliği |
| `magaza_id` | Mağaza kimliği |
| `mesafe_m` | Karayolu mesafesi (m) |
| `sure_sn` | Sürüş süresi (sn) |
| `kaynak` | OSRM API / yedek hesap |
| `cekilme_zamani` | API çağrı zamanı (UTC) |

### `nova.dagitim_merkezi`

Bölgesel dağıtım merkezi (BDM) bilgisi.

| Kolon | Açıklama |
|---|---|
| `bdm_id` | BDM kimliği |
| `ad` | BDM adı |
| `enlem` | Enlem |
| `boylam` | Boylam |

### `nova.magaza`

Mağaza ana verisi (il, ilçe, koordinat, mağaza tipi).

| Kolon | Açıklama |
|---|---|
| `magaza_id` | Mağaza kimliği |
| `magaza_adi` | Mağaza adı |
| `il` | İl |
| `ilce` | İlçe |
| `enlem` | Enlem |
| `boylam` | Boylam |
| `magaza_tipi` | Büyük / Orta / Küçük |
| `satis_alani_m2` | Satış alanı (m²) |
| `acilis_tarihi` | Açılış tarihi |

### `nova.musteri`

Sadakat kartı müşterileri (anonimleştirilmiş).

| Kolon | Açıklama |
|---|---|
| `musteri_id` | Anonim müşteri kimliği |
| `cinsiyet` | K / E / boş |
| `dogum_yili` | Doğum yılı |
| `il` | İkamet ili (ham, tutarsız yazımlar olabilir) |
| `ev_magaza_id` | En sık alışveriş yapılan mağaza |
| `sadakat_segmenti` | Standart / Gümüş / Altın |
| `kayit_tarihi` | Kart kayıt tarihi |

### `nova.perakende_satis`

Satış fişi satırları (her satır bir ürün). İade satırları negatif adetlidir.

| Kolon | Açıklama |
|---|---|
| `satis_id` | Satış satırı kimliği |
| `sepet_id` | Fiş/sepet kimliği |
| `urun_id` | Ürün kimliği |
| `adet` | Adet (iadede negatif) |
| `birim_fiyat` | Satış anındaki birim fiyat (₺) |
| `indirim_tutari` | Satır indirimi (₺) |
| `islem_tipi` | SATIS / IADE |

### `nova.sepet`

Fiş/sepet başlığı (mağaza, zaman, müşteri, ödeme tipi).

| Kolon | Açıklama |
|---|---|
| `sepet_id` | Fiş kimliği |
| `musteri_id` | Sadakat kartı müşteri kimliği (boş = anonim) |
| `magaza_id` | Mağaza kimliği |
| `islem_zamani` | Fiş tarihi-saati |
| `odeme_tipi` | Ödeme yöntemi |

### `nova.urun`

Ürün ana verisi (kategori, fiyat, hacim, ağırlık, koli içi adet).

| Kolon | Açıklama |
|---|---|
| `urun_id` | Ürün kimliği |
| `urun_adi` | Ürün adı |
| `kategori` | Ürün kategorisi |
| `sicaklik_tipi` | Ortam / Soğuk / Dondurulmuş |
| `birim_fiyat` | Liste fiyatı (₺, Ocak) |
| `birim_hacim_dm3` | Birim hacim (dm³ = litre) |
| `birim_agirlik_kg` | Birim ağırlık (kg) |
| `koli_ici_adet` | Bir kolideki adet |

## 2. Staging katmanı

### `staging.stg_dis__il_nufus`

TÜİK ADNKS il nüfusları (dış kaynak).

| Kolon | Tip | Açıklama |
|---|---|---|
| `il_kodu` | INTEGER | Plaka kodu |
| `il_adi` | VARCHAR | İl adı |
| `bolge` | VARCHAR | Coğrafi bölge |
| `nufus` | BIGINT | TÜİK ADNKS nüfusu |
| `nufus_yili` | INTEGER | Nüfus verisinin yılı |
| `kaynak` | VARCHAR | Veri kaynağı |

### `staging.stg_dis__magaza_mesafe`

OSRM API'sinden BDM -> mağaza karayolu mesafesi (km) ve süresi (dk).

| Kolon | Tip | Açıklama |
|---|---|---|
| `bdm_id` | VARCHAR | Bölgesel dağıtım merkezi kimliği |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `mesafe_km` | DOUBLE | BDM'den karayolu mesafesi (km) |
| `surus_suresi_dk` | DOUBLE | BDM'den sürüş süresi (dk) |
| `mesafe_kaynagi` | VARCHAR | Mesafe kaynağı (OSRM API / yedek) |
| `cekilme_zamani` | TIMESTAMP | API çağrı zamanı (UTC) |

### `staging.stg_nova__dagitim_merkezi`

Bölgesel dağıtım merkezi.

| Kolon | Tip | Açıklama |
|---|---|---|
| `bdm_id` | VARCHAR | Bölgesel dağıtım merkezi kimliği |
| `bdm_adi` | VARCHAR | BDM adı |
| `enlem` | DOUBLE | Enlem |
| `boylam` | DOUBLE | Boylam |

### `staging.stg_nova__magaza`

Mağaza ana verisi.

| Kolon | Tip | Açıklama |
|---|---|---|
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `magaza_adi` | VARCHAR | Mağaza adı |
| `il` | VARCHAR | İl adı (standart) |
| `ilce` | VARCHAR | İlçe |
| `enlem` | DOUBLE | Enlem |
| `boylam` | DOUBLE | Boylam |
| `magaza_tipi` | VARCHAR | Büyük / Orta / Küçük |
| `satis_alani_m2` | INTEGER | Satış alanı (m²) |
| `acilis_tarihi` | DATE | Mağaza açılış tarihi |

### `staging.stg_nova__musteri`

Anonim müşteri verisi. İl adları ("  izmir", "İZMİR" gibi) TÜİK il listesine eşlenerek standartlaştırılır; doğum yılından yaş grubu türetilir.

| Kolon | Tip | Açıklama |
|---|---|---|
| `musteri_id` | VARCHAR | Anonim müşteri kimliği (NULL = kartsız) |
| `cinsiyet` | VARCHAR | Kadın / Erkek / Belirtilmemiş |
| `dogum_yili` | INTEGER | Doğum yılı |
| `yas_grubu` | VARCHAR | Yaş grubu (2025'e göre) |
| `il` | VARCHAR | Standartlaştırılmış il adı. |
| `il_ham` | VARCHAR | Kaynaktaki ham il değeri (izlenebilirlik için). |
| `ev_magaza_id` | VARCHAR | Müşterinin ana mağazası |
| `sadakat_segmenti` | VARCHAR | Standart / Gümüş / Altın |
| `kayit_tarihi` | DATE | Sadakat kartı kayıt tarihi |

### `staging.stg_nova__satis`

Satış satırları. Ham CSV'deki çift aktarılmış (aynı satis_id) kayıtlar ayıklanır, tipler dönüştürülür, brüt/net tutar hesaplanır.

| Kolon | Tip | Açıklama |
|---|---|---|
| `satis_id` | BIGINT | Satış satırı anahtarı. |
| `sepet_id` | BIGINT | Satırın ait olduğu sepet (fiş). |
| `urun_id` | VARCHAR | Ürün kimliği |
| `adet` | INTEGER | Satılan adet; iade satırlarında negatiftir. |
| `birim_fiyat` | DECIMAL(12,2) | Satış birim fiyatı (₺) |
| `indirim_tutari` | DECIMAL(12,2) | İndirim tutarı (₺) |
| `islem_tipi` | VARCHAR | SATIS veya IADE. |
| `brut_tutar` | DECIMAL(18,2) | adet x birim_fiyat |
| `net_tutar` | DECIMAL(19,2) | brüt tutar - indirim tutarı |

### `staging.stg_nova__sepet`

Sepet (fiş) başlıkları. Boş müşteri kimliği NULL'a çevrilir.

| Kolon | Tip | Açıklama |
|---|---|---|
| `sepet_id` | BIGINT | Fiş/sepet kimliği |
| `musteri_id` | VARCHAR | Sadakat kartı yoksa NULL. |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `islem_zamani` | TIMESTAMP | Fiş tarihi-saati |
| `tarih` | DATE | İşlem günü |
| `odeme_tipi` | VARCHAR | Ödeme yöntemi |
| `sadakat_karti_var_mi` | BOOLEAN | Fişte sadakat kartı kullanıldı mı |

### `staging.stg_nova__urun`

Ürün ana verisi ve lojistik özellikler.

| Kolon | Tip | Açıklama |
|---|---|---|
| `urun_id` | VARCHAR | Ürün kimliği |
| `urun_adi` | VARCHAR | Ürün adı |
| `kategori` | VARCHAR | Ürün kategorisi |
| `sicaklik_tipi` | VARCHAR | Ortam / Soğuk / Dondurulmuş |
| `liste_fiyati` | DECIMAL(12,2) | Liste fiyatı (₺) |
| `birim_hacim_dm3` | DOUBLE | Birim hacim (dm³) |
| `birim_agirlik_kg` | DOUBLE | Birim ağırlık (kg) |
| `koli_ici_adet` | INTEGER | Koli içi adet |

## 3. Intermediate katmanı

### `intermediate.int_magaza_ikmal_siparisleri`

Koli bazlı ikmal varsayımıyla türetilen BDM -> mağaza sipariş satırları. Mağazanın bir üründeki kümülatif satışı yeni bir koli eşiğini geçtiği gün bir ikmal (toplama) satırı oluşur.

| Kolon | Tip | Açıklama |
|---|---|---|
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `urun_id` | VARCHAR | Ürün kimliği |
| `tarih` | DATE | İşlem günü |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `satis_adedi` | HUGEINT | Satış adedi (iade hariç) |
| `koli_ici_adet` | INTEGER | Koli içi adet |
| `ikmal_koli_sayisi` | INTEGER | O gün toplanan koli adedi. |

### `intermediate.int_satis_satirlari`

Satış satırları + sepet (tarih, mağaza, müşteri) + ürün lojistik özellikleri (hacim, ağırlık, koli).

| Kolon | Tip | Açıklama |
|---|---|---|
| `satis_id` | BIGINT | Satış satırı kimliği |
| `sepet_id` | BIGINT | Fiş/sepet kimliği |
| `tarih` | DATE | İşlem günü |
| `islem_zamani` | TIMESTAMP | Fiş tarihi-saati |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `musteri_id` | VARCHAR | Anonim müşteri kimliği (NULL = kartsız) |
| `urun_id` | VARCHAR | Ürün kimliği |
| `kategori` | VARCHAR | Ürün kategorisi |
| `sicaklik_tipi` | VARCHAR | Ortam / Soğuk / Dondurulmuş |
| `islem_tipi` | VARCHAR | SATIS / IADE |
| `adet` | INTEGER | Adet |
| `birim_fiyat` | DECIMAL(12,2) | Satış birim fiyatı (₺) |
| `indirim_tutari` | DECIMAL(12,2) | İndirim tutarı (₺) |
| `brut_tutar` | DECIMAL(18,2) | Adet × birim fiyat (₺) |
| `net_tutar` | DECIMAL(19,2) | Brüt tutar − indirim (₺) |
| `hacim_dm3` | DOUBLE | Satılan hacim (dm³) |
| `agirlik_kg` | DOUBLE | Satılan ağırlık (kg) |
| `koli_esdegeri` | DOUBLE | Adet / koli içi adet |

## 4. Mart katmanı

### `marts.dim_dagitim_merkezi`

Bölgesel dağıtım merkezi (BDM) konumu.

| Kolon | Tip | Açıklama |
|---|---|---|
| `bdm_id` | VARCHAR | Bölgesel dağıtım merkezi kimliği |
| `bdm_adi` | VARCHAR | BDM adı |
| `enlem` | DOUBLE | Enlem |
| `boylam` | DOUBLE | Boylam |

### `marts.dim_magaza`

Mağaza boyutu. TÜİK il nüfusu, OSRM karayolu mesafesi ve BDM'ye göre yön (rota kümesi: Kuzey/Doğu/Güney/Batı) ile zenginleştirilmiştir.

| Kolon | Tip | Açıklama |
|---|---|---|
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `magaza_adi` | VARCHAR | Mağaza adı |
| `il` | VARCHAR | İl adı (standart) |
| `il_kodu` | INTEGER | Plaka kodu |
| `il_nufusu` | BIGINT | Mağazanın bulunduğu ilin nüfusu |
| `ilce` | VARCHAR | İlçe |
| `enlem` | DOUBLE | Enlem |
| `boylam` | DOUBLE | Boylam |
| `magaza_tipi` | VARCHAR | Büyük / Orta / Küçük |
| `satis_alani_m2` | INTEGER | Satış alanı (m²) |
| `acilis_tarihi` | DATE | Mağaza açılış tarihi |
| `bdm_id` | VARCHAR | Bölgesel dağıtım merkezi kimliği |
| `mesafe_km` | DOUBLE | BDM'den mağazaya karayolu mesafesi (km). |
| `surus_suresi_dk` | DOUBLE | BDM'den sürüş süresi (dk) |
| `mesafe_kaynagi` | VARCHAR | Mesafe kaynağı (OSRM API / yedek) |
| `yon_derece` | DOUBLE | BDM'den pusula açısı (0 = Kuzey) |
| `rota_kumesi` | VARCHAR | BDM'ye göre yön kümesi (Kuzey/Doğu/Güney/Batı) |

### `marts.dim_tarih`

Tarih boyutu. `tam_hafta_mi`, haftanın tamamı veri döneminde ise true'dur.

| Kolon | Tip | Açıklama |
|---|---|---|
| `tarih` | DATE | İşlem günü |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `yil` | BIGINT | Yıl |
| `ay` | BIGINT | Ay (1-12) |
| `ceyrek` | BIGINT | Çeyrek |
| `haftanin_gunu` | BIGINT | ISO gün (1 = Pzt) |
| `gun_adi` | VARCHAR | Gün adı |
| `ay_adi` | VARCHAR | Ay adı |
| `hafta_sonu_mu` | BOOLEAN | Cumartesi/Pazar mı |
| `sezon` | VARCHAR | Yaz Sezonu (Haz-Eyl) / Normal Sezon |
| `tam_hafta_mi` | BOOLEAN | Hafta veri döneminin tamamen içinde mi |

### `marts.dim_urun`

Ürün boyutu (koli hacmi/ağırlığı dahil).

| Kolon | Tip | Açıklama |
|---|---|---|
| `urun_id` | VARCHAR | Ürün kimliği |
| `urun_adi` | VARCHAR | Ürün adı |
| `kategori` | VARCHAR | Ürün kategorisi |
| `sicaklik_tipi` | VARCHAR | Ortam / Soğuk / Dondurulmuş |
| `liste_fiyati` | DECIMAL(12,2) | Liste fiyatı (₺) |
| `birim_hacim_dm3` | DOUBLE | Birim hacim (dm³) |
| `birim_agirlik_kg` | DOUBLE | Birim ağırlık (kg) |
| `koli_ici_adet` | INTEGER | Koli içi adet |
| `koli_hacim_dm3` | DOUBLE | Koli hacmi (dm³) |
| `koli_agirlik_kg` | DOUBLE | Koli ağırlığı (kg) |

### `marts.fct_satis`

Satış olgu tablosu (satır düzeyi) — hacim, ağırlık ve koli eşdeğeri dahil.

| Kolon | Tip | Açıklama |
|---|---|---|
| `satis_id` | BIGINT | Satış satırı kimliği |
| `sepet_id` | BIGINT | Fiş/sepet kimliği |
| `tarih` | DATE | İşlem günü |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `musteri_id` | VARCHAR | Anonim müşteri kimliği (NULL = kartsız) |
| `urun_id` | VARCHAR | Ürün kimliği |
| `kategori` | VARCHAR | Ürün kategorisi |
| `sicaklik_tipi` | VARCHAR | Ortam / Soğuk / Dondurulmuş |
| `islem_tipi` | VARCHAR | SATIS / IADE |
| `adet` | INTEGER | Adet |
| `birim_fiyat` | DECIMAL(12,2) | Satış birim fiyatı (₺) |
| `indirim_tutari` | DECIMAL(12,2) | İndirim tutarı (₺) |
| `brut_tutar` | DECIMAL(18,2) | Adet × birim fiyat (₺) |
| `net_tutar` | DECIMAL(19,2) | Brüt tutar − indirim (₺) |
| `hacim_dm3` | DOUBLE | Satılan hacim (dm³) |
| `agirlik_kg` | DOUBLE | Satılan ağırlık (kg) |
| `koli_esdegeri` | DOUBLE | Adet / koli içi adet |

### `marts.mart_dagitim_plani`

Mağaza dağıtım planı: P90 haftalık talebi hedef doluluk oranıyla karşılayan en düşük maliyetli araç tipi ve haftalık sevkiyat sıklığı.

| Kolon | Tip | Açıklama |
|---|---|---|
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `magaza_adi` | VARCHAR | Mağaza adı |
| `il` | VARCHAR | İl adı (standart) |
| `ilce` | VARCHAR | İlçe |
| `magaza_tipi` | VARCHAR | Büyük / Orta / Küçük |
| `rota_kumesi` | VARCHAR | BDM'ye göre yön kümesi (Kuzey/Doğu/Güney/Batı) |
| `mesafe_km` | DOUBLE | BDM'den karayolu mesafesi (km) |
| `surus_suresi_dk` | DOUBLE | BDM'den sürüş süresi (dk) |
| `ort_haftalik_hacim_m3` | DOUBLE | Tam haftalarda ortalama haftalık hacim (m³, ölçekli) |
| `p90_haftalik_hacim_m3` | DOUBLE | Haftalık hacmin %90'lık dilimi (m³, ölçekli) |
| `ort_haftalik_agirlik_kg` | DOUBLE | Ortalama haftalık ağırlık (kg, ölçekli) |
| `talep_cv` | DOUBLE | Haftalık hacmin varyasyon katsayısı |
| `onerilen_arac_tipi` | VARCHAR | Önerilen araç tipi |
| `haftalik_sevkiyat_sayisi` | INTEGER | Önerilen haftalık sefer sayısı |
| `onerilen_sevkiyat_gunleri` | VARCHAR | Önerilen sevkiyat günleri |
| `arac_hacim_kapasite_m3` | INTEGER | Araç hacim kapasitesi (m³) |
| `sefer_basi_p90_hacim_m3` | DOUBLE | P90 hacmin sefer başına düşen kısmı |
| `arac_agirlik_kapasite_kg` | INTEGER | Araç ağırlık kapasitesi (kg) |
| `ort_hacim_doluluk_orani` | DOUBLE | Ortalama hacim doluluğu |
| `ort_agirlik_doluluk_orani` | DOUBLE | Ortalama ağırlık doluluğu |
| `ort_arac_doluluk_orani` | DOUBLE | Ortalama haftada aracın bağlayıcı (hacim veya ağırlık) kapasitesinin doluluk oranı. |
| `baglayici_kisit` | VARCHAR | P90 talepte aracın önce dolan kapasite boyutu. |
| `sefer_maliyeti_tl` | DOUBLE | Bir sefer maliyeti: sabit + 2 × mesafe × km maliyeti (₺) |
| `haftalik_tasima_maliyeti_tl` | DOUBLE | Haftalık toplam taşıma maliyeti (₺) |
| `haftalik_km` | DOUBLE | Haftalık toplam km |
| `m3_basi_tasima_maliyeti_tl` | DOUBLE | m³ başına taşıma maliyeti (₺) |

### `marts.mart_gunluk_kategori_satis`

Dashboard için gün x mağaza x kategori özeti.

| Kolon | Tip | Açıklama |
|---|---|---|
| `tarih` | DATE | İşlem günü |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `il` | VARCHAR | İl adı (standart) |
| `rota_kumesi` | VARCHAR | BDM'ye göre yön kümesi (Kuzey/Doğu/Güney/Batı) |
| `kategori` | VARCHAR | Ürün kategorisi |
| `satis_adedi` | HUGEINT | Satış adedi (iade hariç) |
| `net_ciro` | DECIMAL(38,2) | Net satış tutarı, iade hariç (₺) |
| `iade_tutari` | DECIMAL(38,2) | İade edilen tutar (₺, pozitif) |
| `hacim_m3` | DOUBLE | Satılan hacim (m³, örneklem) |

### `marts.mart_gunluk_magaza_ozet`

Dashboard için gün x mağaza sepet sayısı ve ciro.

| Kolon | Tip | Açıklama |
|---|---|---|
| `tarih` | DATE | İşlem günü |
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `il` | VARCHAR | İl adı (standart) |
| `rota_kumesi` | VARCHAR | BDM'ye göre yön kümesi (Kuzey/Doğu/Güney/Batı) |
| `sepet_sayisi` | BIGINT | Fiş sayısı |
| `kartli_sepet_sayisi` | BIGINT | Sadakat kartlı fiş sayısı |
| `net_ciro` | DECIMAL(38,2) | Net satış tutarı, iade hariç (₺) |

### `marts.mart_il_talep_ozeti`

İl bazında satış + TÜİK nüfusu; 10.000 kişi başına ciro ve mağaza başına nüfus.

| Kolon | Tip | Açıklama |
|---|---|---|
| `il_kodu` | INTEGER | Plaka kodu |
| `il` | VARCHAR | İl adı (standart) |
| `nufus` | BIGINT | TÜİK ADNKS nüfusu |
| `nufus_yili` | INTEGER | Nüfus verisinin yılı |
| `magaza_sayisi` | BIGINT | Mağaza sayısı |
| `magaza_basina_nufus` | DOUBLE | İl nüfusu / mağaza sayısı |
| `net_ciro` | DECIMAL(38,2) | Net satış tutarı, iade hariç (₺) |
| `on_bin_kisi_basina_ciro` | DOUBLE | 10.000 kişi başına net ciro (₺, örneklem) |
| `toplam_hacim_m3` | DOUBLE | Yıllık hacim (m³) |
| `ort_bdm_mesafesi_km` | DOUBLE | İldeki mağazaların ortalama BDM mesafesi (km) |

### `marts.mart_magaza_haftalik_talep`

Mağaza x hafta talep profili. `tahmini_toplam_*` kolonları örneklemi toplam talebe ölçekler.

| Kolon | Tip | Açıklama |
|---|---|---|
| `magaza_id` | VARCHAR | Mağaza kimliği |
| `hafta_baslangic` | DATE | Haftanın pazartesi tarihi (ISO hafta) |
| `tam_hafta_mi` | BOOLEAN | Hafta veri döneminin tamamen içinde mi |
| `gun_sayisi` | BIGINT | Haftadaki satış günü sayısı |
| `sepet_sayisi` | BIGINT | Fiş sayısı |
| `adet` | HUGEINT | Adet |
| `net_ciro` | DECIMAL(38,2) | Net satış tutarı, iade hariç (₺) |
| `koli_esdegeri` | DOUBLE | Adet / koli içi adet |
| `hacim_m3` | DOUBLE | Satılan hacim (m³, örneklem) |
| `agirlik_kg` | DOUBLE | Satılan ağırlık (kg) |
| `tahmini_toplam_hacim_m3` | DOUBLE | Örneklem hacmi × talep_olcek_katsayisi (m³) |
| `tahmini_toplam_agirlik_kg` | DOUBLE | Örneklem ağırlığı × talep_olcek_katsayisi (kg) |

### `marts.mart_urun_abc_xyz`

Depo yerleşimi (slotting) tablosu. Ürünler BDM'deki toplama sıklığına göre ABC, haftalık talep düzenliliğine (varyasyon katsayısı) göre XYZ sınıflarına ayrılır ve `depo_yerlesim_kurallari` seed'i ile depo bölgesi / raf seviyesi önerisi alır.

| Kolon | Tip | Açıklama |
|---|---|---|
| `urun_id` | VARCHAR | Ürün kimliği |
| `urun_adi` | VARCHAR | Ürün adı |
| `kategori` | VARCHAR | Ürün kategorisi |
| `sicaklik_tipi` | VARCHAR | Ortam / Soğuk / Dondurulmuş |
| `toplam_adet` | HUGEINT | Yıllık satış adedi |
| `toplam_ciro` | DECIMAL(38,2) | Yıllık net ciro (₺) |
| `toplam_hacim_m3` | DOUBLE | Yıllık hacim (m³) |
| `toplama_satiri_sayisi` | BIGINT | BDM'deki toplama (pick) satırı sayısı = koli bazlı ikmal sipariş satırları (int_magaza_ikmal_siparisleri). |
| `toplanan_koli_sayisi` | HUGEINT | Yıl boyunca BDM'de bu ürün için toplanan koli adedi. |
| `satilan_magaza_sayisi` | BIGINT | Ürünün satıldığı mağaza sayısı |
| `haftalik_ort_adet` | DOUBLE | Haftalık ortalama satış adedi |
| `varyasyon_katsayisi` | DOUBLE | Haftalık satış adedinin standart sapma / ortalaması (yalnızca tam haftalar). |
| `toplama_payi` | DOUBLE | Ürünün toplam toplama satırları içindeki payı |
| `kumulatif_toplama_payi` | DOUBLE | Hız sırasına göre kümülatif toplama payı (Pareto). |
| `hiz_sirasi` | BIGINT | Toplama sıklığına göre sıra (1 = en hızlı) |
| `abc_sinifi` | VARCHAR | A / B / C (toplama sıklığı) |
| `xyz_sinifi` | VARCHAR | X / Y / Z (talep düzenliliği) |
| `abc_xyz` | VARCHAR | Birleşik sınıf (örn. AX) |
| `coi` | DOUBLE | Cube-per-Order Index — haftalık raf hacmi (dm3) / haftalık toplama sayısı. Düşük COI rampaya yakın yerleştirilir. |
| `onerilen_depo_bolgesi` | VARCHAR | Önerilen depo bölgesi (sıcaklık bölgesi dahil) |
| `onerilen_raf_seviyesi` | VARCHAR | Önerilen raf seviyesi |
| `yerlesim_onceligi` | INTEGER | Yerleşim önceliği (1 = rampaya en yakın) |
| `yerlesim_gerekcesi` | VARCHAR | Öneri gerekçesi |

## 5. Referans (seed) tabloları

### `referans.arac_tipleri`



| Kolon | Tip | Açıklama |
|---|---|---|
| `arac_tipi` | VARCHAR | Araç tipi |
| `hacim_kapasite_m3` | INTEGER | Hacim kapasitesi (m³) |
| `agirlik_kapasite_kg` | INTEGER | Ağırlık kapasitesi (kg) |
| `sefer_sabit_maliyet_tl` | INTEGER | Sefer başına sabit maliyet: şoför, yükleme (₺) |
| `km_maliyet_tl` | INTEGER | km başına değişken maliyet (₺) |
| `kucuk_magazaya_uygun` | BOOLEAN | Küçük (şehir içi) mağazaya girebilir mi |

### `referans.depo_yerlesim_kurallari`



| Kolon | Tip | Açıklama |
|---|---|---|
| `abc_xyz` | VARCHAR | Birleşik sınıf (örn. AX) |
| `depo_bolgesi` | VARCHAR | Depo bölgesi |
| `raf_seviyesi` | VARCHAR | Raf seviyesi |
| `oncelik` | INTEGER | Yerleşim önceliği |
| `aciklama` | VARCHAR | Kural açıklaması |
