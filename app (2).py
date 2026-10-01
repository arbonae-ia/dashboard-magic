import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Comercial", layout="wide")
st.title("📊 Control de Gestión - Visitas Comerciales")

# Permitir cargar el archivo
archivo = st.file_uploader("Sube el archivo Excel de la correría", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)
    df['Valor Pedido'] = pd.to_numeric(df['Valor Pedido'], errors='coerce').fillna(0)
    df['Metros Pedidos'] = pd.to_numeric(df['Metros Pedidos'], errors='coerce').fillna(0)
    
    # KPIs Rápidos
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("💰 Total Ventas", f"${df['Valor Pedido'].sum():,.2f}")
    kpi2.metric("📍 Total Visitas", f"{df['ID_Visita'].nunique()}")
    
    # Gráfico de Barras interactivo
    df_etapas = df['Etapa Comercial'].value_counts().reset_index()
    df_etapas.columns = ['Etapa', 'Cantidad']
    fig = px.bar(df_etapas, x='Cantidad', y='Etapa', orientation='h', title="Clientes por Etapa")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Por favor sube el archivo Excel para activar el reporte.")
