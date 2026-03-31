
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Airbnb", page_icon="🏠", layout="wide")

@st.cache_data
def cargar_datos():
    np.random.seed(42)
    propiedades = [
        ("Emily House",     850, 4200),
        ("Casa Zoe",        750, 3800),
        ("Casa 5min CAS",   650, 3500),
        ("Casa Alegre",     900, 4500),
        ("Casa del Parque", 700, 3200),
        ("Casa de Ineva",   800, 4000)
    ]
    meses = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio"}
    filas = []
    for mes_num, mes_nombre in meses.items():
        for nombre, precio, gastos in propiedades:
            noches = np.random.randint(12, 28)
            filas.append({
                "mes_nombre": mes_nombre, "mes_num": mes_num,
                "propiedad": nombre, "noches": noches,
                "precio_noche": precio, "gastos": gastos
            })
    df = pd.DataFrame(filas)
    df["ingreso_bruto"] = df["noches"] * df["precio_noche"]
    df["utilidad_neta"] = df["ingreso_bruto"] - df["gastos"]
    df["ocupacion_pct"] = (df["noches"] / 30 * 100).round(1)
    df["roi_pct"]       = (df["utilidad_neta"] / df["gastos"] * 100).round(1)
    return df

df = cargar_datos()

st.sidebar.title("🏠 Filtros")
propiedades_sel = st.sidebar.multiselect(
    "Propiedades:", df["propiedad"].unique().tolist(),
    default=df["propiedad"].unique().tolist()
)
meses_sel = st.sidebar.multiselect(
    "Meses:", df["mes_nombre"].unique().tolist(),
    default=df["mes_nombre"].unique().tolist()
)
meta = st.sidebar.slider("Meta ocupación (%):", 50, 95, 70, 5)

df_f = df[df["propiedad"].isin(propiedades_sel) & df["mes_nombre"].isin(meses_sel)]

st.title("🏠 Dashboard Portafolio Airbnb 2024")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Ingreso Total",   f"${df_f['ingreso_bruto'].sum():,.0f}")
c2.metric("📈 Utilidad Total",  f"${df_f['utilidad_neta'].sum():,.0f}")
c3.metric("🛏️ Ocupación Prom", f"{df_f['ocupacion_pct'].mean():.1f}%")
c4.metric("🏆 ROI Promedio",    f"{df_f['roi_pct'].mean():.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Ingreso por Propiedad")
    res = df_f.groupby("propiedad")["ingreso_bruto"].sum().sort_values()
    colores = ["green" if v >= res.mean() else "steelblue" for v in res]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(res.index, res.values, color=colores)
    for i, v in enumerate(res.values):
        ax.text(v + 200, i, f"${v:,.0f}", va="center", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("🎯 Ocupación vs Meta")
    ocup = df_f.groupby("propiedad")["ocupacion_pct"].mean().sort_values()
    colores_o = ["green" if v >= meta else "orange" if v >= meta*0.85 else "red"
                 for v in ocup]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(ocup.index, ocup.values, color=colores_o)
    ax.axvline(x=meta, color="red", linestyle="--", linewidth=2, label=f"Meta {meta}%")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Tendencia Mensual")
    tend = df_f.groupby(["mes_num","mes_nombre","propiedad"])["ingreso_bruto"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    for prop in propiedades_sel:
        d = tend[tend["propiedad"]==prop].sort_values("mes_num")
        ax.plot(d["mes_nombre"], d["ingreso_bruto"], marker="o", label=prop, linewidth=2)
    ax.legend(fontsize=7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col4:
    st.subheader("💹 Ocupación vs ROI")
    sc = df_f.groupby("propiedad").agg(
        ocupacion=("ocupacion_pct","mean"), roi=("roi_pct","mean")
    ).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(sc["ocupacion"], sc["roi"], s=150, color="purple", zorder=5)
    for _, row in sc.iterrows():
        ax.annotate(row["propiedad"].split()[0], (row["ocupacion"], row["roi"]),
                   textcoords="offset points", xytext=(5,5), fontsize=8)
    ax.axvline(x=meta, color="red", linestyle="--", alpha=0.5)
    ax.set_xlabel("Ocupación (%)")
    ax.set_ylabel("ROI (%)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")
st.subheader("📋 Resumen por Propiedad")
tabla = df_f.groupby("propiedad").agg(
    Ingreso=("ingreso_bruto","sum"),
    Utilidad=("utilidad_neta","sum"),
    Ocupacion=("ocupacion_pct","mean"),
    ROI=("roi_pct","mean")
).round(1).sort_values("Ingreso", ascending=False)
st.dataframe(tabla, use_container_width=True)
st.caption("Dashboard construido con Python + Streamlit — Raul Gandara 2024")
