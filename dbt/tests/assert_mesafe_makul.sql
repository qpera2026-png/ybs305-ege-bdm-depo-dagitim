-- Ege BDM'den bölge mağazalarına karayolu mesafesi 0-600 km arasında olmalı (koordinat/API hatası yakalama).
select magaza_id, mesafe_km
from {{ ref('dim_magaza') }}
where mesafe_km is null or mesafe_km <= 0 or mesafe_km > 600
