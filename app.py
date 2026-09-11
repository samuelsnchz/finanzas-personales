import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Control Financiero Quincenal", page_icon="💰", layout="wide")

st.title("📊 Panel de Control y Metas Financieras")
st.markdown("Monitoreo quincenal, presupuesto vs. real y seguimiento de metas.")

# --- 1. CARGA DE DATOS DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=30)
def load_data():
    # IMPORTANTE: Reemplaza '1C6lm7X3DB6sx3xhJ9PKMuFVlgvnzyypCzCH52_-Dbg4' con el ID real de tu Google Sheets 
    # y asegúrate de que la hoja esté compartida (Cualquier usuario con el enlace -> Lector)
    sheet_id = "1C6lm7X3DB6sx3xhJ9PKMuFVlgvnzyypCzCH52_-Dbg4"
    sheet_name = "Datos"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
        # Limpieza y tipado de datos
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        # Asignación automática de Quincena (Q1: días 1-15, Q2: días 16-31)
        df['Dia'] = df['Fecha'].dt.day
        df['Quincena'] = df.apply(lambda row: f"{row['Fecha'].strftime('%Y-%m')} - {'Q1 (1-15)' if row['Dia'] <= 15 else 'Q2 (16-fin)'}" if pd.notnull(row['Fecha']) else "Sin Fecha", axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ No se detectaron datos en tu Google Sheets o falta configurar el ID de la hoja en el código.")
    st.info("💡 Asegúrate de poner tu Sheet ID real en la variable `sheet_id` dentro del código de Python.")
else:
    # --- 2. FILTROS EN LA BARRA LATERAL ---
    st.sidebar.header("Filtros de Período")
    quincenas_disponibles = sorted(df['Quincena'].unique(), reverse=True)
    quincena_seleccionada = st.sidebar.selectbox("Selecciona la Quincena", quincenas_disponibles)
    
    # Filtrar DataFrame por la quincena elegida
    df_q = df[df['Quincena'] == quincena_seleccionada]

    # --- 3. MÉTRICAS PRINCIPALES (KPIS) ---
    total_ingresos = df_q[df_q['Tipo'] == 'Ingreso']['Monto'].sum()
    total_egresos = df_q[df_q['Tipo'] == 'Egreso']['Monto'].sum()
    flujo_neto = total_ingresos - total_egresos

    st.subheader(f"Resumen del Periodo: {quincena_seleccionada}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Ingresos Quincenales", f"${total_ingresos:,.2f} MXN")
    col2.metric("📤 Egresos Quincenales", f"${total_egresos:,.2f} MXN")
    col3.metric("💡 Flujo Neto", f"${flujo_neto:,.2f} MXN", delta=f"${flujo_neto:,.2f}")

    st.markdown("---")

    # --- 4. CONTROL DE PRESUPUESTO VS REAL POR CATEGORÍA ---
    st.subheader("🎯 Presupuesto vs. Real (Egresos por Categoría)")
    
    # Categorías oficiales definidas
    categorias_oficiales = [
        "Casa", "Personales", "Préstamos y Tarjetas", 
        "Auto y transporte", "Educación y Deporte", "Extras", "Ahorros"
    ]

    # Simulación de presupuestos quincenales base (puedes ajustarlos o conectarlos a una tabla de metas)
    presupuestos_base = {
        "Casa": 15500, 
        "Personales": 5800, 
        "Préstamos y Tarjetas": 7000,
        "Auto y transporte": 1500, 
        "Educación y Deporte": 900, 
        "Extras": 3800, 
        "Ahorros": 2500
    }

    # Agrupar gastos reales por categoría en la quincena
    gastos_reales = df_q[df_q['Tipo'] == 'Egreso'].groupby('Categoría')['Monto'].sum().to_dict()

    # Mostrar barras de progreso y alertas gráficas por categoría
    cols = st.columns(2)
    for i, cat in enumerate(categorias_oficiales):
        real = gastos_reales.get(cat, 0.0)
        presupuesto = presupuestos_base.get(cat, 2000) # Límite por defecto quincenal
        porcentaje = (real / presupuesto) if presupuesto > 0 else 0
        
        with cols[i % 2]:
            st.markdown(f"**{cat}** (Gastado: ${real:,.2f} / Límite: ${presupuesto:,.2f})")
            
            # Alertas visuales con colores según el porcentaje consumido
            if porcentaje >= 1.0:
                st.error(f"🚨 ¡Límite superado! ({porcentaje*100:.1f}%)")
            elif porcentaje >= 0.8:
                st.warning(f"⚠️ Alerta de gasto cercano al límite ({porcentaje*100:.1f}%)")
            else:
                st.success(f"✅ Gasto saludable ({porcentaje*100:.1f}%)")
                
            st.progress(min(porcentaje, 1.0))
            st.markdown("---")

    # --- 5. GRÁFICOS ANALÍTICOS ---
    st.subheader("📈 Análisis Gráfico")
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.markdown("**Distribución de Gastos (Dona)**")
        df_egresos = df_q[df_q['Tipo'] == 'Egreso']
        if not df_egresos.empty:
            fig_pie = px.pie(df_egresos, names='Categoría', values='Monto', hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay egresos registrados en esta quincena.")

    with g_col2:
        st.markdown("**Presupuesto vs Real (Comparativa)**")
        comparativa_data = []
        for cat in categorias_oficiales:
            comparativa_data.append({
                "Categoría": cat,
                "Tipo": "Real",
                "Monto": gastos_reales.get(cat, 0)
            })
            comparativa_data.append({
                "Categoría": cat,
                "Tipo": "Presupuesto",
                "Monto": presupuestos_base.get(cat, 0)
            })
        df_comp = pd.DataFrame(comparativa_data)
        fig_bar = px.bar(df_comp, x='Categoría', y='Monto', color='Tipo', barmode='group', color_discrete_map={'Real': '#EF553B', 'Presupuesto': '#636EFA'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 6. SECCIÓN DE METAS A CORTO, MEDIANO Y LARGO PLAZO ---
    st.markdown("---")
    st.subheader("🚀 Seguimiento de Metas Financieras")
    
    # Calcular el acumulado histórico de la categoría 'Ahorros' desde tu Google Sheets
    actual_ahorros = df[df['Categoría'] == 'Ahorros']['Monto'].sum()
    
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    
    with meta_col1:
        st.markdown("### 🛠️ Corto Plazo")
        st.write("**Bebé**")
        meta_cp = 35000  # Puedes ajustar tu meta aquí
        prog_cp = min(actual_ahorros / meta_cp, 1.0) if meta_cp > 0 else 0
        st.progress(prog_cp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_cp:,.2f} ({prog_cp*100:.1f}%)")

    with meta_col2:
        st.markdown("### 🚗 Mediano Plazo")
        st.write("**Fondo de Emergencia**")
        meta_mp = 110000  # Puedes ajustar tu meta aquí
        prog_mp = min(actual_ahorros / meta_mp, 1.0) if meta_mp > 0 else 0
        st.progress(prog_mp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_mp:,.2f} ({prog_mp*100:.1f}%)")

    with meta_col3:
        st.markdown("### 🏡 Largo Plazo")
        st.write("**Pa'la Casa**")
        meta_lp = 250000 # Puedes ajustar tu meta aquí
        prog_lp = min(actual_ahorros / meta_lp, 1.0) if meta_lp > 0 else 0
        st.progress(prog_lp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_lp:,.2f} ({prog_lp*100:.1f}%)")

    # --- 7. REGISTROS DETALLADOS ---
    with st.expander("Ver tabla completa de movimientos de la quincena"):
        st.dataframe(df_q, use_container_width=True)
