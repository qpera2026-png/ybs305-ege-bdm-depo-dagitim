-- Dağıtım planı, P90 haftalık hacmi seçilen araç kapasitesi x sevkiyat sayısı x hedef doluluk ile karşılamalı.
select magaza_id, p90_haftalik_hacim_m3, haftalik_sevkiyat_sayisi, arac_hacim_kapasite_m3
from {{ ref('mart_dagitim_plani') }}
where p90_haftalik_hacim_m3
      > haftalik_sevkiyat_sayisi * arac_hacim_kapasite_m3 * {{ var('hedef_doluluk') }} + 0.01
