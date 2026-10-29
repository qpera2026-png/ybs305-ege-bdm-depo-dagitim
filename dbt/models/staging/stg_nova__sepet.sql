with kaynak as (
    select * from {{ source('nova', 'sepet') }}
)

select
    cast(sepet_id as bigint)                     as sepet_id,
    nullif(trim(musteri_id), '')                 as musteri_id,
    trim(magaza_id)                              as magaza_id,
    cast(islem_zamani as timestamp)              as islem_zamani,
    cast(islem_zamani as date)                   as tarih,
    trim(odeme_tipi)                             as odeme_tipi,
    nullif(trim(musteri_id), '') is not null     as sadakat_karti_var_mi
from kaynak
