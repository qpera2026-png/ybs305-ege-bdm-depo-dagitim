# data/raw

NovaPerakende ham verisi buraya konur (CSV). Dosyalar repoya eklenmez (.gitignore).

Şu an test verisi kullanılıyor:

```bash
python scripts/generate_nova_test_data.py   # seed=42, tekrar üretilebilir
```

Gerçek veri geldiğinde aynı adlarla (`perakende_satis.csv`, `sepet.csv`, `musteri.csv`,
`urun.csv`, `magaza.csv`, `dagitim_merkezi.csv`) buraya kopyalayın ve
`python scripts/run_pipeline.py --veri-uretme` çalıştırın. Kolon adları farklıysa yalnızca
`dbt/models/staging/stg_nova__*.sql` dosyalarında eşleme güncellenir.
