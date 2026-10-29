select
    trim(bdm_id)                                    as bdm_id,
    trim(magaza_id)                                 as magaza_id,
    round(cast(mesafe_m as double) / 1000, 1)       as mesafe_km,
    round(cast(sure_sn as double) / 60, 0)          as surus_suresi_dk,
    trim(kaynak)                                    as mesafe_kaynagi,
    cast(cekilme_zamani as timestamp)               as cekilme_zamani
from {{ source('dis_kaynak', 'magaza_mesafe_osrm') }}
