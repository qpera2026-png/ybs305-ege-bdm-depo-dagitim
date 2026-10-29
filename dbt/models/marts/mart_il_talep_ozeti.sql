-- İl bazında talep yoğunluğu: NovaPerakende satışları + TÜİK nüfusu (dış kaynak)
with magaza as (select * from {{ ref('dim_magaza') }}),
satis as (
    select magaza_id, sum(net_tutar) as net_ciro, sum(hacim_dm3) / 1000 as hacim_m3
    from {{ ref('fct_satis') }}
    where islem_tipi = 'SATIS'
    group by magaza_id
)
select
    il.il_kodu,
    il.il_adi                                               as il,
    il.nufus,
    il.nufus_yili,
    count(m.magaza_id)                                      as magaza_sayisi,
    round(il.nufus / nullif(count(m.magaza_id), 0), 0)      as magaza_basina_nufus,
    round(sum(s.net_ciro), 2)                               as net_ciro,
    round(sum(s.net_ciro) / il.nufus * 10000, 2)            as on_bin_kisi_basina_ciro,
    round(sum(s.hacim_m3), 2)                               as toplam_hacim_m3,
    round(avg(m.mesafe_km), 1)                              as ort_bdm_mesafesi_km
from {{ ref('stg_dis__il_nufus') }} il
left join magaza m on m.il = il.il_adi
left join satis s on s.magaza_id = m.magaza_id
group by il.il_kodu, il.il_adi, il.nufus, il.nufus_yili
