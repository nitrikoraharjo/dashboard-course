# vercel_dash/app_dash_callback.py — salinan sesi7/app_dash_callback.py untuk deploy Vercel
# Sistem callback Dash: filter -> KPI, chart, tabel

from pathlib import Path

import pandas as pd
import plotly.express as px

from dash import (
    Dash,
    html,
    dcc,
    dash_table,
    Input,
    Output,
    State,
    callback,
    ctx,
    no_update
)

from dash.exceptions import PreventUpdate


# ==================================================
# 1. LOAD DATA
# ==================================================

# Versi Vercel: folder data ada di samping file ini (vercel_dash/data)
ROOT = Path(__file__).resolve().parent

df = pd.read_csv(
    ROOT / "data" / "customer_churn.csv",
    parse_dates=["signup_date"]
)

df["status"] = df["churn"].map({
    0: "Bertahan",
    1: "Churn"
})


# ==================================================
# 2. KONFIGURASI
# ==================================================

WARNA = {
    "Bertahan": "#4C72B0",
    "Churn": "#C44E52"
}

KARTU = {
    "flex": 1,
    "padding": "14px",
    "borderRadius": "10px",
    "background": "#F4F6FA",
    "textAlign": "center"
}

TABEL_COLS = [
    "customer_id",
    "region",
    "segment",
    "contract_type",
    "tenure_months",
    "monthly_charges",
    "num_complaints",
    "status"
]

# LATIHAN 1: daftar layanan internet untuk checklist
LAYANAN = sorted(df.internet_service.unique())

# LATIHAN 4: kolom yang disimpan di dcc.Store (cukup yang dipakai KPI, chart, tabel)
STORE_COLS = TABEL_COLS + ["churn", "internet_service"]


# ==================================================
# 3. MEMBUAT APLIKASI DASH
# ==================================================

app = Dash(
    __name__,
    title="Dash Callback"
)


# ==================================================
# 4. LAYOUT DASHBOARD
# ==================================================

app.layout = html.Div(
    style={
        "maxWidth": "1200px",
        "margin": "auto",
        "fontFamily": "Arial"
    },
    children=[

        html.H1(
            "Dash Callback System — Dashboard Churn"
        ),

        # ------------------------------------------
        # PANEL FILTER
        # ------------------------------------------

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr 1fr",
                "gap": "16px"
            },
            children=[

                # Filter Region
                html.Div([
                    html.Label("Region"),

                    dcc.Dropdown(
                        id="dd-region",
                        options=sorted(df.region.unique()),
                        multi=True,
                        placeholder="Semua region"
                    )
                ]),

                # Filter Segment
                html.Div([
                    html.Label(
                        "Segmen (opsi bergantung region)"
                    ),

                    dcc.Dropdown(
                        id="dd-segment",
                        multi=True,
                        placeholder="Semua segmen"
                    )
                ]),

                # Filter Jenis Kontrak
                html.Div([
                    html.Label("Jenis kontrak"),

                    dcc.RadioItems(
                        id="rd-kontrak",
                        inline=True,
                        value="Semua",
                        options=[
                            "Semua",
                            "Bulanan",
                            "Tahunan",
                            "Dua Tahun"
                        ]
                    )
                ])

            ]
        ),

        # ------------------------------------------
        # LATIHAN 1: FILTER LAYANAN INTERNET (CHECKLIST)
        # ------------------------------------------

        html.Div(
            style={
                "marginTop": "12px"
            },
            children=[

                html.Label("Layanan internet"),

                dcc.Checklist(
                    id="ck-internet",
                    options=LAYANAN,
                    value=LAYANAN,
                    inline=True,
                    inputStyle={
                        "marginRight": "4px",
                        "marginLeft": "12px"
                    }
                )

            ]
        ),

        # ------------------------------------------
        # FILTER TENURE
        # ------------------------------------------

        html.Div(
            style={
                "marginTop": "12px"
            },
            children=[

                html.Label("Tenure (bulan)"),

                dcc.RangeSlider(
                    id="rs-tenure",
                    min=1,
                    max=72,
                    step=1,
                    value=[1, 72],
                    marks={
                        i: str(i)
                        for i in (
                            1, 12, 24, 36, 48, 60, 72
                        )
                    }
                )

            ]
        ),

        # ------------------------------------------
        # FILTER JUMLAH KELUHAN
        # ------------------------------------------

        html.Div(
            style={
                "display": "flex",
                "gap": "8px",
                "alignItems": "center"
            },
            children=[

                html.Label(
                    "Minimal jumlah keluhan:"
                ),

                dcc.Input(
                    id="in-keluhan",
                    type="number",
                    min=0,
                    max=10,
                    value=0,
                    style={
                        "width": "70px"
                    }
                ),

                html.Button(
                    "Terapkan",
                    id="btn-terapkan",
                    n_clicks=0
                ),

                html.Button(
                    "Reset filter",
                    id="btn-reset",
                    n_clicks=0
                ),

                html.Span(
                    id="info-keluhan",
                    style={
                        "color": "#666"
                    }
                )

            ]
        ),

        # Menyimpan nilai filter keluhan
        dcc.Store(
            id="store-keluhan",
            data=0
        ),

        # LATIHAN 4: menyimpan DataFrame hasil filter (format records)
        dcc.Store(
            id="store-data"
        ),

        # ------------------------------------------
        # KPI DASHBOARD
        # ------------------------------------------

        html.Div(
            id="kpi",
            style={
                "display": "flex",
                "gap": "12px",
                "margin": "16px 0"
            }
        ),

        # ------------------------------------------
        # CHART DASHBOARD
        # ------------------------------------------

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "12px"
            },
            children=[

                dcc.Graph(
                    id="g-bar"
                ),

                dcc.Graph(
                    id="g-scatter"
                ),

                # LATIHAN 2: histogram tenure yang ikut terfilter
                dcc.Graph(
                    id="g-hist"
                ),

                # LATIHAN 3: detail pelanggan saat titik scatter diklik
                html.Div(
                    id="detail-pelanggan",
                    style={
                        **KARTU,
                        "textAlign": "left",
                        "alignSelf": "center"
                    }
                )

            ]
        ),

        html.P(
            "Tip: klik salah satu batang region "
            "untuk memfilter tabel di bawah. "
            "Klik titik scatter untuk melihat detail pelanggan; "
            "drag kotak/lasso di scatter untuk memfilter tabel "
            "(double-click untuk batal).",
            style={
                "color": "#666"
            }
        ),

        # ------------------------------------------
        # TABEL DETAIL PELANGGAN
        # ------------------------------------------

        html.H3(
            id="judul-tabel"
        ),

        dash_table.DataTable(
            id="tbl",
            page_size=10,
            sort_action="native",

            columns=[
                {
                    "name": c,
                    "id": c
                }
                for c in TABEL_COLS
            ],

            style_cell={
                "padding": "6px",
                "textAlign": "left"
            },

            style_header={
                "fontWeight": "bold",
                "background": "#E9EDF5"
            },

            style_data_conditional=[
                {
                    "if": {
                        "filter_query": (
                            "{status} = 'Churn'"
                        )
                    },
                    "backgroundColor": "#FBE9EA"
                }
            ]
        )

    ]
)


# ==================================================
# 5. FUNGSI FILTER DATA
# ==================================================

def filter_df(
    region,
    segment,
    kontrak,
    tenure,
    min_keluhan,
    internet
):

    d = df

    if region:
        d = d[
            d.region.isin(region)
        ]

    if segment:
        d = d[
            d.segment.isin(segment)
        ]

    if kontrak and kontrak != "Semua":
        d = d[
            d.contract_type == kontrak
        ]

    # LATIHAN 1: filter layanan internet
    # (checklist kosong = tidak ada layanan dipilih = data kosong)
    d = d[
        d.internet_service.isin(internet or [])
    ]

    d = d[
        d.tenure_months.between(
            tenure[0],
            tenure[1]
        )
    ]

    return d[
        d.num_complaints >= (min_keluhan or 0)
    ]


def dari_store(records):
    # LATIHAN 4: mengubah isi store kembali menjadi DataFrame
    return pd.DataFrame(
        records or [],
        columns=STORE_COLS
    )


# ==================================================
# 6. CALLBACK PERTAMA
# Update opsi segment berdasarkan region
# ==================================================

@callback(
    Output("dd-segment", "options"),
    Input("dd-region", "value")
)
def update_segment_options(region):

    d = df[df.region.isin(region)] if region else df

    return sorted(
        d.segment.unique()
    )


# ==================================================
# 7. CALLBACK KEDUA
# Terapkan dan reset filter keluhan
# ==================================================

@callback(
    Output("store-keluhan", "data"),
    Output("in-keluhan", "value"),
    Output("dd-region", "value"),
    Output("dd-segment", "value"),
    Output("rd-kontrak", "value"),
    Output("rs-tenure", "value"),
    Output("ck-internet", "value"),

    Input("btn-terapkan", "n_clicks"),
    Input("btn-reset", "n_clicks"),

    State("in-keluhan", "value"),

    prevent_initial_call=True
)
def terapkan_atau_reset(
    n_apply,
    n_reset,
    nilai
):

    if ctx.triggered_id == "btn-reset":

        return (
            0,
            0,
            None,
            None,
            "Semua",
            [1, 72],
            LAYANAN
        )

    if nilai is None:
        raise PreventUpdate

    # Input kosong: jangan ubah nilai lainnya
    return (
        nilai,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update
    )


# ==================================================
# 7b. LATIHAN 4: SIMPAN HASIL FILTER KE dcc.Store
# filter_df() cukup dijalankan sekali di sini
# ==================================================

@callback(
    Output("store-data", "data"),

    Input("dd-region", "value"),
    Input("dd-segment", "value"),
    Input("rd-kontrak", "value"),
    Input("rs-tenure", "value"),
    Input("store-keluhan", "data"),
    Input("ck-internet", "value")
)
def simpan_filter(
    region,
    segment,
    kontrak,
    tenure,
    min_keluhan,
    internet
):

    d = filter_df(
        region,
        segment,
        kontrak,
        tenure,
        min_keluhan,
        internet
    )

    return d[STORE_COLS].to_dict("records")


# ==================================================
# 8. CALLBACK KETIGA
# Update KPI dan chart dashboard
# ==================================================

@callback(
    Output("kpi", "children"),
    Output("g-bar", "figure"),
    Output("g-scatter", "figure"),
    Output("info-keluhan", "children"),
    Output("g-hist", "figure"),          # LATIHAN 2: output kelima

    Input("store-data", "data"),
    State("store-keluhan", "data")
)
def update_dashboard(
    records,
    min_keluhan
):

    d = dari_store(records)

    info = (
        f"Filter keluhan aktif: ≥ {min_keluhan}"
    )

    # Jika data kosong
    if d.empty:

        kosong = px.scatter(
            title="Tidak ada data untuk filter ini"
        )

        return (
            [
                html.Div(
                    "Data kosong",
                    style=KARTU
                )
            ],
            kosong,
            kosong,
            info,
            kosong
        )

    # ------------------------------------------
    # Fungsi membuat kartu KPI
    # ------------------------------------------

    def kartu(j, v):

        return html.Div(
            [
                html.Small(j),

                html.H2(
                    v,
                    style={
                        "margin": "4px 0"
                    }
                )
            ],
            style=KARTU
        )

    # ------------------------------------------
    # Menghitung KPI
    # ------------------------------------------

    kpi = [

        kartu(
            "Pelanggan",
            f"{len(d):,}"
        ),

        kartu(
            "Churn rate",
            f"{d.churn.mean():.1%}"
        ),

        kartu(
            "Rata-rata tagihan",
            f"Rp{d.monthly_charges.mean():,.0f}".replace(
                ",", "."
            )
        ),

        kartu(
            "Rata-rata keluhan",
            f"{d.num_complaints.mean():.2f}"
        )

    ]

    # ------------------------------------------
    # BAR CHART: CHURN RATE PER REGION
    # ------------------------------------------

    reg = (
        d.groupby(
            "region",
            as_index=False
        )["churn"]
        .mean()
        .sort_values(
            "churn",
            ascending=False
        )
    )

    bar = px.bar(
        reg,
        x="region",
        y="churn",
        template="plotly_white",
        title="Churn rate per region",
        labels={
            "churn": "Churn rate",
            "region": ""
        },
        color_discrete_sequence=[
            "#C44E52"
        ]
    )

    bar.update_yaxes(
        tickformat=".0%"
    )

    # ------------------------------------------
    # SCATTER PLOT: TENURE VS TAGIHAN
    # custom_data berisi customer_id agar bisa dibaca
    # saat titik diklik (latihan 3) atau diseleksi (latihan 5)
    # ------------------------------------------

    sc = px.scatter(
        d,
        x="tenure_months",
        y="monthly_charges",
        color="status",
        opacity=0.6,
        color_discrete_map=WARNA,
        template="plotly_white",
        hover_name="customer_id",
        custom_data=["customer_id"],
        title="Tenure vs tagihan",
        labels={
            "tenure_months": "Tenure (bulan)",
            "monthly_charges": "Tagihan (Rp)"
        }
    )

    # LATIHAN 5: mode drag default = box select (lasso tersedia di toolbar)
    sc.update_layout(
        dragmode="select",
        clickmode="event+select"
    )

    # ------------------------------------------
    # LATIHAN 2: HISTOGRAM TENURE (IKUT TERFILTER)
    # ------------------------------------------

    hist = px.histogram(
        d,
        x="tenure_months",
        color="status",
        nbins=36,
        barmode="overlay",
        opacity=0.7,
        color_discrete_map=WARNA,
        template="plotly_white",
        title="Distribusi tenure (data terfilter)",
        labels={
            "tenure_months": "Tenure (bulan)",
            "status": "Status"
        }
    )

    return (
        kpi,
        bar,
        sc,
        info,
        hist
    )


# ==================================================
# 9. CALLBACK KEEMPAT
# Klik batang chart / seleksi scatter untuk filter tabel
# LATIHAN 4: data dibaca dari dcc.Store, bukan filter_df() lagi
# ==================================================

@callback(
    Output("tbl", "data"),
    Output("judul-tabel", "children"),

    Input("g-bar", "clickData"),
    Input("g-scatter", "selectedData"),
    Input("store-data", "data")
)
def update_tabel(
    click,
    selected,
    records
):

    d = dari_store(records)

    judul = (
        "Detail pelanggan (semua region terpilih)"
    )

    if ctx.triggered_id == "g-bar" and click:

        reg = click["points"][0]["x"]

        d = d[
            d.region == reg
        ]

        judul = (
            f"Detail pelanggan — region {reg}"
        )

    # LATIHAN 5: box/lasso select pada scatter memfilter tabel
    elif ctx.triggered_id == "g-scatter" and selected and selected.get("points"):

        ids = {
            p["customdata"][0]
            for p in selected["points"]
        }

        d = d[
            d.customer_id.isin(ids)
        ]

        judul = (
            f"Detail pelanggan — {len(d):,} titik terpilih di scatter"
        )

    return (
        d[TABEL_COLS].to_dict("records"),
        judul
    )


# ==================================================
# 10. LATIHAN 3: CALLBACK KELIMA
# Klik titik scatter -> tampilkan detail pelanggan
# ==================================================

@callback(
    Output("detail-pelanggan", "children"),
    Input("g-scatter", "clickData")
)
def tampilkan_detail(click):

    if not click:
        return [
            html.H3("Detail pelanggan"),
            html.P(
                "Klik salah satu titik pada scatter "
                "untuk melihat detail pelanggan.",
                style={"color": "#666"}
            )
        ]

    cid = click["points"][0]["customdata"][0]
    p = df.loc[df.customer_id == cid].iloc[0]

    def baris(label, nilai):
        return html.Tr([
            html.Td(label, style={"padding": "4px 12px 4px 0", "color": "#666"}),
            html.Td(nilai, style={"padding": "4px 0", "fontWeight": "bold"})
        ])

    return [
        html.H3("Detail pelanggan"),
        html.Table([
            baris("ID", p.customer_id),
            baris("Region", p.region),
            baris("Kontrak", p.contract_type),
            baris("Keluhan", f"{p.num_complaints}"),
            baris("Status", p.status),
        ])
    ]


# ==================================================
# 11. MENJALANKAN APLIKASI
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=False,
        port=8052
    )
