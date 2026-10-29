-- Satış satırlarını sepet (zaman, mağaza, müşteri) ve ürün lojistik özellikleriyle zenginleştirir
select
    s.satis_id,
    s.sepet_id,
    sp.tarih,
    sp.islem_zamani,
    cast(date_trunc('week', sp.tarih) as date)          as hafta_baslangic,
    sp.magaza_id,
    sp.musteri_id,
    s.urun_id,
    u.kategori,
    u.sicaklik_tipi,
    s.islem_tipi,
    s.adet,
    s.birim_fiyat,
    s.indirim_tutari,
    s.brut_tutar,
    s.net_tutar,
    s.adet * u.birim_hacim_dm3                          as hacim_dm3,
    s.adet * u.birim_agirlik_kg                         as agirlik_kg,
    s.adet::double / u.koli_ici_adet                    as koli_esdegeri
from {{ ref('stg_nova__satis') }} s
inner join {{ ref('stg_nova__sepet') }} sp on s.sepet_id = sp.sepet_id
inner join {{ ref('stg_nova__urun') }}  u  on s.urun_id = u.urun_id
