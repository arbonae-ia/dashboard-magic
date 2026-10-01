import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard Comercial", layout="wide")
st.title("📊 Control de Gestión - Visitas Comerciales")
st.markdown("Herramienta automatizada para la evaluación de la gestión de ventas.")

# 2. CARGA DEL ARCHIVO EXCEL
archivo = st.file_uploader("Sube el archivo Excel de la correría", type=["xlsx", "xls"])

if archivo is not None:
    # Leer datos con Pandas
    df = pd.read_excel(archivo)
    
    # Limpieza estándar de datos numéricos
    df['Valor Pedido'] = pd.to_numeric(df['Valor Pedido'], errors='coerce').fillna(0)
    df['Metros Pedidos'] = pd.to_numeric(df['Metros Pedidos'], errors='coerce').fillna(0)
    
    # 3. FILTROS DINÁMICOS EN LA BARRA LATERAL
    st.sidebar.header("🔍 Filtros del Reporte")
    
    ciudades_disponibles = ["Todas"] + list(df['Ciudad'].dropna().unique())
    ciudad_sel = st.sidebar.selectbox("Selecciona la Ciudad:", ciudades_disponibles)
    
    segmentos_disponibles = ["Todos"] + list(df['Segmento'].dropna().unique())
    segmento_sel = st.sidebar.selectbox("Selecciona el Segmento:", segmentos_disponibles)
    
    # Aplicar filtros al DataFrame
    df_filtrado = df.copy()
    if ciudad_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Ciudad'] == ciudad_sel]
    if segmento_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Segmento'] == segmento_sel]

    # 4. CÁLCULO DE KPIs PRINCIPALES
    total_ventas = df_filtrado['Valor Pedido'].sum()
    total_visitas = df_filtrado['ID_Visita'].nunique()
    total_metros = df_filtrado['Metros Pedidos'].sum()
    
    # Renderizar los KPIs en 3 columnas
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("💰 Total Ventas Logradas", f"${total_ventas:,.2f}")
    kpi2.metric("📍 Total Visitas Ejecutadas", f"{total_visitas} Clientes")
    kpi3.metric("📏 Total Metros Pedidos", f"{total_metros:,.1f} m")
    
    st.markdown("---")
    
    # 5. RENDERIZADO DE LOS GRÁFICOS INTERACTIVOS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Estado de la Etapa Comercial")
        df_etapas = df_filtrado['Etapa Comercial'].value_counts().reset_index()
        df_etapas.columns = ['Etapa', 'Cantidad']
        fig_etapas = px.bar(df_etapas, x='Cantidad', y='Etapa', orientation='h', 
                            color='Etapa', text_auto=True)
        fig_etapas.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_etapas, use_container_width=True)
        
    with col2:
        st.subheader("👗 Ventas por Segmento de Mercado")
        df_seg = df_filtrado.groupby('Segmento')['Valor Pedido'].sum().reset_index()
        fig_seg = px.pie(df_seg, values='Valor Pedido', names='Segmento', hole=0.4)
        st.plotly_chart(fig_seg, use_container_width=True)
        
    st.markdown("---")
    
    # Gráfico 3 de ancho completo al fondo
    st.subheader("📦 Efectividad: ¿Dejar Muestrario genera más Pedidos?")
    df_muestras = df_filtrado.groupby(['Muestrario', 'Genero Pedido']).size().reset_index(name='Cantidad')
    fig_muestras = px.bar(df_muestras, x='Muestrario', y='Cantidad', color='Genero Pedido', barmode='group')
    st.plotly_chart(fig_muestras, use_container_width=True)

else:
    st.info("👋 Por favor sube el archivo Excel en el campo de arriba para generar el dashboard automáticamente.")
