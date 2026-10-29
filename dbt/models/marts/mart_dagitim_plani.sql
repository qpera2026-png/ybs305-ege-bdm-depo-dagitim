-- MAĞAZA DAĞITIM PLANI
-- Her mağaza için haftalık talebin %90'lık dilimini (P90) karşılayacak en düşük maliyetli
-- araç tipi + haftalık sevkiyat sıklığı kombinasyonu seçilir.
-- Varsayım: BDM -> mağaza -> BDM doğrudan sefer (gidiş-dönüş = 2 x mesafe).
with talep as (
    select
        magaza_id,
        avg(tahmini_toplam_hacim_m3)                                        as ort_haftalik_hacim_m3,
        quantile_cont(tahmini_toplam_hacim_m3, 0.9)                         as p90_haftalik_hacim_m3,
        avg(tahmini_toplam_agirlik_kg)                                      as ort_haftalik_agirlik_kg,
        quantile_cont(tahmini_toplam_agirlik_kg, 0.9)                       as p90_haftalik_agirlik_kg,
        stddev_pop(tahmini_toplam_hacim_m3) / avg(tahmini_toplam_hacim_m3)  as talep_cv
    from {{ ref('mart_magaza_haftalik_talep') }}
    where tam_hafta_mi
    group by magaza_id
),
adaylar as (
    select
        m.magaza_id,
        a.arac_tipi,
        a.hacim_kapasite_m3,
        a.agirlik_kapasite_kg,
        greatest(
            ceil(t.p90_haftalik_hacim_m3 / (a.hacim_kapasite_m3 * {{ var('hedef_doluluk') }})),
            ceil(t.p90_haftalik_agirlik_kg / (a.agirlik_kapasite_kg * {{ var('hedef_doluluk') }})),
            {{ var('min_haftalik_sevkiyat') }}
        )::integer                                                          as haftalik_sevkiyat_sayisi,
        a.sefer_sabit_maliyet_tl + 2 * m.mesafe_km * a.km_maliyet_tl        as sefer_maliyeti_tl
    from {{ ref('dim_magaza') }} m
    join talep t using (magaza_id)
    cross join {{ ref('arac_tipleri') }} a
    -- Tır, şehir içindeki küçük mağazalara giremez
    where a.kucuk_magazaya_uygun or m.magaza_tipi <> 'Küçük'
),
secim as (
    select
        *,
        haftalik_sevkiyat_sayisi * sefer_maliyeti_tl as haftalik_tasima_maliyeti_tl
    from adaylar
    where haftalik_sevkiyat_sayisi <= 7
    qualify row_number() over (
        partition by magaza_id
        order by haftalik_sevkiyat_sayisi * sefer_maliyeti_tl, haftalik_sevkiyat_sayisi desc
    ) = 1
)

select
    m.magaza_id,
    m.magaza_adi,
    m.il,
    m.ilce,
    m.magaza_tipi,
    m.rota_kumesi,
    m.mesafe_km,
    m.surus_suresi_dk,
    round(t.ort_haftalik_hacim_m3, 2)                       as ort_haftalik_hacim_m3,
    round(t.p90_haftalik_hacim_m3, 2)                       as p90_haftalik_hacim_m3,
    round(t.ort_haftalik_agirlik_kg, 0)                     as ort_haftalik_agirlik_kg,
    round(t.talep_cv, 3)                                    as talep_cv,
    s.arac_tipi                                             as onerilen_arac_tipi,
    s.haftalik_sevkiyat_sayisi,
    case s.haftalik_sevkiyat_sayisi
        when 1 then 'Pzt'
        when 2 then 'Pzt, Per'
        when 3 then 'Pzt, Çar, Cum'
        when 4 then 'Pzt, Sal, Per, Cum'
        when 5 then 'Pzt-Cum'
        when 6 then 'Pzt-Cmt'
        else 'Her gün'
    end                                                     as onerilen_sevkiyat_gunleri,
    s.hacim_kapasite_m3                                     as arac_hacim_kapasite_m3,
    round(t.p90_haftalik_hacim_m3 / s.haftalik_sevkiyat_sayisi, 2) as sefer_basi_p90_hacim_m3,
    s.agirlik_kapasite_kg                                   as arac_agirlik_kapasite_kg,
    round(t.ort_haftalik_hacim_m3 / (s.haftalik_sevkiyat_sayisi * s.hacim_kapasite_m3), 3)     as ort_hacim_doluluk_orani,
    round(t.ort_haftalik_agirlik_kg / (s.haftalik_sevkiyat_sayisi * s.agirlik_kapasite_kg), 3) as ort_agirlik_doluluk_orani,
    -- Araç kapasitesinin hangi boyutu önce doluyor? (gıda sevkiyatında çoğunlukla ağırlık)
    round(greatest(t.ort_haftalik_hacim_m3 / (s.haftalik_sevkiyat_sayisi * s.hacim_kapasite_m3),
                   t.ort_haftalik_agirlik_kg / (s.haftalik_sevkiyat_sayisi * s.agirlik_kapasite_kg)), 3) as ort_arac_doluluk_orani,
    case when t.p90_haftalik_agirlik_kg / s.agirlik_kapasite_kg > t.p90_haftalik_hacim_m3 / s.hacim_kapasite_m3
         then 'Ağırlık' else 'Hacim' end                    as baglayici_kisit,
    round(s.sefer_maliyeti_tl, 0)                           as sefer_maliyeti_tl,
    round(s.haftalik_tasima_maliyeti_tl, 0)                 as haftalik_tasima_maliyeti_tl,
    round(2 * m.mesafe_km * s.haftalik_sevkiyat_sayisi, 0)  as haftalik_km,
    round(s.haftalik_tasima_maliyeti_tl / nullif(t.ort_haftalik_hacim_m3, 0), 1) as m3_basi_tasima_maliyeti_tl
from {{ ref('dim_magaza') }} m
join talep t using (magaza_id)
join secim s using (magaza_id)
