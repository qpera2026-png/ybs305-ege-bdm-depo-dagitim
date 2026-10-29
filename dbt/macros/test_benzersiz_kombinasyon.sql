{# Özel generic test: verilen kolon kombinasyonu tabloda tekil olmalı (dbt_utils paketine gerek kalmadan). #}
{% test benzersiz_kombinasyon(model, columns) %}
select {{ columns | join(', ') }}, count(*) as kayit_sayisi
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
