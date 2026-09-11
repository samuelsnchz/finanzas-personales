import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página y paleta corporativa (Estética Minimalista de Papel)
st.set_page_config(page_title="Control Financiero Quincenal", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    /* Fondo principal Azul Marino */
    .stApp { background-color: #0E3846; }
    
    /* Tipografía general en Blanco y Gris Muted */
    h1, h2, h3, p, span, label, .stMarkdown { color: #F8F9FA !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Tarjetas estilo papel (Verde Salvia y Verde Menta) */
    .kpi-card {
        background-color: #E4EFE7;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        text-align: center;
    }
    .kpi-card-main {
        background-color: #93CBA8;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        text-align: center;
    }
    .kpi-title { color: #5A6B6B !important; font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; }
    .kpi-value { color: #0E3846 !important; font-size: 2rem; font-weight: bold; margin: 0; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Panel de Control y Metas Financieras")
st.markdown("Monitoreo quincenal, presupuesto vs. real y seguimiento de metas.")

# --- 1. CARGA DE DATOS DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=30)
def load_data():
    sheet_id = "1C6lm7X3DB6sx3xhJ9PKMuFVlgvnzyypCzCH52_-Dbg4"
    sheet_name = "Datos"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        df['Dia'] = df['Fecha'].dt.day
        df['Quincena'] = df.apply(lambda row: f"{row['Fecha'].strftime('%Y-%m')} - {'Q1 (1-15)' if row['Dia'] <= 15 else 'Q2 (16-fin)'}" if pd.notnull(row['Fecha']) else "Sin Fecha", axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ No se detectaron datos en tu Google Sheets o falta configurar el ID de la hoja en el código.")
else:
    # --- 2. FILTROS EN LA BARRA LATERAL ---
    st.sidebar.header("Filtros de Período")
    quincenas_disponibles = sorted(df['Quincena'].unique(), reverse=True)
    quincena_seleccionada = st.sidebar.selectbox("Selecciona la Quincena", quincenas_disponibles)
    
    df_q = df[df['Quincena'] == quincena_seleccionada]

    # --- 3. MÉTRICAS PRINCIPALES (KPIS) ---
    total_ingresos = df_q[df_q['Tipo'] == 'Ingreso']['Monto'].sum()
    total_egresos = df_q[df_q['Tipo'] == 'Egreso']['Monto'].sum()
    flujo_neto = total_ingresos - total_egresos

    st.subheader(f"Resumen del Periodo: {quincena_seleccionada}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="kpi-card"><p class="kpi-title">📥 Ingresos Quincenales</p><p class="kpi-value">${total_ingresos:,.2f}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><p class="kpi-title">📤 Egresos Quincenales</p><p class="kpi-value">${total_egresos:,.2f}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card-main"><p class="kpi-title" style="color:#0E3846 !important;">💡 Flujo Neto</p><p class="kpi-value">${flujo_neto:,.2f}</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. CONTROL DE PRESUPUESTO VS REAL POR CATEGORÍA ---
    st.subheader("🎯 Presupuesto vs. Real (Egresos por Categoría)")
    
    categorias_oficiales = [
        "Casa", "Personales", "Préstamos y Tarjetas", 
        "Auto y transporte", "Educación y Deporte", "Extras", "Ahorros"
    ]

    presupuestos_base = {
        "Casa": 15500, "Personales": 5800, "Préstamos y Tarjetas": 7000,
        "Auto y transporte": 1500, "Educación y Deporte": 900, "Extras": 3800, "Ahorros": 2500
    }

    gastos_reales = df_q[df_q['Tipo'] == 'Egreso'].groupby('Categoría')['Monto'].sum().to_dict()

    cols = st.columns(2)
    for i, cat in enumerate(categorias_oficiales):
        real = gastos_reales.get(cat, 0.0)
        presupuesto = presupuestos_base.get(cat, 2000)
        porcentaje = (real / presupuesto) if presupuesto > 0 else 0
        
        with cols[i % 2]:
            st.markdown(f"**{cat}** (Gastado: ${real:,.2f} / Límite: ${presupuesto:,.2f})")
            if porcentaje >= 1.0:
                st.error(f"🚨 ¡Límite superado! ({porcentaje*100:.1f}%)")
            elif porcentaje >= 0.8:
                st.warning(f"⚠️ Alerta de gasto cercano al límite ({porcentaje*100:.1f}%)")
            else:
                st.success(f"✅ Gasto saludable ({porcentaje*100:.1f}%)")
            st.progress(min(porcentaje, 1.0))
            st.markdown("---")

    # --- 5. GRÁFICOS ANALÍTICOS (ESTÉTICA MINIMALISTA TIPO PAPEL) ---
    st.subheader("📈 Análisis Gráfico")
    g_col1, g_col2 = st.columns(2)

    df_egresos = df_q[df_q['Tipo'] == 'Egreso']
    
    with g_col1:
        st.markdown("**Distribución de Egresos (Estilo Anillo Limpio)**")
        if not df_egresos.empty:
            df_g_pie = df_egresos.groupby('Categoría')['Monto'].sum().reset_index()
            
            # Gráfico de Anillo personalizado con Plotly Graph Objects (Sin fondos ni ruido visual)
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_g_pie['Categoría'],
                values=df_g_pie['Monto'],
                hole=0.65,
                marker=dict(colors=['#93CBA8', '#E4EFE7', '#5A6B6B', '#0E3846', '#F8F9FA']),
                textinfo='label+percent',
                textfont=dict(color='#F8F9FA', size=12)
            )])
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=350
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay egresos registrados en esta quincena.")

    with g_col2:
        st.markdown("**Presupuesto vs Real (Barras Minimalistas)**")
        # Gráfico de barras agrupadas con líneas horizontales limpias (Referencia de barras estilo papel)
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            name='Real',
            x=categorias_oficiales,
            y=[gastos_reales.get(cat, 0) for cat in categorias_oficiales],
            marker_color='#93CBA8',
            marker_line_width=0
        ))
        
        fig_bar.add_trace(go.Bar(
            name='Presupuesto',
            x=categorias_oficiales,
            y=[presupuestos_base.get(cat, 0) for cat in categorias_oficiales],
            marker_color='#5A6B6B',
            marker_line_width=0
        ))
        
        fig_bar.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F8F9FA'),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(90, 107, 107, 0.4)', # Líneas horizontales finas y discretas
                zeroline=False
            ),
            xaxis=dict(
                showgrid=False, 
                zeroline=False
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20),
            height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 6. SECCIÓN DE METAS A CORTO, MEDIANO Y LARGO PLAZO ---
    st.markdown("---")
    st.subheader("🚀 Seguimiento de Metas Financieras")
    
    actual_ahorros = df[df['Categoría'] == 'Ahorros']['Monto'].sum()
    
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    
    with meta_col1:
        st.markdown("### 🛠️ Corto Plazo")
        st.write("**Bebé**")
        meta_cp = 35000 
        prog_cp = min(actual_ahorros / meta_cp, 1.0) if meta_cp > 0 else 0
        st.progress(prog_cp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_cp:,.2f} ({prog_cp*100:.1f}%)")

    with meta_col2:
        st.markdown("### 🚗 Mediano Plazo")
        st.write("**Fondo de Emergencia**")
        meta_mp = 110000 
        prog_mp = min(actual_ahorros / meta_mp, 1.0) if meta_mp > 0 else 0
        st.progress(prog_mp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_mp:,.2f} ({prog_mp*100:.1f}%)")

    with meta_col3:
        st.markdown("### 🏡 Largo Plazo")
        st.write("**Pa'la Casa**")
        meta_lp = 250000 
        prog_lp = min(actual_ahorros / meta_lp, 1.0) if meta_lp > 0 else 0
        st.progress(prog_lp)
        st.caption(f"Progreso: ${actual_ahorros:,.2f} / ${meta_lp:,.2f} ({prog_lp*100:.1f}%)")

    # --- 7. REGISTROS DETALLADOS ---
    with st.expander("Ver tabla completa de movimientos de la quincena"):
        st.dataframe(df_q, use_container_width=True)
