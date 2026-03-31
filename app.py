
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard Airbnb — Raul Gandara",
    page_icon="🏠",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    df = pd.read_csv("airbnb_limpio.csv")
    df["fecha_pago"]      = pd.to_datetime(df["fecha_pago"],   errors="coerce")
    df["fecha_inicio"]    = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["ingreso_bruto"]   = pd.to_numeric(df["ingreso_bruto"],   errors="coerce").fillna(0)
    df["monto_total"]     = pd.to_numeric(df["monto_total"],     errors="coerce").fillna(0)
    df["comision_airbnb"] = pd.to_numeric(df["comision_airbnb"], errors="coerce").fillna(0)
    df["noches"]          = pd.to_numeric(df["noches"],          errors="coerce").fillna(0)
    return df

df = cargar_datos()

orden_meses = {"December":0,"January":1,"February":2,"March":3}
meses_ordenados = sorted(df["mes_nombre"].unique().tolist(),
                         key=lambda x: orden_meses.get(x, 99))

# ── SIDEBAR ──────────────────────────────────────────────
st.sidebar.title("🏠 Filtros")
st.sidebar.markdown("---")

vista = st.sidebar.radio("Ver por:", ["Todas las propiedades","Por propiedad","Por mes"])

propiedades_sel = st.sidebar.multiselect(
    "Propiedades:",
    sorted(df["propiedad"].unique().tolist()),
    default=sorted(df["propiedad"].unique().tolist())
)
meses_sel = st.sidebar.multiselect(
    "Meses:", meses_ordenados, default=meses_ordenados
)

df_f = df[
    df["propiedad"].isin(propiedades_sel) &
    df["mes_nombre"].isin(meses_sel)
].copy()

# ── HEADER ───────────────────────────────────────────────
st.title("🏠 Dashboard Portafolio Airbnb — Raul Gandara")
st.markdown(f"📅 Dic 2025 — Mar 2026 | **{df_f['propiedad'].nunique()}** propiedades | **{len(meses_sel)}** meses")
st.info("💡 Los montos coinciden exactamente con el portal de Airbnb. Las noches son aproximadas — Airbnb usa datos internos no incluidos en el archivo exportado.")
st.markdown("---")

# ── MÉTRICAS ─────────────────────────────────────────────
total_bruto    = df_f["ingreso_bruto"].sum()
total_neto     = df_f["monto_total"].sum()
total_comision = df_f["comision_airbnb"].sum()
total_reserv   = len(df_f)
total_noches   = df_f["noches"].sum()
prom_noches    = df_f["noches"].mean()
pct_comision   = (total_comision / total_bruto * 100) if total_bruto > 0 else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💰 Ingreso bruto",       f"${total_bruto:,.0f}")
c2.metric("📈 Monto neto",          f"${total_neto:,.0f}")
c3.metric("✂️ Comisión Airbnb",    f"${total_comision:,.0f}",
          delta=f"-{pct_comision:.1f}% del bruto", delta_color="inverse")
c4.metric("📋 Reservaciones",       f"{total_reserv:,}")
c5.metric("🛏️ Noches aprox.",      f"~{total_noches:,.0f}")
c6.metric("📊 Prom noches/estancia",f"{prom_noches:.1f}")

st.markdown("---")

# ── VISTAS ───────────────────────────────────────────────
if vista == "Todas las propiedades":

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Monto neto por propiedad")
        res = df_f.groupby("propiedad")["monto_total"].sum().sort_values()
        promedio = res.mean()
        colores = ["#2ecc71" if v >= promedio else "#3498db" for v in res]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(res.index, res.values, color=colores)
        for i, v in enumerate(res.values):
            ax.text(v + 300, i, f"${v:,.0f}", va="center", fontsize=8)
        ax.axvline(x=promedio, color="red", linestyle="--",
                   linewidth=1.5, label=f"Promedio ${promedio:,.0f}")
        ax.set_xlabel("Monto Neto ($)")
        ax.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("✂️ Comisión Airbnb por propiedad")
        com = df_f.groupby("propiedad").agg(
            bruto    = ("ingreso_bruto",   "sum"),
            comision = ("comision_airbnb", "sum")
        )
        com["pct"] = (com["comision"] / com["bruto"] * 100).round(1)
        com = com.sort_values("comision")
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(com.index, com["comision"], color="#e74c3c")
        for i, (_, row) in enumerate(com.iterrows()):
            ax.text(row["comision"] + 100, i,
                   f"${row['comision']:,.0f} ({row['pct']}%)",
                   va="center", fontsize=8)
        ax.set_xlabel("Comisión ($)")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📈 Tendencia monto neto por mes")
        tend = df_f.groupby(["mes_num","mes_nombre","propiedad"])["monto_total"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(7, 5))
        for prop in propiedades_sel:
            d = tend[tend["propiedad"]==prop].sort_values("mes_num")
            if len(d) > 0:
                ax.plot(d["mes_nombre"], d["monto_total"],
                       marker="o", label=prop, linewidth=2)
        ax.set_xlabel("Mes")
        ax.set_ylabel("Monto Neto ($)")
        ax.legend(fontsize=6, loc="upper left")
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col4:
        st.subheader("✂️ Comisión Airbnb por mes")
        com_mes = df_f.groupby(["mes_num","mes_nombre"]).agg(
            bruto    = ("ingreso_bruto",   "sum"),
            comision = ("comision_airbnb", "sum")
        ).reset_index().sort_values("mes_num")
        com_mes["pct"] = (com_mes["comision"] / com_mes["bruto"] * 100).round(1)
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(com_mes["mes_nombre"], com_mes["comision"],
                     color="#e74c3c", zorder=3)
        for bar, pct in zip(bars, com_mes["pct"]):
            ax.text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 500,
                   f"${bar.get_height():,.0f}\n({pct}%)",
                   ha="center", fontsize=8)
        ax.set_ylabel("Comisión ($)")
        ax.grid(True, alpha=0.3, zorder=0)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Promedio noches por estancia por propiedad
    st.subheader("📊 Promedio de noches por estancia")
    prom_prop = df_f.groupby("propiedad")["noches"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 4))
    colores_p = ["#9b59b6" if v >= prom_prop.mean() else "#bdc3c7" for v in prom_prop]
    bars = ax.barh(prom_prop.index, prom_prop.values, color=colores_p)
    for i, v in enumerate(prom_prop.values):
        ax.text(v + 0.05, i, f"{v:.1f} noches", va="center", fontsize=9)
    ax.axvline(x=prom_prop.mean(), color="red", linestyle="--",
               linewidth=1.5, label=f"Promedio {prom_prop.mean():.1f}")
    ax.set_xlabel("Promedio noches por estancia")
    ax.legend(fontsize=8)
    ax.set_xlim(0, prom_prop.max() + 1.5)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

elif vista == "Por propiedad":

    propiedad_sel = st.selectbox(
        "Selecciona una propiedad:",
        sorted(df_f["propiedad"].unique().tolist())
    )
    df_prop = df_f[df_f["propiedad"] == propiedad_sel]

    st.markdown(f"### 🏠 {propiedad_sel}")

    p1, p2, p3, p4, p5 = st.columns(5)
    p_bruto    = df_prop["ingreso_bruto"].sum()
    p_neto     = df_prop["monto_total"].sum()
    p_comision = df_prop["comision_airbnb"].sum()
    p_noches   = df_prop["noches"].sum()
    p_prom     = df_prop["noches"].mean()
    p1.metric("💰 Ingreso bruto",      f"${p_bruto:,.0f}")
    p2.metric("📈 Monto neto",         f"${p_neto:,.0f}")
    p3.metric("✂️ Comisión Airbnb",   f"${p_comision:,.0f}",
              delta=f"-{(p_comision/p_bruto*100):.1f}%", delta_color="inverse")
    p4.metric("🛏️ Noches aprox.",     f"~{p_noches:,.0f}")
    p5.metric("📊 Prom noches",        f"{p_prom:.1f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Ingresos por mes")
        mes_prop = df_prop.groupby(["mes_num","mes_nombre"]).agg(
            bruto    = ("ingreso_bruto",   "sum"),
            neto     = ("monto_total",     "sum"),
            comision = ("comision_airbnb", "sum")
        ).reset_index().sort_values("mes_num")
        fig, ax = plt.subplots(figsize=(7, 4))
        x = range(len(mes_prop))
        w = 0.35
        ax.bar([i-w/2 for i in x], mes_prop["bruto"], width=w,
               label="Bruto", color="#3498db")
        ax.bar([i+w/2 for i in x], mes_prop["neto"],  width=w,
               label="Neto",  color="#2ecc71")
        ax.set_xticks(list(x))
        ax.set_xticklabels(mes_prop["mes_nombre"], rotation=30)
        ax.set_ylabel("Ingreso ($)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("✂️ Comisión Airbnb por mes")
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(mes_prop["mes_nombre"], mes_prop["comision"],
                     color="#e74c3c")
        for bar, (_, row) in zip(bars, mes_prop.iterrows()):
            pct = (row["comision"]/row["bruto"]*100) if row["bruto"] > 0 else 0
            ax.text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 200,
                   f"${bar.get_height():,.0f}\n({pct:.1f}%)",
                   ha="center", fontsize=8)
        ax.set_ylabel("Comisión ($)")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.subheader("📋 Reservaciones")
    tabla_prop = df_prop[["fecha_pago","mes_nombre","noches",
                          "ingreso_bruto","comision_airbnb","monto_total"]].copy()
    tabla_prop.columns = ["Fecha pago","Mes","Noches","Bruto","Comisión","Neto"]
    tabla_prop = tabla_prop.sort_values("Fecha pago", ascending=False)
    st.dataframe(tabla_prop, use_container_width=True)

elif vista == "Por mes":

    mes_sel = st.selectbox("Selecciona un mes:", meses_ordenados)
    df_mes  = df_f[df_f["mes_nombre"] == mes_sel]

    st.markdown(f"### 📅 {mes_sel} 2026")

    m1, m2, m3, m4, m5 = st.columns(5)
    m_bruto    = df_mes["ingreso_bruto"].sum()
    m_neto     = df_mes["monto_total"].sum()
    m_comision = df_mes["comision_airbnb"].sum()
    m_noches   = df_mes["noches"].sum()
    m_prom     = df_mes["noches"].mean()
    m1.metric("💰 Ingreso bruto",     f"${m_bruto:,.0f}")
    m2.metric("📈 Monto neto",        f"${m_neto:,.0f}")
    m3.metric("✂️ Comisión Airbnb",  f"${m_comision:,.0f}",
              delta=f"-{(m_comision/m_bruto*100):.1f}%", delta_color="inverse")
    m4.metric("🛏️ Noches aprox.",    f"~{m_noches:,.0f}")
    m5.metric("📊 Prom noches",       f"{m_prom:.1f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Monto neto por propiedad")
        res_mes = df_mes.groupby("propiedad")["monto_total"].sum().sort_values()
        colores = ["#2ecc71" if v >= res_mes.mean() else "#3498db" for v in res_mes]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(res_mes.index, res_mes.values, color=colores)
        for i, v in enumerate(res_mes.values):
            ax.text(v + 200, i, f"${v:,.0f}", va="center", fontsize=8)
        ax.axvline(x=res_mes.mean(), color="red", linestyle="--",
                   linewidth=1.5, label=f"Promedio ${res_mes.mean():,.0f}")
        ax.set_xlabel("Monto Neto ($)")
        ax.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("✂️ Comisión Airbnb por propiedad")
        com_mes_prop = df_mes.groupby("propiedad").agg(
            bruto    = ("ingreso_bruto",   "sum"),
            comision = ("comision_airbnb", "sum")
        )
        com_mes_prop["pct"] = (com_mes_prop["comision"]/com_mes_prop["bruto"]*100).round(1)
        com_mes_prop = com_mes_prop.sort_values("comision")
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(com_mes_prop.index, com_mes_prop["comision"], color="#e74c3c")
        for i, (_, row) in enumerate(com_mes_prop.iterrows()):
            ax.text(row["comision"] + 100, i,
                   f"${row['comision']:,.0f} ({row['pct']}%)",
                   va="center", fontsize=8)
        ax.set_xlabel("Comisión ($)")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.subheader("📊 Promedio noches por estancia")
    prom_mes = df_mes.groupby("propiedad")["noches"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 4))
    colores_p = ["#9b59b6" if v >= prom_mes.mean() else "#bdc3c7" for v in prom_mes]
    ax.barh(prom_mes.index, prom_mes.values, color=colores_p)
    for i, v in enumerate(prom_mes.values):
        ax.text(v + 0.05, i, f"{v:.1f}", va="center", fontsize=9)
    ax.axvline(x=prom_mes.mean(), color="red", linestyle="--",
               linewidth=1.5, label=f"Promedio {prom_mes.mean():.1f}")
    ax.set_xlabel("Promedio noches por estancia")
    ax.legend(fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.subheader("📋 Resumen del mes por propiedad")
    tabla_mes = df_mes.groupby("propiedad").agg(
        Reservaciones = ("noches",          "count"),
        Noches        = ("noches",          "sum"),
        Prom_Noches   = ("noches",          "mean"),
        Bruto         = ("ingreso_bruto",   "sum"),
        Comision      = ("comision_airbnb", "sum"),
        Neto          = ("monto_total",     "sum")
    ).round(1).sort_values("Neto", ascending=False)
    tabla_mes["% Comision"] = (tabla_mes["Comision"]/tabla_mes["Bruto"]*100).round(1)
    st.dataframe(tabla_mes, use_container_width=True)

# ── TABLA GLOBAL ─────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Tabla resumen completa")
tabla = df_f.groupby("propiedad").agg(
    Reservaciones = ("noches",          "count"),
    Noches        = ("noches",          "sum"),
    Prom_Noches   = ("noches",          "mean"),
    Bruto         = ("ingreso_bruto",   "sum"),
    Comision      = ("comision_airbnb", "sum"),
    Neto          = ("monto_total",     "sum")
).round(1).sort_values("Neto", ascending=False)
tabla["% Comision"] = (tabla["Comision"]/tabla["Bruto"]*100).round(1)
st.dataframe(tabla, use_container_width=True)

st.markdown("---")
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
col_t1.metric("💰 Total bruto",        f"${total_bruto:,.0f} MXN")
col_t2.metric("📈 Total neto",         f"${total_neto:,.0f} MXN")
col_t3.metric("✂️ Total comisión",    f"${total_comision:,.0f} MXN")
col_t4.metric("📊 Prom noches/estancia", f"{prom_noches:.1f} noches")

st.caption("⚠️ Noches aproximadas — los montos coinciden exactamente con el portal de Airbnb.")
st.caption("Dashboard construido con Python + Streamlit — Raul Gandara 2026")
