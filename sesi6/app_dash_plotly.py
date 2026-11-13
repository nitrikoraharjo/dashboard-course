# sesi6/app_dash_plotly.py — menampilkan chart Plotly di aplikasi Dash
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "customer_churn.csv", parse_dates=["signup_date"])
df["status"] = df["churn"].map({0: "Bertahan", 1: "Churn"})
WARNA = {"Bertahan": "#4C72B0", "Churn": "#C44E52"}

hist = px.histogram(df, x="tenure_months", color="status", nbins=36, barmode="overlay",
                    opacity=0.7, color_discrete_map=WARNA, template="plotly_white",
                    labels={"tenure_months": "Tenure (bulan)", "status": "Status"},
                    title="Churn terkonsentrasi pada tenure pendek")

# LATIHAN 2: scatter diubah menjadi bubble chart — ukuran titik = jumlah panggilan ke CS
# 332 pelanggan punya support_calls = 0; gelembung berukuran 0 tidak terlihat,
# jadi ukuran memakai support_calls + 1 (nilai asli tetap tampil di hover).
df["ukuran_bubble"] = df["support_calls"] + 1
scatter = px.scatter(df, x="tenure_months", y="monthly_charges", color="status",
                     size="ukuran_bubble", size_max=14,
                     color_discrete_map=WARNA, opacity=0.55, template="plotly_white",
                     hover_name="customer_id",
                     hover_data={"region": True, "contract_type": True, "num_complaints": True,
                                 "support_calls": True, "ukuran_bubble": False},
                     labels={"tenure_months": "Tenure (bulan)", "monthly_charges": "Tagihan (Rp)",
                             "support_calls": "Panggilan CS"},
                     title="Bubble: ukuran = panggilan ke CS")

# Filter visual tanpa callback: tombol dropdown bawaan Plotly (updatemenus)
bar_df = df.groupby(["region", "contract_type"], as_index=False)["churn"].mean()
bar = px.bar(bar_df, x="region", y="churn", color="contract_type", barmode="group",
             template="plotly_white", labels={"churn": "Churn rate", "region": "Region",
                                              "contract_type": "Kontrak"},
             title="Churn rate per region dan kontrak")
# PERBAIKAN: px.bar memberi tiap kontrak "offsetgroup" sendiri, sehingga batang selalu
# berdampingan dan tombol Stacked tidak berefek. Hapus offsetgroup agar barmode bisa diganti.
bar.update_traces(offsetgroup=None)
bar.update_yaxes(tickformat=".0%")
bar.update_layout(updatemenus=[dict(type="buttons", direction="right", x=1, y=1.15, buttons=[
    dict(label="Grouped", method="relayout", args=[{"barmode": "group"}]),
    dict(label="Stacked", method="relayout", args=[{"barmode": "stack"}]),
])])

# ================= LATIHAN MANDIRI SESI 6 =================
rata_nasional = df["churn"].mean()

# LATIHAN 1: bar horizontal churn rate per payment_method, tertinggi di atas + garis rata-rata
pay = df.groupby("payment_method", as_index=False)["churn"].mean().sort_values("churn")
bar_pay = px.bar(pay, x="churn", y="payment_method", orientation="h", text_auto=".1%",
                 color_discrete_sequence=["#C44E52"], template="plotly_white",
                 labels={"churn": "Churn rate", "payment_method": ""},
                 title="Churn rate per metode pembayaran")
bar_pay.add_vline(x=rata_nasional, line_dash="dot", line_color="#555",
                  annotation_text=f"rata-rata nasional {rata_nasional:.1%}",
                  annotation_position="top")
bar_pay.update_xaxes(tickformat=".0%")

# LATIHAN 3: sunburst jumlah pelanggan region -> segmen -> kontrak
sun_df = df.groupby(["region", "segment", "contract_type"], as_index=False)["customer_id"].count()
sun_df = sun_df.rename(columns={"customer_id": "pelanggan"})
sunburst = px.sunburst(sun_df, path=["region", "segment", "contract_type"], values="pelanggan",
                       color_discrete_sequence=px.colors.qualitative.Set2,
                       title="Sunburst: jumlah pelanggan region → segmen → kontrak")
sunburst.update_traces(textinfo="label+percent parent")
sunburst.update_layout(height=520, margin=dict(t=60, l=10, r=10, b=10))

# LATIHAN 4: gauge churn rate keseluruhan
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=rata_nasional * 100,
    number={"suffix": "%", "valueformat": ".1f"},
    title={"text": "Churn rate keseluruhan"},
    gauge={
        "axis": {"range": [0, 100], "ticksuffix": "%"},
        "bar": {"color": "#C44E52"},
        "steps": [{"range": [0, 30], "color": "#e3f1e8"},
                  {"range": [30, 60], "color": "#fdf0d5"},
                  {"range": [60, 100], "color": "#fbe1e1"}],
    },
))
gauge.update_layout(template="plotly_white", height=360, margin=dict(t=80, l=30, r=30, b=10))

CARA_BACA_SUNBURST = [
    html.H3("Cara membaca sunburst"),
    html.Ul([
        html.Li("Lingkaran dibaca dari dalam ke luar: cincin dalam = region, "
                "cincin tengah = segmen, cincin luar = jenis kontrak."),
        html.Li("Besar sudut irisan sebanding dengan jumlah pelanggan. "
                f"Irisan Jawa paling besar karena berisi {(df.region == 'Jawa').sum():,} "
                f"dari {len(df):,} pelanggan."),
        html.Li("Persentase pada label adalah porsi terhadap induknya (percent parent), "
                "misalnya porsi kontrak Bulanan di dalam segmen Retail wilayah Jawa."),
        html.Li("Klik satu irisan untuk zoom ke kelompok itu; klik bagian tengah untuk kembali."),
        html.Li("Arahkan kursor untuk melihat jumlah pelanggan pada setiap irisan."),
    ]),
]

app = Dash(__name__, title="Plotly di Dash")
app.layout = html.Div(style={"maxWidth": "1150px", "margin": "auto", "fontFamily": "Arial"}, children=[
    html.H1("Interactive Visualization with Plotly"),
    html.P("Arahkan kursor (hover), zoom dengan drag, double-click untuk reset, klik legenda untuk filter."),
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}, children=[
        dcc.Graph(figure=hist), dcc.Graph(figure=scatter)]),
    dcc.Graph(figure=bar, config={"displaylogo": False,
                                  "toImageButtonOptions": {"format": "png", "scale": 2}}),

    # ---------- LATIHAN MANDIRI SESI 6 ----------
    html.Hr(),
    html.H2("Latihan mandiri Sesi 6"),
    html.Div(style={"display": "grid", "gridTemplateColumns": "3fr 2fr", "gap": "12px"}, children=[
        dcc.Graph(figure=bar_pay),   # Latihan 1
        dcc.Graph(figure=gauge),     # Latihan 4
    ]),
    html.Div(style={"display": "grid", "gridTemplateColumns": "3fr 2fr", "gap": "12px",
                    "alignItems": "center"}, children=[
        dcc.Graph(figure=sunburst),  # Latihan 3
        html.Div(CARA_BACA_SUNBURST, style={"fontSize": "15px", "lineHeight": "1.6"}),
    ]),
])

if __name__ == "__main__":
    
    app.run(debug=False, port=8051)
