with sinirlar as (
    select min(tarih) as ilk, max(tarih) as son from {{ ref('stg_nova__sepet') }}
),
gunler as (
    select cast(unnest(generate_series(ilk, son, interval 1 day)) as date) as tarih from sinirlar
)
select
    tarih,
    cast(date_trunc('week', tarih) as date)             as hafta_baslangic,
    year(tarih)                                         as yil,
    month(tarih)                                        as ay,
    quarter(tarih)                                      as ceyrek,
    isodow(tarih)                                       as haftanin_gunu,
    ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'][isodow(tarih)] as gun_adi,
    ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'][month(tarih)] as ay_adi,
    isodow(tarih) in (6, 7)                             as hafta_sonu_mu,
    case when month(tarih) in (6, 7, 8, 9) then 'Yaz Sezonu' else 'Normal Sezon' end as sezon,
    -- Hafta, veri döneminin tamamen içindeyse true (kısmi haftalar istatistiklerden çıkarılır)
    date_trunc('week', tarih) >= (select ilk from sinirlar)
        and date_trunc('week', tarih) + interval 6 day <= (select son from sinirlar) as tam_hafta_mi
from gunler
