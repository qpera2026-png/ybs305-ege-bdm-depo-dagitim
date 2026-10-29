-- Bölgesel dağıtım merkezi boyutu (dashboard haritası için)
select * from {{ ref('stg_nova__dagitim_merkezi') }}
