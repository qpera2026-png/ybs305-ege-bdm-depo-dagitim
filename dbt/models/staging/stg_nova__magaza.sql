select
    trim(magaza_id)                 as magaza_id,
    trim(magaza_adi)                as magaza_adi,
    trim(il)                        as il,
    trim(ilce)                      as ilce,
    cast(enlem as double)           as enlem,
    cast(boylam as double)          as boylam,
    trim(magaza_tipi)               as magaza_tipi,
    cast(satis_alani_m2 as integer) as satis_alani_m2,
    cast(acilis_tarihi as date)     as acilis_tarihi
from {{ source('nova', 'magaza') }}
