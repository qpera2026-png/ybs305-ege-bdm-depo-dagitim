"""
Ege Bölgesel Dağıtım Merkezi — Talep Odaklı Depo Yerleşimi ve Mağaza Dağıtım Planlaması
Streamlit dashboard'u. dbt mart tablolarının Parquet çıktılarını (data/marts) okur.

Çalıştırma:  streamlit run app/dashboard.py
"""
from decimal import Decimal
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

VERI = Path(__file__).resolve().parents[1] / "data" / "marts"

# Kategorik palet: sabit sırayla atanır, sıralamaya göre değil varlığa göre (kategori -> renk)
PALET = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
KATEGORI_SIRASI = ["Temel Gıda", "Süt ve Kahvaltılık", "İçecek", "Atıştırmalık",
                   "Temizlik", "Kişisel Bakım", "Dondurulmuş", "Ev ve Yaşam"]
KATEGORI_RENK = dict(zip(KATEGORI_SIRASI, PALET))
ROTA_SIRASI = ["Batı Rotası", "Kuzey Rotası", "Doğu Rotası", "Güney Rotası"]
ROTA_RENK = dict(zip(ROTA_SIRASI, PALET))
ABC_RENK = {"A": "#104281", "B": "#2a78d6", "C": "#86b6ef"}  # sıralı (ordinal) mavi rampa
ARKA = "rgba(0,0,0,0)"


def tl(x: float) -> str:
    return f"₺{x:,.0f}".replace(",", ".")


def tl_kisa(x: float) -> str:
    return f"₺{sayi(x / 1e6, 1)} Mn" if abs(x) >= 1e6 else tl(x)


def sayi(x: float, ondalik=0) -> str:
    s = f"{x:,.{ondalik}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def sade(fig: go.Figure, yukseklik=380) -> go.Figure:
    fig.update_layout(
        height=yukseklik, margin=dict(l=10, r=10, t=95 if fig.layout.showlegend is not False else 50, b=10),
        paper_bgcolor=ARKA, plot_bgcolor=ARKA,
        title=dict(y=0.98, yref="container", yanchor="top", x=0, xref="paper"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None),
        hoverlabel=dict(font_size=13), font=dict(size=13),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    return fig


@st.cache_data
def yukle():
    oku = lambda ad: pd.read_parquet(VERI / f"{ad}.parquet")
    d = {ad: oku(ad) for ad in [
        "dim_magaza", "mart_urun_abc_xyz", "mart_magaza_haftalik_talep", "mart_dagitim_plani",
        "mart_il_talep_ozeti", "mart_gunluk_kategori_satis", "mart_gunluk_magaza_ozet",
        "dim_dagitim_merkezi"]}
    # DuckDB decimal kolonları Parquet'ten Decimal nesnesi olarak gelir -> float
    for df in d.values():
        for kolon in df.columns:
            if df[kolon].dtype == object and isinstance(next(iter(df[kolon].dropna()), None), Decimal):
                df[kolon] = df[kolon].astype(float)
    for ad in ("mart_gunluk_kategori_satis", "mart_gunluk_magaza_ozet"):
        d[ad]["tarih"] = pd.to_datetime(d[ad]["tarih"])
    d["mart_magaza_haftalik_talep"]["hafta_baslangic"] = pd.to_datetime(d["mart_magaza_haftalik_talep"]["hafta_baslangic"])
    return d


st.set_page_config(page_title="Ege BDM – Depo ve Dağıtım Planlama", page_icon="🚚", layout="wide")
if not (VERI / "dim_magaza.parquet").exists():
    st.error("data/marts bulunamadı. Önce `dbt run` ve `python scripts/export_marts.py` çalıştırın.")
    st.stop()
D = yukle()

# ---------------------------------------------------------------- Filtreler
st.title("🚚 Ege Bölgesel Dağıtım Merkezi")
st.caption("Talep Odaklı Depo Yerleşimi ve Mağaza Dağıtım Planlaması · NovaPerakende (test verisi) + TÜİK + OSRM")

gunluk = D["mart_gunluk_kategori_satis"]
with st.sidebar:
    st.header("Filtreler")
    ilk, son = gunluk["tarih"].min().date(), gunluk["tarih"].max().date()
    tarih = st.date_input("Tarih aralığı", (ilk, son), min_value=ilk, max_value=son, format="DD.MM.YYYY")
    t0, t1 = (pd.Timestamp(tarih[0]), pd.Timestamp(tarih[1])) if len(tarih) == 2 else (pd.Timestamp(ilk), pd.Timestamp(son))
    iller = sorted(D["dim_magaza"]["il"].unique())
    sec_il = st.multiselect("İl", iller, default=iller)
    sec_rota = st.multiselect("Rota kümesi", ROTA_SIRASI, default=ROTA_SIRASI)
    sec_kat = st.multiselect("Kategori", KATEGORI_SIRASI, default=KATEGORI_SIRASI)
    st.divider()
    st.caption("Depo yerleşimi (ABC-XYZ) BDM'nin tüm mağazalara yaptığı toplamaya göre hesaplanır; "
               "il/rota filtresi bu sekmeyi etkilemez, kategori filtresi etkiler.")

magazalar = D["dim_magaza"][D["dim_magaza"]["il"].isin(sec_il) & D["dim_magaza"]["rota_kumesi"].isin(sec_rota)]
mg_ids = set(magazalar["magaza_id"])
g = gunluk[gunluk["magaza_id"].isin(mg_ids) & gunluk["kategori"].isin(sec_kat) & gunluk["tarih"].between(t0, t1)]
gm = D["mart_gunluk_magaza_ozet"]
gm = gm[gm["magaza_id"].isin(mg_ids) & gm["tarih"].between(t0, t1)]
plan = D["mart_dagitim_plani"][D["mart_dagitim_plani"]["magaza_id"].isin(mg_ids)]
abc = D["mart_urun_abc_xyz"][D["mart_urun_abc_xyz"]["kategori"].isin(sec_kat)]

if g.empty:
    st.warning("Seçilen filtrelerle veri yok.")
    st.stop()

# ---------------------------------------------------------------- KPI'lar
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Net Ciro", tl_kisa(g["net_ciro"].sum()), help="Seçili mağaza/kategori/tarihte iade hariç net satış")
sepet = gm["sepet_sayisi"].sum()
k2.metric("Sepet Sayısı", sayi(sepet), help="Kategori filtresinden bağımsızdır")
k3.metric("Ort. Sepet Tutarı", tl(gm["net_ciro"].sum() / sepet if sepet else 0))
k4.metric("Haftalık Sevk Hacmi", f"{sayi(plan['ort_haftalik_hacim_m3'].sum(), 1)} m³",
          help="Seçili mağazaların tahmini toplam haftalık ortalama hacmi (örneklem x ölçek katsayısı)")
k5.metric("Haftalık Taşıma Maliyeti", tl(plan["haftalik_tasima_maliyeti_tl"].sum()),
          help="Önerilen dağıtım planına göre tahmini haftalık maliyet")

a_say = (abc["abc_sinifi"] == "A").sum()
a_pay = abc.loc[abc["abc_sinifi"] == "A", "toplama_payi"].sum() / max(abc["toplama_payi"].sum(), 1e-9)
k6, k7, k8, k9, k10 = st.columns(5)
k6.metric("A Sınıfı Ürün", f"{a_say} / {len(abc)}", help="Toplama satırlarının ~%80'ini oluşturan ürünler")
k7.metric("A Ürünlerinin Toplama Payı", f"%{sayi(a_pay * 100, 1)}")
k8.metric("Ort. BDM Mesafesi", f"{sayi(magazalar['mesafe_km'].mean(), 0)} km")
k9.metric("Haftalık Sefer", sayi(plan["haftalik_sevkiyat_sayisi"].sum()))
k10.metric("Ort. Araç Doluluğu", f"%{sayi(plan['ort_arac_doluluk_orani'].mean() * 100, 0)}")

sekme1, sekme2, sekme3, sekme4 = st.tabs(["📈 Talep", "🏬 Depo Yerleşimi", "🗺️ Mağaza Dağıtımı", "ℹ️ Veri ve Yöntem"])

# ---------------------------------------------------------------- 1) Talep
with sekme1:
    sol, sag = st.columns([3, 2])
    with sol:
        haftalik = (g.groupby([pd.Grouper(key="tarih", freq="W-MON", label="left", closed="left"), "kategori"])
                    ["hacim_m3"].sum().reset_index())
        fig = px.bar(haftalik, x="tarih", y="hacim_m3", color="kategori",
                     color_discrete_map=KATEGORI_RENK, category_orders={"kategori": KATEGORI_SIRASI},
                     labels={"tarih": "Hafta", "hacim_m3": "Hacim (m³, örneklem)", "kategori": "Kategori"},
                     title="Haftalık talep hacmi — kategori kırılımı")
        fig.update_traces(marker_line_width=0, hovertemplate="%{x|%d.%m.%Y}<br>%{fullData.name}: %{y:.2f} m³<extra></extra>")
        fig.update_layout(bargap=0.15)
        st.plotly_chart(sade(fig, 420), width="stretch")
        st.caption("Yaz aylarında İçecek ve Dondurulmuş hacmi artıyor: BDM'de bu kategoriler için yaz öncesi "
                   "ek raf/soğuk oda kapasitesi planlanmalı.")
    with sag:
        il = D["mart_il_talep_ozeti"]
        il = il[il["il"].isin(sec_il)].sort_values("on_bin_kisi_basina_ciro")
        fig = px.bar(il, x="on_bin_kisi_basina_ciro", y="il", orientation="h",
                     labels={"on_bin_kisi_basina_ciro": "10.000 kişi başına net ciro (₺)", "il": ""},
                     title="İl bazında talep yoğunluğu (TÜİK nüfusuna göre)",
                     custom_data=["nufus", "magaza_sayisi", "ort_bdm_mesafesi_km"])
        fig.update_traces(marker_color=PALET[0], hovertemplate=(
            "<b>%{y}</b><br>10.000 kişi başına: ₺%{x:,.0f}<br>Nüfus: %{customdata[0]:,}"
            "<br>Mağaza: %{customdata[1]}<br>Ort. mesafe: %{customdata[2]} km<extra></extra>"))
        st.plotly_chart(sade(fig, 420), width="stretch")

    gun = g.assign(gun=g["tarih"].dt.dayofweek).groupby("gun")["hacim_m3"].sum().reindex(range(7), fill_value=0)
    gun = (gun / gun.sum() * 100).reset_index()
    gun["gun_adi"] = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    fig = px.bar(gun, x="gun_adi", y="hacim_m3", title="Haftanın günlerine göre talep dağılımı (%)",
                 labels={"gun_adi": "", "hacim_m3": "Haftalık hacmin payı (%)"})
    fig.update_traces(marker_color=PALET[0], hovertemplate="%{x}: %%{y:.1f}<extra></extra>")
    st.plotly_chart(sade(fig, 300), width="stretch")

# ---------------------------------------------------------------- 2) Depo yerleşimi
with sekme2:
    sol, sag = st.columns([3, 2])
    with sol:
        p = abc.sort_values("toplama_satiri_sayisi", ascending=False).reset_index(drop=True)
        p["sira_pay"] = (p.index + 1) / len(p) * 100
        p["kum"] = p["toplama_satiri_sayisi"].cumsum() / p["toplama_satiri_sayisi"].sum() * 100
        fig = go.Figure()
        for sinif in "ABC":
            s = p[p["abc_sinifi"] == sinif]
            fig.add_trace(go.Bar(x=s["sira_pay"], y=s["kum"], name=f"{sinif} sınıfı", marker_color=ABC_RENK[sinif],
                                 marker_line_width=0, customdata=s[["urun_adi", "toplama_satiri_sayisi"]],
                                 hovertemplate="%{customdata[0]}<br>Toplama satırı: %{customdata[1]:,}"
                                               "<br>Kümülatif pay: %%{y:.1f}<extra></extra>"))
        fig.update_layout(title="Pareto: ürünlerin kümülatif toplama payı", bargap=0,
                          xaxis_title="Ürünlerin yüzdesi (hız sırasına göre)", yaxis_title="Kümülatif toplama payı (%)")
        fig.add_hline(y=80, line_dash="dot", line_color="gray", annotation_text="%80", annotation_position="top left")
        st.plotly_chart(sade(fig, 400), width="stretch")
    with sag:
        mat = (abc.groupby(["abc_sinifi", "xyz_sinifi"]).size().unstack(fill_value=0)
               .reindex(index=list("ABC"), columns=list("XYZ"), fill_value=0))
        fig = go.Figure(go.Heatmap(
            z=mat.values, x=["X (düzenli)", "Y (dalgalı)", "Z (düzensiz)"], y=["A (hızlı)", "B (orta)", "C (yavaş)"],
            colorscale=[[0, "#cde2fb"], [0.5, "#3987e5"], [1, "#0d366b"]], xgap=2, ygap=2,
            text=mat.values, texttemplate="%{text}", showscale=False,
            hovertemplate="%{y} / %{x}: %{z} ürün<extra></extra>"))
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(title="ABC–XYZ matrisi (ürün sayısı)")
        st.plotly_chart(sade(fig, 400), width="stretch")

    bolge = abc.groupby(["onerilen_depo_bolgesi", "abc_sinifi"])["toplam_hacim_m3"].sum().reset_index()
    fig = px.bar(bolge, y="onerilen_depo_bolgesi", x="toplam_hacim_m3", color="abc_sinifi", orientation="h",
                 color_discrete_map=ABC_RENK, category_orders={"abc_sinifi": list("ABC")},
                 labels={"onerilen_depo_bolgesi": "", "toplam_hacim_m3": "Yıllık akış hacmi (m³, örneklem)",
                         "abc_sinifi": "ABC"},
                 title="Önerilen depo bölgelerine göre ürün akış hacmi")
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(sade(fig, 360), width="stretch")

    st.subheader("Ürün yerleşim önerileri")
    sinif_sec = st.segmented_control("ABC sınıfı", list("ABC"), selection_mode="multi", default=list("ABC"))
    tablo = abc[abc["abc_sinifi"].isin(sinif_sec or list("ABC"))].sort_values("hiz_sirasi")
    st.dataframe(
        tablo[["hiz_sirasi", "urun_id", "urun_adi", "kategori", "abc_xyz", "toplama_satiri_sayisi",
               "varyasyon_katsayisi", "coi", "onerilen_depo_bolgesi", "onerilen_raf_seviyesi", "yerlesim_gerekcesi"]],
        hide_index=True, width="stretch", height=380,
        column_config={
            "hiz_sirasi": "Sıra", "urun_id": "Ürün", "urun_adi": "Ürün adı", "kategori": "Kategori",
            "abc_xyz": "Sınıf", "toplama_satiri_sayisi": st.column_config.NumberColumn("Toplama satırı", format="%d"),
            "varyasyon_katsayisi": st.column_config.NumberColumn("CV", format="%.2f"),
            "coi": st.column_config.NumberColumn("COI", format="%.3f", help="Düşük COI → rampaya yakın"),
            "onerilen_depo_bolgesi": "Depo bölgesi", "onerilen_raf_seviyesi": "Raf seviyesi",
            "yerlesim_gerekcesi": "Gerekçe"})

# ---------------------------------------------------------------- 3) Mağaza dağıtımı
with sekme3:
    bdm = D["dim_dagitim_merkezi"].iloc[0]
    harita = magazalar.merge(plan[["magaza_id", "ort_haftalik_hacim_m3", "onerilen_arac_tipi",
                                   "haftalik_sevkiyat_sayisi", "haftalik_tasima_maliyeti_tl"]], on="magaza_id")
    fig = go.Figure()
    for rota in ROTA_SIRASI:
        r = harita[harita["rota_kumesi"] == rota]
        if r.empty:
            continue
        for _, m in r.iterrows():  # BDM -> mağaza bağlantı çizgileri
            fig.add_trace(go.Scattermap(lat=[bdm.enlem, m.enlem], lon=[bdm.boylam, m.boylam], mode="lines",
                                        line=dict(width=1, color=ROTA_RENK[rota]), opacity=0.45,
                                        hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scattermap(
            lat=r["enlem"], lon=r["boylam"], mode="markers", name=rota,
            marker=dict(size=(r["ort_haftalik_hacim_m3"] ** 0.5 * 3).clip(9, 30), color=ROTA_RENK[rota]),
            customdata=r[["magaza_adi", "il", "mesafe_km", "ort_haftalik_hacim_m3", "onerilen_arac_tipi",
                          "haftalik_sevkiyat_sayisi"]],
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Mesafe: %{customdata[2]} km"
                          "<br>Haftalık hacim: %{customdata[3]:.1f} m³<br>Araç: %{customdata[4]}"
                          " × %{customdata[5]}/hafta<extra></extra>"))
    fig.add_trace(go.Scattermap(lat=[bdm.enlem], lon=[bdm.boylam], mode="markers+text", name="BDM",
                                marker=dict(size=20, color="#0b0b0b"), text=["BDM"], textposition="top right",
                                hovertemplate=f"<b>{bdm.bdm_adi}</b><extra></extra>"))
    fig.update_layout(map=dict(style="carto-positron", center=dict(lat=38.2, lon=28.6), zoom=6.15),
                      title="Mağazalar, rota kümeleri ve haftalık hacim (balon büyüklüğü)")
    st.plotly_chart(sade(fig, 520), width="stretch")

    sol, sag = st.columns(2)
    with sol:
        pm = plan.sort_values("haftalik_tasima_maliyeti_tl")
        fig = px.bar(pm, x="haftalik_tasima_maliyeti_tl", y="magaza_adi", color="rota_kumesi", orientation="h",
                     color_discrete_map=ROTA_RENK, category_orders={"rota_kumesi": ROTA_SIRASI},
                     custom_data=["onerilen_arac_tipi", "haftalik_sevkiyat_sayisi", "mesafe_km"],
                     labels={"haftalik_tasima_maliyeti_tl": "Haftalık taşıma maliyeti (₺)", "magaza_adi": "",
                             "rota_kumesi": "Rota"},
                     title="Mağaza bazında haftalık taşıma maliyeti")
        fig.update_traces(marker_line_width=0, hovertemplate=(
            "<b>%{y}</b><br>₺%{x:,.0f}/hafta<br>%{customdata[0]} × %{customdata[1]} sefer"
            "<br>Mesafe: %{customdata[2]} km<extra></extra>"))
        st.plotly_chart(sade(fig, 640), width="stretch")
    with sag:
        arac = plan.groupby("onerilen_arac_tipi").agg(magaza=("magaza_id", "count"),
                                                      sefer=("haftalik_sevkiyat_sayisi", "sum")).reset_index()
        fig = px.bar(arac, x="onerilen_arac_tipi", y="sefer", text="magaza",
                     labels={"onerilen_arac_tipi": "", "sefer": "Haftalık sefer sayısı"},
                     title="Araç tipine göre haftalık sefer (etiket: mağaza sayısı)")
        fig.update_traces(marker_color=PALET[0], texttemplate="%{text} mağaza", textposition="outside",
                          hovertemplate="%{x}: %{y} sefer<extra></extra>")
        st.plotly_chart(sade(fig, 300), width="stretch")

        sec_mg = st.selectbox("Mağaza haftalık talep profili", harita["magaza_adi"].sort_values())
        mid = harita.loc[harita["magaza_adi"] == sec_mg, "magaza_id"].iloc[0]
        h = D["mart_magaza_haftalik_talep"]
        h = h[(h["magaza_id"] == mid) & h["tam_hafta_mi"]]
        p90 = plan.loc[plan["magaza_id"] == mid, "p90_haftalik_hacim_m3"].iloc[0]
        fig = px.line(h, x="hafta_baslangic", y="tahmini_toplam_hacim_m3",
                      labels={"hafta_baslangic": "Hafta", "tahmini_toplam_hacim_m3": "Tahmini hacim (m³)"},
                      title=f"{sec_mg}: haftalık talep ve P90 planlama seviyesi")
        fig.update_traces(line=dict(width=2, color=PALET[0]),
                          hovertemplate="%{x|%d.%m.%Y}: %{y:.1f} m³<extra></extra>")
        fig.add_hline(y=p90, line_dash="dot", line_color=PALET[1], annotation_text=f"P90 = {p90:.1f} m³")
        st.plotly_chart(sade(fig, 300), width="stretch")

    st.subheader("Önerilen dağıtım planı")
    st.dataframe(
        plan[["magaza_id", "magaza_adi", "il", "magaza_tipi", "rota_kumesi", "mesafe_km", "surus_suresi_dk",
              "ort_haftalik_hacim_m3", "p90_haftalik_hacim_m3", "onerilen_arac_tipi", "haftalik_sevkiyat_sayisi",
              "onerilen_sevkiyat_gunleri", "ort_arac_doluluk_orani", "baglayici_kisit", "haftalik_tasima_maliyeti_tl"]]
        .sort_values(["rota_kumesi", "mesafe_km"]),
        hide_index=True, width="stretch",
        column_config={
            "magaza_id": "Mağaza", "magaza_adi": "Ad", "il": "İl", "magaza_tipi": "Tip", "rota_kumesi": "Rota",
            "mesafe_km": st.column_config.NumberColumn("Mesafe (km)", format="%.0f"),
            "surus_suresi_dk": st.column_config.NumberColumn("Süre (dk)", format="%.0f"),
            "ort_haftalik_hacim_m3": st.column_config.NumberColumn("Ort. hacim (m³/hf)", format="%.1f"),
            "p90_haftalik_hacim_m3": st.column_config.NumberColumn("P90 hacim (m³/hf)", format="%.1f"),
            "onerilen_arac_tipi": "Araç", "haftalik_sevkiyat_sayisi": "Sefer/hafta",
            "onerilen_sevkiyat_gunleri": "Günler",
            "ort_arac_doluluk_orani": st.column_config.ProgressColumn("Ort. doluluk", min_value=0, max_value=1,
                                                                     format="percent"),
            "baglayici_kisit": "Bağlayıcı kısıt",
            "haftalik_tasima_maliyeti_tl": st.column_config.NumberColumn("Maliyet (₺/hf)", format="%.0f")})

# ---------------------------------------------------------------- 4) Veri ve yöntem
with sekme4:
    st.markdown(f"""
**İş sorusu:** Ege BDM'de hangi ürün hangi depo bölgesine yerleştirilmeli ve her mağazaya hangi araçla,
haftada kaç kez sevkiyat yapılmalı ki toplama verimliliği artsın ve taşıma maliyeti düşsün?

**Veri kaynakları**
- **NovaPerakende** (perakende_satis, sepet, musteri + ürün/mağaza ana verisi). *Şu an sentetik test verisidir*
  (`scripts/generate_nova_test_data.py`); gerçek veri geldiğinde `data/raw/` değiştirilir.
- **TÜİK ADNKS 2023** il nüfusları: talep yoğunluğu ve mağaza dağılımı için.
- **OSRM açık rota API'si** (OpenStreetMap): BDM → mağaza karayolu mesafe/süreleri
  (kaynak: `{magazalar['mesafe_kaynagi'].iloc[0]}`).

**Yöntem**
- *ABC*: ürünün BDM'de yer aldığı (mağaza, gün) sipariş sayısı = toplama satırı; kümülatif %80 → A, %95 → B.
- *XYZ*: tam haftalardaki haftalık satış adedinin varyasyon katsayısı; ≤0,5 → X, ≤1,0 → Y, üstü → Z.
- *COI* (Cube-per-Order Index): haftalık raf hacmi / haftalık toplama; düşük COI rampaya yakın yerleştirilir.
- *Dağıtım planı*: haftalık talebin P90 değerini %85 hedef doluluğu aşmadan karşılayan, en düşük haftalık
  maliyetli (sabit sefer maliyeti + 2 × mesafe × km maliyeti) araç/sıklık kombinasyonu; en az 2 sevkiyat/hafta.
  Tır küçük mağazalara atanmaz.
- Veri, mağaza işlemlerinin örneklemidir; hacimler `talep_olcek_katsayisi` (dbt var) ile ölçeklenir.

**Sınırlılıklar:** Doğrudan (tek duraklı) sefer varsayımı; çok duraklı rota optimizasyonu (VRP) Bölüm 2'de ele
alınabilir. Araç maliyetleri yaklaşık değerlerdir.
""")
