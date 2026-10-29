-- BDM -> mağaza ikmal sipariş satırları (koli bazlı ikmal varsayımı)
-- Mağaza, bir ürünün kümülatif satışı yeni bir koli eşiğini geçtiği gün BDM'den o ürünü sipariş eder.
-- Bu satırlar BDM'deki toplama (pick) satırlarını, ikmal_koli_sayisi ise toplanan koli adedini temsil eder.
with gunluk as (
    select magaza_id, urun_id, tarih, hafta_baslangic, sum(adet) as adet
    from {{ ref('int_satis_satirlari') }}
    where islem_tipi = 'SATIS'
    group by all
),
kumulatif as (
    select
        g.*,
        u.koli_ici_adet,
        ceil(sum(g.adet) over (partition by g.magaza_id, g.urun_id order by g.tarih
                               rows between unbounded preceding and current row) / u.koli_ici_adet) as koli_no
    from gunluk g
    join {{ ref('stg_nova__urun') }} u using (urun_id)
),
farklar as (
    select
        *,
        koli_no - coalesce(lag(koli_no) over (partition by magaza_id, urun_id order by tarih), 0) as ikmal_koli_sayisi
    from kumulatif
)
select
    magaza_id,
    urun_id,
    tarih,
    hafta_baslangic,
    adet                        as satis_adedi,
    koli_ici_adet,
    cast(ikmal_koli_sayisi as integer) as ikmal_koli_sayisi
from farklar
where ikmal_koli_sayisi > 0
