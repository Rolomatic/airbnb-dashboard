
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Airbnb — Raul Gandara", page_icon="🏠", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("airbnb_limpio.csv")
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"])
    return df

df = cargar_datos()

# Sidebar
st.sidebar.title("🏠 Filtros")
propiedades_sel = st.sidebar.multiselect(
    "Propiedades:",
    df["propiedad"].unique().tolist(),
    default=df["propiedad"].unique().tolist()
)
meses_disponibles = df["mes_nombre"].unique().tolist()
meses_sel = st.sidebar.multiselect(
    "Meses:",
    meses_disponibles,
    default=meses_disponibles
)
meta = st.sidebar.slider("Meta ocupación (%):", 30, 95, 60, 5)

df_f = df[
    df["propiedad"].isin(propiedades_sel) &
    df["mes_nombre"].isin(meses_sel)
]

# Header
st.title("🏠 Dashboard Portafolio Airbnb — Raul Gandara")
st.markdown(f"📅 Enero — Marzo 2026 | {len(propiedades_sel)} propiedades | {len(meses_sel)} meses")
st.markdown("---")

# Métricas
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Ingreso Bruto",    f"${df_f['ingreso_bruto'].sum():,.0f}")
c2.metric("📈 Ingreso Neto",     f"${df_f['ingreso_neto'].sum():,.0f}")
c3.metric("🛏️ Noches Vendidas", f"{df_f['noches'].sum():,.0f}")
c4.metric("📋 Reservaciones",    f"{len(df_f):,}")
c5.metric("🏠 Propiedades",      f"{df_f['propiedad'].nunique()}")

st.markdown("---")

# Gráfica 1 y 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Ingreso bruto por propiedad")
    res = df_f.groupby("propiedad")["ingreso_bruto"].sum().sort_values()
    promedio = res.mean()
    colores = ["green" if v >= promedio else "steelblue" for v in res]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.barh(res.index, res.values, color=colores)
    for i, v in enumerate(res.values):
        ax.text(v + 500, i, f"${v:,.0f}", va="center", fontsize=8)
    ax.axvline(x=promedio, color="red", linestyle="--",
               linewidth=1.5, label=f"Promedio ${promedio:,.0f}")
    ax.legend(fontsize=8)
    ax.set_xlabel("Ingreso ($)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("🛏️ Noches vendidas por propiedad")
    noches = df_f.groupby("propiedad")["noches"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(7, 5))
    colores_n = ["green" if v >= noches.mean() else "steelblue" for v in noches]
    ax.barh(noches.index, noches.values, color=colores_n)
    for i, v in enumerate(noches.values):
        ax.text(v + 0.5, i, f"{v:.0f} noches", va="center", fontsize=8)
    ax.set_xlabel("Noches")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Gráfica 3 y 4
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Tendencia de ingresos por mes")
    orden_meses = {"January":1, "February":2, "March":3, "December":0}
    tend = df_f.groupby(["mes_num","mes_nombre","propiedad"])["ingreso_bruto"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    for prop in propiedades_sel:
        d = tend[tend["propiedad"]==prop].sort_values("mes_num")
        if len(d) > 0:
            ax.plot(d["mes_nombre"], d["ingreso_bruto"],
                   marker="o", label=prop, linewidth=2)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Ingreso ($)")
    ax.legend(fontsize=6, loc="upper left")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col4:
    st.subheader("📊 Reservaciones por propiedad")
    reserv = df_f.groupby("propiedad")["noches"].count().sort_values()
    fig, ax = plt.subplots(figsize=(7, 5))
    colores_r = ["green" if v >= reserv.mean() else "steelblue" for v in reserv]
    ax.barh(reserv.index, reserv.values, color=colores_r)
    for i, v in enumerate(reserv.values):
        ax.text(v + 0.1, i, str(int(v)), va="center", fontsize=8)
    ax.set_xlabel("Número de reservaciones")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Tabla completa
st.markdown("---")
st.subheader("📋 Resumen completo por propiedad")
tabla = df_f.groupby("propiedad").agg(
    Reservaciones  = ("noches",        "count"),
    Noches         = ("noches",        "sum"),
    Ingreso_Bruto  = ("ingreso_bruto", "sum"),
    Ingreso_Neto   = ("ingreso_neto",  "sum"),
).round(0).sort_values("Ingreso_Bruto", ascending=False)

tabla["Comision_Airbnb"] = (tabla["Ingreso_Bruto"] - tabla["Ingreso_Neto"]).round(0)
tabla["Pct_Comision"]    = ((tabla["Comision_Airbnb"] / tabla["Ingreso_Bruto"]) * 100).round(1)

st.dataframe(tabla, use_container_width=True)

# Totales
st.markdown("---")
col_t1, col_t2, col_t3 = st.columns(3)
col_t1.metric("💰 Total ingreso bruto",     f"${df_f['ingreso_bruto'].sum():,.0f} MXN")
col_t2.metric("📈 Total ingreso neto",      f"${df_f['ingreso_neto'].sum():,.0f} MXN")
col_t3.metric("✂️ Total comisión Airbnb",  f"${(df_f['ingreso_bruto'].sum() - df_f['ingreso_neto'].sum()):,.0f} MXN")

st.caption("Dashboard construido con Python + Streamlit — Raul Gandara 2026")
