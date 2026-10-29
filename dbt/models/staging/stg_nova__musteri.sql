-- Müşteri: il adlarının standartlaştırılması (TÜİK il listesine eşleme), boş değerlerin temizliği
with kaynak as (
    select * from {{ source('nova', 'musteri') }}
),

iller as (
    select il_adi, {{ il_anahtari('il_adi') }} as il_anahtari
    from {{ ref('stg_dis__il_nufus') }}
)

select
    k.musteri_id,
    case upper(trim(k.cinsiyet)) when 'K' then 'Kadın' when 'E' then 'Erkek' else 'Belirtilmemiş' end as cinsiyet,
    try_cast(k.dogum_yili as integer)                    as dogum_yili,
    case
        when try_cast(k.dogum_yili as integer) is null then 'Bilinmiyor'
        when 2025 - cast(k.dogum_yili as integer) < 25 then '18-24'
        when 2025 - cast(k.dogum_yili as integer) < 35 then '25-34'
        when 2025 - cast(k.dogum_yili as integer) < 50 then '35-49'
        when 2025 - cast(k.dogum_yili as integer) < 65 then '50-64'
        else '65+'
    end                                                  as yas_grubu,
    coalesce(i.il_adi, 'Bilinmiyor')                     as il,
    trim(k.il)                                           as il_ham,
    trim(k.ev_magaza_id)                                 as ev_magaza_id,
    trim(k.sadakat_segmenti)                             as sadakat_segmenti,
    cast(k.kayit_tarihi as date)                         as kayit_tarihi
from kaynak k
left join iller i
    on {{ il_anahtari('k.il') }} = i.il_anahtari
