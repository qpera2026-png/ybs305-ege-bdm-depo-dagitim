select
    cast(il_kodu as integer)    as il_kodu,
    trim(il_adi)                as il_adi,
    trim(bolge)                 as bolge,
    cast(nufus as bigint)       as nufus,
    cast(yil as integer)        as nufus_yili,
    trim(kaynak)                as kaynak
from {{ source('dis_kaynak', 'il_nufus_tuik') }}
