import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA Y COLORES BASE
st.set_page_config(page_title="Mis Finanzas 360", layout="wide", initial_sidebar_state="collapsed")

# Inyección de CSS para la estética de papel y paleta corporativa
st.markdown("""
    <style>
    /* Fondo Azul Marino */
    .stApp {
        background-color: #0E3846;
    }
    /* Tarjetas estilo papel Verde Salvia */
    .kpi-card {
        background-color: #E4EFE7;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 4px 6px 12px rgba(0,0,0,0.25); /* Sombra para simular relieve de papel */
        text-align: center;
    }
    /* Tarjeta de acento Verde Menta */
    .kpi-card-main {
        background-color: #93CBA8;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 4px 6px 12px rgba(0,0,0,0.25);
        text-align: center;
    }
    .kpi-title { color: #5A6B6B; font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; }
    .kpi-value { color: #0E3846; font-size: 2.2rem; font-weight: bold; margin: 0; }
    /* Ajuste de tipografía global */
    h1, h2, h3, p { color: #F8F9FA !important; font-family: 'Helvetica Neue', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Mis Finanzas 360</h1>", unsafe_allow_html=True)
st.write("---")

# 2. TARJETAS DE RESUMEN (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="kpi-card"><p class="kpi-title">Ingresos Quincenales</p><p class="kpi-value">$15,000</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><p class="kpi-title">Gastos Registrados</p><p class="kpi-value">$8,450</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card-main"><p class="kpi-title" style="color:#0E3846;">Balance Disponible</p><p class="kpi-value">$6,550</p></div>', unsafe_allow_html=True)

st.write("")
st.write("")

# 3. GRÁFICOS Y ANÁLISIS
col_izq, col_der = st.columns([1.5, 1.2])

with col_izq:
    st.markdown("### Tendencia de Gastos")
    # Gráfico de Barras Minimalista (Estilo Papel)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=['Comida', 'Transporte', 'Vivienda', 'Servicios'],
        y=[3200, 1500, 4000, 1800],
        marker_color=['#0E3846', '#93CBA8', '#E4EFE7', '#5A6B6B'],
        marker_line_color='rgba(255,255,255,0.2)',
        marker_line_width=1,
        opacity=0.95
    ))
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F8F9FA'),
        yaxis=dict(showgrid=True, gridcolor='#5A6B6B', zeroline=False, gridwidth=1),
        xaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=0, r=0, t=20, b=0),
        height=300
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.write("---")
    
    st.markdown("### Distribución Financiera")
    # Gráfico tipo Sunburst / Anillo para análisis de distribución
    fig_pie = go.Figure(data=[go.Pie(
        labels=['Fijos', 'Variables', 'Ahorro', 'Entretenimiento'], 
        values=[50, 20, 20, 10], 
        hole=.6, # Crea el centro vacío del anillo
        marker_colors=['#E4EFE7', '#93CBA8', '#5A6B6B', '#0E3846'],
        textinfo='label+percent',
        textfont=dict(color='#0E3846', size=14, family='Arial Black')
    )])
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0),
        height=300
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_der:
    st.markdown("### Metas de Ahorro")
    # Gráfico Polar/Radial escalonado simulando estructura 3D concéntrica
    fig_metas = go.Figure(go.Barpolar(
        r=[80, 50, 35], # Porcentajes de avance
        theta=['Corto Plazo<br>(Mensual)', 'Medio Plazo<br>(Trimestral)', 'Largo Plazo<br>(Semestral)'],
        width=[0.75, 0.75, 0.75],
        marker_color=['#93CBA8', '#E4EFE7', '#5A6B6B'],
        marker_line_color='#0E3846',
        marker_line_width=2,
        opacity=0.9
    ))
    fig_metas.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False, ticks='', gridcolor='rgba(90, 107, 107, 0.3)'),
            angularaxis=dict(showticklabels=True, ticks='', tickfont=dict(color='#F8F9FA', size=13))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        height=450
    )
    st.plotly_chart(fig_metas, use_container_width=True)
