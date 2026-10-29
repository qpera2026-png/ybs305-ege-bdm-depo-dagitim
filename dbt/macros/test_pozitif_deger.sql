{# Özel generic test: kolondaki tüm değerler 0'dan büyük olmalı. #}
{% test pozitif_deger(model, column_name) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} <= 0
{% endtest %}
