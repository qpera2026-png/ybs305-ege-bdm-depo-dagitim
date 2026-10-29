select
    trim(bdm_id)            as bdm_id,
    trim(ad)                as bdm_adi,
    cast(enlem as double)   as enlem,
    cast(boylam as double)  as boylam
from {{ source('nova', 'dagitim_merkezi') }}
