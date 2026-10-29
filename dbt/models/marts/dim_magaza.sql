-- Mağaza boyutu: TÜİK il nüfusu, OSRM mesafesi ve BDM'ye göre yön (rota kümesi) ile zenginleştirilmiş
with m as (select * from {{ ref('stg_nova__magaza') }}),
bdm as (select * from {{ ref('stg_nova__dagitim_merkezi') }}),
mesafe as (select * from {{ ref('stg_dis__magaza_mesafe') }}),
il as (select * from {{ ref('stg_dis__il_nufus') }}),

yonlu as (
    select
        m.*,
        bdm.bdm_id,
        -- BDM'den mağazaya pusula açısı (0 = Kuzey, 90 = Doğu)
        (degrees(atan2(
            sin(radians(m.boylam - bdm.boylam)) * cos(radians(m.enlem)),
            cos(radians(bdm.enlem)) * sin(radians(m.enlem))
              - sin(radians(bdm.enlem)) * cos(radians(m.enlem)) * cos(radians(m.boylam - bdm.boylam))
        )) + 360) % 360 as yon_derece
    from m cross join bdm
)

select
    y.magaza_id,
    y.magaza_adi,
    y.il,
    il.il_kodu,
    il.nufus                    as il_nufusu,
    y.ilce,
    y.enlem,
    y.boylam,
    y.magaza_tipi,
    y.satis_alani_m2,
    y.acilis_tarihi,
    y.bdm_id,
    ms.mesafe_km,
    ms.surus_suresi_dk,
    ms.mesafe_kaynagi,
    round(y.yon_derece, 1)      as yon_derece,
    case
        when y.yon_derece >= 315 or y.yon_derece < 45 then 'Kuzey Rotası'
        when y.yon_derece < 135 then 'Doğu Rotası'
        when y.yon_derece < 225 then 'Güney Rotası'
        else 'Batı Rotası'
    end                         as rota_kumesi
from yonlu y
left join mesafe ms on y.magaza_id = ms.magaza_id
left join il on y.il = il.il_adi
