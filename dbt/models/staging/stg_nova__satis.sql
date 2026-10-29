-- Satış satırları: tip dönüşümü, tekrar eden kayıtların ayıklanması, tutar hesapları
with kaynak as (
    select * from {{ source('nova', 'perakende_satis') }}
),

tipli as (
    select
        cast(satis_id as bigint)                 as satis_id,
        cast(sepet_id as bigint)                 as sepet_id,
        trim(urun_id)                            as urun_id,
        cast(adet as integer)                    as adet,
        cast(birim_fiyat as decimal(12, 2))      as birim_fiyat,
        coalesce(try_cast(indirim_tutari as decimal(12, 2)), 0) as indirim_tutari,
        upper(trim(islem_tipi))                  as islem_tipi
    from kaynak
),

tekilsiz as (
    -- Aynı satis_id ile birden fazla gelen (çift aktarılmış) kayıtlardan yalnızca biri tutulur
    select *
    from tipli
    qualify row_number() over (partition by satis_id order by satis_id) = 1
)

select
    satis_id,
    sepet_id,
    urun_id,
    adet,
    birim_fiyat,
    indirim_tutari,
    islem_tipi,
    adet * birim_fiyat                       as brut_tutar,
    adet * birim_fiyat - indirim_tutari      as net_tutar
from tekilsiz
