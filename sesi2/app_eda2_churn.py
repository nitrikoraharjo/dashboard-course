# sesi2/app_eda2_churn.py — EDA interaktif + jawaban Latihan Mandiri Sesi 2
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="EDA Churn", page_icon="🔎", layout="wide")

STATUS = {"Bertahan": "#2a78d6", "Churn": "#eb6834"}
KATEGORI = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e87ba4"]
KONTRAK = ["Bulanan", "Tahunan", "Dua Tahun"]


@st.cache_data
def load_data():
    df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
    df["total_charges_missing"] = df["total_charges"].isna()  # catat sebelum imputasi
    df["total_charges"] = df["total_charges"].fillna(df["total_charges"].median())
    df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
    df["kelompok_tenure"] = pd.cut(
        df["tenure_months"], [0, 12, 24, 48, 72], labels=["0-12", "13-24", "25-48", "49-72"]
    ).astype(str)
    return df


def gaya(fig, tinggi=360):
    fig.update_layout(
        template="plotly_white",
        height=tinggi,
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=15,
        legend_title_text="",
    )
    return fig


df = load_data()

st.title("🔎 Exploratory Data Analysis — Customer Churn")
st.caption("Data latihan sintetis · 3.000 pelanggan · pendaftaran Januari 2023 – Desember 2025")

# ---------- KPI CARDS ----------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total pelanggan", f"{len(df):,}")
k2.metric("Churn rate", f"{df.churn.mean():.1%}")
k3.metric("Rata-rata tagihan", f"Rp{df.monthly_charges.mean():,.0f}".replace(",", "."))
k4.metric("Rata-rata tenure", f"{df.tenure_months.mean():.1f} bln")
k5.metric("Missing total_charges", f"{df.total_charges_missing.sum()} baris", help="Diisi median")

tab = st.tabs([
    "🥧 Komposisi", "📊 Perbandingan", "📈 Distribusi", "⏱️ Tren", "🔗 Hubungan", "📋 Data",
    "📣 Keluhan",  # LATIHAN 5: tab ketujuh
])

# ---------- 1. KOMPOSISI: pie, donut, treemap ----------
with tab[0]:
    c1, c2 = st.columns(2)
    pie = px.pie(
        df, names="status", color="status", color_discrete_map=STATUS,
        title="Satu dari tiga pelanggan churn",
    )
    pie.update_traces(textinfo="percent+label", textfont_size=14)
    c1.plotly_chart(gaya(pie), width="stretch")

    donut = px.pie(
        df, names="contract_type", hole=0.55, color_discrete_sequence=KATEGORI,
        category_orders={"contract_type": KONTRAK},
        title="Separuh pelanggan berkontrak bulanan",
    )
    donut.update_traces(textinfo="percent+label")
    donut.add_annotation(text=f"<b>{len(df):,}</b><br>pelanggan", showarrow=False, font_size=16)
    c2.plotly_chart(gaya(donut), width="stretch")

    tm = df.groupby(["region", "segment"], as_index=False).agg(
        pelanggan=("customer_id", "count"), churn_rate=("churn", "mean")
    )
    tree = px.treemap(
        tm, path=["region", "segment"], values="pelanggan", color="churn_rate",
        color_continuous_scale="Oranges",
        title="Treemap: luas = jumlah pelanggan, warna = churn rate",
    )
    st.plotly_chart(gaya(tree, 420), width="stretch")

    # ===== LATIHAN 1: pie internet_service, donut region, lalu bar horizontal terurut =====
    st.divider()
    st.subheader("Latihan 1 — Pie/donut vs bar horizontal terurut")
    c1, c2 = st.columns(2)
    pie_inet = px.pie(
        df, names="internet_service", color_discrete_sequence=KATEGORI,
        title="Pie: komposisi internet_service (3 kategori)",
    )
    pie_inet.update_traces(textinfo="percent+label")
    c1.plotly_chart(gaya(pie_inet), width="stretch")

    donut_region = px.pie(
        df, names="region", hole=0.55, color_discrete_sequence=KATEGORI,
        title="Donut: komposisi region (5 kategori)",
    )
    donut_region.update_traces(textinfo="percent+label")
    c2.plotly_chart(gaya(donut_region), width="stretch")

    c3, c4 = st.columns(2)
    for kol, wadah in [("internet_service", c3), ("region", c4)]:
        komposisi = df[kol].value_counts(normalize=True).sort_values().reset_index(name="proporsi")
        bar_kom = px.bar(
            komposisi, x="proporsi", y=kol, orientation="h", text_auto=".1%",
            color_discrete_sequence=["#2a78d6"], title=f"Bar terurut: komposisi {kol}",
        )
        bar_kom.update_xaxes(tickformat=".0%")
        bar_kom.update_layout(yaxis_title="")
        wadah.plotly_chart(gaya(bar_kom), width="stretch")

    st.info(
        "**Kesimpulan:** untuk 5 kategori (region), **bar horizontal terurut lebih mudah dibaca**. "
        "Mata manusia lebih akurat membandingkan panjang batang daripada sudut/luas irisan, dan "
        "urutan dari kecil ke besar langsung memperlihatkan peringkat. Pada donut, irisan yang "
        "ukurannya mirip (Sulawesi 14%, Kalimantan 11%, Bali-Nusa Tenggara 10%) sulit dibedakan. "
        "Pie masih cukup untuk 2–3 kategori seperti internet_service."
    )

# ---------- 2. PERBANDINGAN: bar, grouped bar, stacked 100% ----------
with tab[1]:
    kolom = st.selectbox(
        "Bandingkan churn rate berdasarkan",
        ["contract_type", "region", "segment", "payment_method", "internet_service"],
    )
    rk = (
        df.groupby(kolom, as_index=False)
        .agg(pelanggan=("customer_id", "count"), churn_rate=("churn", "mean"))
        .sort_values("churn_rate")
    )
    bar = px.bar(
        rk, x="churn_rate", y=kolom, orientation="h", text_auto=".1%",
        color_discrete_sequence=["#eb6834"], title=f"Churn rate per {kolom}",
    )
    bar.add_vline(x=df.churn.mean(), line_dash="dot", annotation_text="rata-rata")
    bar.update_xaxes(tickformat=".0%")

    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(gaya(bar), width="stretch")
    c2.dataframe(
        rk.sort_values("churn_rate", ascending=False)
        .style.format({"churn_rate": "{:.1%}"})
        .background_gradient(subset=["churn_rate"], cmap="Oranges"),
        width="stretch",
        hide_index=True,
    )
    # ===== LATIHAN 6: unduh tabel ringkasan sebagai CSV =====
    c2.download_button(
        "⬇️ Unduh tabel ringkasan (CSV)",
        data=rk.sort_values("churn_rate", ascending=False).to_csv(index=False).encode("utf-8"),
        file_name=f"ringkasan_churn_per_{kolom}.csv",
        mime="text/csv",
    )

    c3, c4 = st.columns(2)
    gb = df.groupby(["contract_type", "segment"], as_index=False)["churn"].mean()
    grouped = px.bar(
        gb, x="contract_type", y="churn", color="segment", barmode="group",
        color_discrete_sequence=KATEGORI, category_orders={"contract_type": KONTRAK},
        title="Grouped bar: kontrak × segmen",
    )
    grouped.update_yaxes(tickformat=".0%")
    c3.plotly_chart(gaya(grouped), width="stretch")

    stacked = px.histogram(
        df, y="payment_method", color="status", barnorm="percent",
        color_discrete_map=STATUS, title="Stacked bar 100%: status per pembayaran",
    )
    stacked.update_layout(xaxis_title="Proporsi (%)", yaxis_title="")
    c4.plotly_chart(gaya(stacked), width="stretch")

    # ===== LATIHAN 2: stacked bar 100% status churn per internet_service =====
    st.divider()
    st.subheader("Latihan 2 — Stacked bar 100% status churn per internet_service")
    stacked_inet = px.histogram(
        df, y="internet_service", color="status", barnorm="percent", text_auto=".1f",
        color_discrete_map=STATUS, title="Stacked bar 100%: status churn per internet_service",
    )
    stacked_inet.update_layout(xaxis_title="Proporsi (%)", yaxis_title="")
    st.plotly_chart(gaya(stacked_inet), width="stretch")

# ---------- 3. DISTRIBUSI: histogram, box, violin ----------
with tab[2]:
    num = st.selectbox(
        "Variabel numerik", ["tenure_months", "monthly_charges", "num_complaints", "support_calls"]
    )
    c1, c2 = st.columns(2)
    hist = px.histogram(
        df, x=num, color="status", barmode="overlay", opacity=0.7, nbins=30,
        color_discrete_map=STATUS, marginal="box", title=f"Histogram {num}",
    )
    c1.plotly_chart(gaya(hist, 400), width="stretch")

    vio = px.violin(
        df, x="contract_type", y=num, color="contract_type", box=True,
        color_discrete_sequence=KATEGORI, category_orders={"contract_type": KONTRAK},
        title=f"Violin {num} per kontrak",
    )
    c2.plotly_chart(gaya(vio, 400), width="stretch")

    # ===== LATIHAN 3: box plot support_calls berdasarkan status churn =====
    st.divider()
    st.subheader("Latihan 3 — Box plot support_calls per status churn")
    box = px.box(
        df, x="status", y="support_calls", color="status", points="outliers",
        color_discrete_map=STATUS, category_orders={"status": ["Bertahan", "Churn"]},
        title="Distribusi support_calls: Bertahan vs Churn",
    )
    st.plotly_chart(gaya(box, 400), width="stretch")

# ---------- 4. TREN: line, area ----------
with tab[3]:
    bulanan = (
        df.set_index("signup_date").resample("ME")["customer_id"].count()
        .rename("pelanggan").reset_index()
    )
    bulanan["rata2_3bln"] = bulanan["pelanggan"].rolling(3).mean()
    line = px.line(
        bulanan, x="signup_date", y=["pelanggan", "rata2_3bln"], markers=True,
        color_discrete_sequence=["#9dbbe6", "#2a78d6"],
        title="Pelanggan baru per bulan dan rata-rata bergerak 3 bulan",
    )
    st.plotly_chart(gaya(line), width="stretch")

    c1, c2 = st.columns(2)
    kt = df.groupby("kelompok_tenure", as_index=False)["churn"].mean()
    lt = px.line(
        kt, x="kelompok_tenure", y="churn", markers=True,
        text=kt["churn"].map("{:.1%}".format),
        color_discrete_sequence=["#eb6834"], title="Churn rate per kelompok tenure",
    )
    lt.update_traces(textposition="top center", marker_size=10)
    lt.update_yaxes(tickformat=".0%", range=[0, 0.65])
    c1.plotly_chart(gaya(lt), width="stretch")

    q = (
        df.assign(kuartal=df.signup_date.dt.to_period("Q").astype(str))
        .groupby(["kuartal", "segment"], as_index=False)["customer_id"].count()
    )
    area = px.area(
        q, x="kuartal", y="customer_id", color="segment",
        color_discrete_sequence=KATEGORI, title="Area: pelanggan baru per kuartal",
    )
    c2.plotly_chart(gaya(area), width="stretch")

    # ===== LATIHAN 4: line chart churn rate per kuartal pendaftaran =====
    st.divider()
    st.subheader("Latihan 4 — Churn rate per kuartal pendaftaran")
    churn_q = (
        df.assign(kuartal=df.signup_date.dt.to_period("Q").astype(str))
        .groupby("kuartal", as_index=False)
        .agg(pelanggan=("customer_id", "count"), churn_rate=("churn", "mean"))
    )
    line_q = px.line(
        churn_q, x="kuartal", y="churn_rate", markers=True,
        text=churn_q["churn_rate"].map("{:.0%}".format), hover_data=["pelanggan"],
        color_discrete_sequence=["#eb6834"], title="Churn rate per kuartal pendaftaran",
    )
    line_q.update_traces(textposition="top center")
    line_q.add_hline(y=df.churn.mean(), line_dash="dot", annotation_text="rata-rata")
    line_q.update_yaxes(tickformat=".0%", rangemode="tozero")
    st.plotly_chart(gaya(line_q, 380), width="stretch")

# ---------- 5. HUBUNGAN: scatter, heatmap ----------
with tab[4]:
    c1, c2 = st.columns(2)
    sc = px.scatter(
        df, x="tenure_months", y="monthly_charges", color="status", opacity=0.55,
        color_discrete_map=STATUS, hover_name="customer_id",
        hover_data=["contract_type", "num_complaints"], title="Tenure vs tagihan",
    )
    c1.plotly_chart(gaya(sc, 420), width="stretch")

    corr = df[["tenure_months", "monthly_charges", "num_complaints", "support_calls", "churn"]].corr()
    hm = px.imshow(
        corr.round(2), text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Heatmap korelasi",
    )
    c2.plotly_chart(gaya(hm, 420), width="stretch")

    pv = pd.pivot_table(df, values="churn", index="region", columns="segment", aggfunc="mean")
    hm2 = px.imshow(
        pv * 100, text_auto=".1f", color_continuous_scale="Oranges",
        labels={"color": "Churn (%)"}, title="Heatmap churn rate region × segmen (%)",
    )
    st.plotly_chart(gaya(hm2, 360), width="stretch")

# ---------- 6. DATA: profil + tabel ----------
with tab[5]:
    profil = pd.DataFrame({
        "tipe": df.dtypes.astype(str),
        "missing": df.isna().sum().where(df.columns != "total_charges", df.total_charges_missing.sum()),
        "unik": df.nunique(),
    }).reset_index(names="kolom")

    c1, c2 = st.columns([2, 3])
    c1.markdown("**Profil kolom**")
    c1.dataframe(profil, width="stretch", hide_index=True)
    c2.markdown("**Statistik deskriptif**")
    c2.dataframe(df.describe(include="number").T.round(1), width="stretch")

    st.markdown("**10 baris pertama**")
    st.dataframe(df.head(10), width="stretch", hide_index=True)

# ---------- 7. KELUHAN (LATIHAN 5): churn rate per jumlah keluhan ----------
with tab[6]:
    st.subheader("Latihan 5 — Churn rate per jumlah keluhan")
    # Keluhan 5, 6, 7 hanya dimiliki 31 pelanggan -> digabung jadi "5+" agar churn rate tidak menyesatkan
    keluhan = (
        df.assign(keluhan=df["num_complaints"].clip(upper=5).astype(str).replace("5", "5+"))
        .groupby("keluhan", as_index=False)
        .agg(pelanggan=("customer_id", "count"), churn_rate=("churn", "mean"))
    )
    bar_kel = px.bar(
        keluhan, x="keluhan", y="churn_rate", text_auto=".1%", hover_data=["pelanggan"],
        color_discrete_sequence=["#eb6834"], title="Churn rate per jumlah keluhan",
        labels={"keluhan": "Jumlah keluhan", "churn_rate": "Churn rate"},
    )
    bar_kel.add_hline(y=df.churn.mean(), line_dash="dot", annotation_text="rata-rata")
    bar_kel.update_yaxes(tickformat=".0%")

    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(gaya(bar_kel, 400), width="stretch")
    c2.dataframe(keluhan.style.format({"churn_rate": "{:.1%}"}), width="stretch", hide_index=True)
    c2.caption('Keluhan ≥ 5 digabung menjadi "5+" karena jumlah pelanggannya sangat sedikit.')
