-- DEPO YERLEŞİMİ (slotting) analizi
-- ABC: BDM'deki toplama (pick) sıklığına göre; toplama satırı = koli bazlı ikmal sipariş satırı
--      (bkz. int_magaza_ikmal_siparisleri)
-- XYZ: haftalık talebin varyasyon katsayısına (CV) göre talep düzenliliği
-- COI (Cube-per-Order Index): haftalık gereken raf hacmi / haftalık toplama sayısı; düşük COI -> rampaya yakın
with satis as (
    select * from {{ ref('fct_satis') }} where islem_tipi = 'SATIS'
),
ikmal as (
    select * from {{ ref('int_magaza_ikmal_siparisleri') }}
),
tam_haftalar as (
    select distinct hafta_baslangic from {{ ref('dim_tarih') }} where tam_hafta_mi
),
urun_ozet as (
    select
        s.urun_id,
        s.toplam_adet,
        s.toplam_ciro,
        s.toplam_hacim_dm3,
        s.satilan_magaza_sayisi,
        coalesce(i.toplama_satiri_sayisi, 0)    as toplama_satiri_sayisi,
        coalesce(i.toplanan_koli_sayisi, 0)     as toplanan_koli_sayisi
    from (
        select urun_id, sum(adet) as toplam_adet, sum(net_tutar) as toplam_ciro,
               sum(hacim_dm3) as toplam_hacim_dm3, count(distinct magaza_id) as satilan_magaza_sayisi
        from satis
        group by urun_id
    ) s
    left join (
        select urun_id, count(*) as toplama_satiri_sayisi, sum(ikmal_koli_sayisi) as toplanan_koli_sayisi
        from ikmal
        group by urun_id
    ) i using (urun_id)
),
haftalik as (
    select s.urun_id, s.hafta_baslangic, s.adet, coalesce(i.toplama, 0) as toplama
    from (
        select urun_id, hafta_baslangic, sum(adet) as adet
        from satis
        where hafta_baslangic in (select hafta_baslangic from tam_haftalar)
        group by 1, 2
    ) s
    left join (
        select urun_id, hafta_baslangic, count(*) as toplama
        from ikmal
        group by 1, 2
    ) i using (urun_id, hafta_baslangic)
),
haftalik_tam as (
    -- Satış olmayan haftalar 0 kabul edilir
    select u.urun_id, h.hafta_baslangic,
           coalesce(w.adet, 0) as adet, coalesce(w.toplama, 0) as toplama
    from {{ ref('dim_urun') }} u
    cross join tam_haftalar h
    left join haftalik w on w.urun_id = u.urun_id and w.hafta_baslangic = h.hafta_baslangic
),
degiskenlik as (
    select
        urun_id,
        avg(adet)                                   as haftalik_ort_adet,
        stddev_pop(adet) / nullif(avg(adet), 0)     as varyasyon_katsayisi,
        avg(toplama)                                as haftalik_ort_toplama
    from haftalik_tam
    group by urun_id
),
siralama as (
    select
        o.*,
        d.haftalik_ort_adet,
        d.varyasyon_katsayisi,
        d.haftalik_ort_toplama,
        o.toplama_satiri_sayisi / sum(o.toplama_satiri_sayisi) over ()      as toplama_payi,
        sum(o.toplama_satiri_sayisi) over (order by o.toplama_satiri_sayisi desc, o.urun_id
                                           rows between unbounded preceding and current row)
            / sum(o.toplama_satiri_sayisi) over ()                          as kumulatif_toplama_payi,
        row_number() over (order by o.toplama_satiri_sayisi desc, o.urun_id) as hiz_sirasi
    from urun_ozet o
    join degiskenlik d using (urun_id)
),
siniflar as (
    select
        *,
        case
            when kumulatif_toplama_payi <= {{ var('abc_a_siniri') }} then 'A'
            when kumulatif_toplama_payi <= {{ var('abc_b_siniri') }} then 'B'
            else 'C'
        end as abc_sinifi,
        case
            when varyasyon_katsayisi <= {{ var('xyz_x_siniri') }} then 'X'
            when varyasyon_katsayisi <= {{ var('xyz_y_siniri') }} then 'Y'
            else 'Z'
        end as xyz_sinifi
    from siralama
)

select
    c.urun_id,
    u.urun_adi,
    u.kategori,
    u.sicaklik_tipi,
    c.toplam_adet,
    round(c.toplam_ciro, 2)                         as toplam_ciro,
    round(c.toplam_hacim_dm3 / 1000, 3)             as toplam_hacim_m3,
    c.toplama_satiri_sayisi,
    c.toplanan_koli_sayisi,
    c.satilan_magaza_sayisi,
    round(c.haftalik_ort_adet, 2)                   as haftalik_ort_adet,
    round(c.varyasyon_katsayisi, 3)                 as varyasyon_katsayisi,
    round(c.toplama_payi, 5)                        as toplama_payi,
    round(c.kumulatif_toplama_payi, 5)              as kumulatif_toplama_payi,
    c.hiz_sirasi,
    c.abc_sinifi,
    c.xyz_sinifi,
    c.abc_sinifi || c.xyz_sinifi                    as abc_xyz,
    -- Haftalık gereken raf hacmi (dm3) / haftalık toplama sayısı
    round(c.haftalik_ort_adet * u.birim_hacim_dm3 / nullif(c.haftalik_ort_toplama, 0), 4) as coi,
    case u.sicaklik_tipi
        when 'Soğuk' then 'Soğuk Oda (+4°C) – ' || k.depo_bolgesi
        when 'Dondurulmuş' then 'Dondurucu (-18°C) – ' || k.depo_bolgesi
        else k.depo_bolgesi
    end                                             as onerilen_depo_bolgesi,
    k.raf_seviyesi                                  as onerilen_raf_seviyesi,
    k.oncelik                                       as yerlesim_onceligi,
    k.aciklama                                      as yerlesim_gerekcesi
from siniflar c
join {{ ref('dim_urun') }} u using (urun_id)
left join {{ ref('depo_yerlesim_kurallari') }} k on k.abc_xyz = c.abc_sinifi || c.xyz_sinifi
