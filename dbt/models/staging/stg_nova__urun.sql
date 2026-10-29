select
    trim(urun_id)                               as urun_id,
    trim(urun_adi)                              as urun_adi,
    trim(kategori)                              as kategori,
    trim(sicaklik_tipi)                         as sicaklik_tipi,
    cast(birim_fiyat as decimal(12, 2))         as liste_fiyati,
    cast(birim_hacim_dm3 as double)             as birim_hacim_dm3,
    cast(birim_agirlik_kg as double)            as birim_agirlik_kg,
    cast(koli_ici_adet as integer)              as koli_ici_adet
from {{ source('nova', 'urun') }}
