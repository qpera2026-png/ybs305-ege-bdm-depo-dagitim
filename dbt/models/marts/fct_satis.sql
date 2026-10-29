-- Olgu tablosu: satış satırı düzeyi (iade satırları islem_tipi = 'IADE')
select
    satis_id,
    sepet_id,
    tarih,
    hafta_baslangic,
    magaza_id,
    musteri_id,
    urun_id,
    kategori,
    sicaklik_tipi,
    islem_tipi,
    adet,
    birim_fiyat,
    indirim_tutari,
    brut_tutar,
    net_tutar,
    hacim_dm3,
    agirlik_kg,
    koli_esdegeri
from {{ ref('int_satis_satirlari') }}
