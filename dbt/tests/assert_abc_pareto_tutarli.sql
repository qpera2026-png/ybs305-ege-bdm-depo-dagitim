-- ABC sınıflaması Pareto ilkesine uymalı:
-- (1) A sınıfı ürünler toplam toplama satırlarının en az %70'ini oluşturmalı,
-- (2) her A ürününün hız sırası her B ürününden, her B ürünününki her C ürününden önce gelmeli.
with paylar as (
    select abc_sinifi, sum(toplama_payi) as pay, min(hiz_sirasi) as ilk_sira, max(hiz_sirasi) as son_sira
    from {{ ref('mart_urun_abc_xyz') }}
    group by abc_sinifi
)
select 'A payi dusuk' as hata from paylar where abc_sinifi = 'A' and pay < 0.70
union all
select 'Siralama bozuk' from paylar a join paylar b
    on (a.abc_sinifi = 'A' and b.abc_sinifi = 'B') or (a.abc_sinifi = 'B' and b.abc_sinifi = 'C')
where a.son_sira > b.ilk_sira
