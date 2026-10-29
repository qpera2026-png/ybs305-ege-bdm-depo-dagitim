-- Dönüşüm sırasında satır kaybı olmamalı: staging'deki net tutar toplamı = olgu tablosundaki toplam.
select s.toplam as staging_toplam, f.toplam as fct_toplam
from (select round(sum(net_tutar), 2) as toplam from {{ ref('stg_nova__satis') }}) s,
     (select round(sum(net_tutar), 2) as toplam from {{ ref('fct_satis') }}) f
where abs(s.toplam - f.toplam) > 0.01
