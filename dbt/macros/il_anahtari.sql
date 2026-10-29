{# İl adlarını karşılaştırma için normalize eder: "  İZMİR", "izmir", "Izmir" -> "izmir" #}
{% macro il_anahtari(kolon) -%}
    replace(strip_accents(lower(trim({{ kolon }}))), 'ı', 'i')
{%- endmacro %}
