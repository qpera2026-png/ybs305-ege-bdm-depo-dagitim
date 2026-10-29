-- Mağaza x hafta talep profili (BDM'den çekilen hacim/ağırlık). "tahmini_toplam" kolonları
-- örneklem talebini var('talep_olcek_katsayisi') ile toplam mağaza talebine ölçekler.
with satis as (
    select * from {{ ref('fct_satis') }} where islem_tipi = 'SATIS'
),
hafta as (
    select distinct hafta_baslangic, tam_hafta_mi from {{ ref('dim_tarih') }}
)
select
    s.magaza_id,
    s.hafta_baslangic,
    h.tam_hafta_mi,
    count(distinct s.tarih)                                 as gun_sayisi,
    count(distinct s.sepet_id)                              as sepet_sayisi,
    sum(s.adet)                                             as adet,
    round(sum(s.net_tutar), 2)                              as net_ciro,
    round(sum(s.koli_esdegeri), 1)                          as koli_esdegeri,
    round(sum(s.hacim_dm3) / 1000, 3)                       as hacim_m3,
    round(sum(s.agirlik_kg), 1)                             as agirlik_kg,
    round(sum(s.hacim_dm3) / 1000 * {{ var('talep_olcek_katsayisi') }}, 2) as tahmini_toplam_hacim_m3,
    round(sum(s.agirlik_kg) * {{ var('talep_olcek_katsayisi') }}, 0)       as tahmini_toplam_agirlik_kg
from satis s
join hafta h using (hafta_baslangic)
group by s.magaza_id, s.hafta_baslangic, h.tam_hafta_mi
