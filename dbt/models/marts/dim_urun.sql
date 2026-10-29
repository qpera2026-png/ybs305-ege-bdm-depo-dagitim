select
    urun_id,
    urun_adi,
    kategori,
    sicaklik_tipi,
    liste_fiyati,
    birim_hacim_dm3,
    birim_agirlik_kg,
    koli_ici_adet,
    birim_hacim_dm3 * koli_ici_adet     as koli_hacim_dm3,
    birim_agirlik_kg * koli_ici_adet    as koli_agirlik_kg
from {{ ref('stg_nova__urun') }}
