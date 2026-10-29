-- Dashboard için gün x mağaza sepet metrikleri
with sepet_tutar as (
    select sepet_id, sum(net_tutar) as net_tutar
    from {{ ref('stg_nova__satis') }}
    where islem_tipi = 'SATIS'
    group by sepet_id
)
select
    sp.tarih,
    sp.magaza_id,
    m.il,
    m.rota_kumesi,
    count(*)                                            as sepet_sayisi,
    count(*) filter (where sp.sadakat_karti_var_mi)     as kartli_sepet_sayisi,
    round(sum(t.net_tutar), 2)                          as net_ciro
from {{ ref('stg_nova__sepet') }} sp
join {{ ref('dim_magaza') }} m using (magaza_id)
left join sepet_tutar t using (sepet_id)
group by all
