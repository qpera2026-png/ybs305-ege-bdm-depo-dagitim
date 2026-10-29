-- SATIS tipindeki satırlarda adet her zaman pozitif olmalı; IADE satırlarında negatif olmalı.
select satis_id, islem_tipi, adet
from {{ ref('fct_satis') }}
where (islem_tipi = 'SATIS' and adet <= 0)
   or (islem_tipi = 'IADE' and adet >= 0)
