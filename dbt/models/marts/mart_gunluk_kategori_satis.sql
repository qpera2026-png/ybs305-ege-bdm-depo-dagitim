-- Dashboard için gün x mağaza x kategori özeti (filtrelenebilir)
select
    f.tarih,
    f.hafta_baslangic,
    f.magaza_id,
    m.il,
    m.rota_kumesi,
    f.kategori,
    sum(case when f.islem_tipi = 'SATIS' then f.adet else 0 end)                        as satis_adedi,
    round(sum(case when f.islem_tipi = 'SATIS' then f.net_tutar else 0 end), 2)         as net_ciro,
    round(-sum(case when f.islem_tipi = 'IADE' then f.net_tutar else 0 end), 2)         as iade_tutari,
    round(sum(case when f.islem_tipi = 'SATIS' then f.hacim_dm3 else 0 end) / 1000, 4)  as hacim_m3
from {{ ref('fct_satis') }} f
join {{ ref('dim_magaza') }} m using (magaza_id)
group by all
