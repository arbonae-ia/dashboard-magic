import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard Ejecutivo Magic Print", layout="wide")

# Estilos CSS globales para empaquetar tablas y métricas en contenedores gris claro con negrilla masiva
st.markdown("""
    <style>
    /* Tarjetas de Métricas en cuadros gris suave */
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        font-size: 26px !important;
        color: #1a1c23 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #555555 !important;
    }
    /* Contenedor gris suave para las tablas */
    .contenedor-tabla {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    /* Títulos unificados */
    .titulo-seccion {
        font-size: 16px;
        font-weight: 700;
        color: #1a1c23;
        margin-bottom: 15px;
        border-left: 4px solid #b71c1c;
        padding-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. LOGO CORPORATIVO Y FILTROS EN LA BARRA LATERAL
# Colocamos el logo en la parte superior izquierda de la barra lateral usando el enlace de la imagen cargada
st.sidebar.image("https://githubusercontent.com", errors="ignore")
# Nota: Si el enlace superior expira, puedes subir tu imagen a GitHub en la misma carpeta y llamarla como st.sidebar.image("image_W9KVU6.png")

st.sidebar.markdown("### 🔍 Filtros Ejecutivos")

# Carga del Archivo Excel en la barra lateral
archivo = st.sidebar.file_uploader("Cargar Base de Datos (Excel)", type=["xlsx", "xls"])

if archivo is not None:
    # Cargar y preprocesar los datos
    df = pd.read_excel(archivo)
    df['Valor Pedido'] = pd.to_numeric(df['Valor Pedido'], errors='coerce').fillna(0)
    df['Metros Pedidos'] = pd.to_numeric(df['Metros Pedidos'], errors='coerce').fillna(0)
    
    # Selectores dinámicos para la segmentación multidimensional
    ciudades_disponibles = ["Todas"] + list(df['Ciudad'].dropna().unique())
    ciudad_sel = st.sidebar.selectbox("Ciudad / Zona:", ciudades_disponibles)
    
    segmentos_disponibles = ["Todos"] + list(df['Segmento'].dropna().unique())
    segmento_sel = st.sidebar.selectbox("Segmento de Mercado:", segmentos_disponibles)
    
    # Aplicación estricta de filtros dinámicos
    df_filtrado = df.copy()
    if ciudad_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Ciudad'] == ciudad_sel]
    if segmento_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Segmento'] == segmento_sel]

    # Header Principal con el Nombre de la Compañía
    st.title("📊 Magic Print — Informe Comercial Ejecutivo")
    st.markdown("Visión general de visitas, conversión y relaciones comerciales.")
    st.markdown("---")

    # 3. MBL DE MÉTRICAS (KPIs PRINCIPALES) EN CUADROS GRIS SUAVE
    total_ventas = df_filtrado['Valor Pedido'].sum()
    total_visitas = df_filtrado['ID_Visita'].nunique()
    total_metros = df_filtrado['Metros Pedidos'].sum()
    
    visitas_con_pedido = df_filtrado[df_filtrado['Valor Pedido'] > 0]['ID_Visita'].nunique()
    efectividad = (visitas_con_pedido / total_visitas * 100) if total_visitas > 0 else 0
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        with st.container(border=True):
            st.metric(label="TOTAL FACTURADO", value=f"$ {total_ventas:,.0f}")
    with kpi2:
        with st.container(border=True):
            st.metric(label="TOTAL VISITAS", value=f"{total_visitas}")
    with kpi3:
        with st.container(border=True):
            st.metric(label="TOTAL METROS PEDIDOS", value=f"{total_metros:,.1f} m")
    with kpi4:
        with st.container(border=True):
            st.metric(label="CONVERSIÓN COMERCIAL", value=f"{efectividad:.1f}%")

    st.markdown("---")

    # 4. CONFIGURACIÓN DE FILAS PARA LOS GRÁFICOS (EMPAQUETADOS EN CONTENEDORES GRIS SUAVE)
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        with st.container(border=True): # Fondo gris suave provisto por el contenedor nativo
            st.markdown('<div class="titulo-seccion">Visitas por Ciudad / Zona</div>', unsafe_allow_html=True)
            
            # Preparación de datos agregando volumen y porcentajes
            df_ciudad_g = df_filtrado['Ciudad'].value_counts().reset_index()
            df_ciudad_g.columns = ['Ciudad', 'Visitas']
            df_ciudad_g['Porcentaje'] = (df_ciudad_g['Visitas'] / df_ciudad_g['Visitas'].sum() * 100).round(1)
            df_ciudad_g['Texto_Etiqueta'] = df_ciudad_g['Visitas'].astype(str) + " (" + df_ciudad_g['Porcentaje'].astype(str) + "%)"
            
            fig_ciudad = px.bar(
                df_ciudad_g, x='Visitas', y='Ciudad', orientation='h',
                text='Texto_Etiqueta', color_discrete_sequence=['#24b4c4']
            )
            # Limpieza estricta de ejes, rótulos y escalas del eje X según requerimiento
            fig_ciudad.update_layout(
                xaxis_title="", yaxis_title="", showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10), height=300, paper_bgcolor='#f8f9fa', plot_bgcolor='#f8f9fa'
            )
            fig_ciudad.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
            fig_ciudad.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_ciudad, use_container_width=True)

    with col_g2:
        with st.container(border=True):
            st.markdown('<div class="titulo-seccion">Composición por Segmento de Mercado</div>', unsafe_allow_html=True)
            
            # Filtrar estrictamente la serie para mostrar solo los datos que tienen valores > 0
            df_seg = df_filtrado.groupby('Segmento')['Valor Pedido'].sum().reset_index()
            df_seg = df_seg[df_seg['Valor Pedido'] > 0]
            
            if not df_seg.empty:
                # Gráfico en anillo delgado (Donut Chart) con etiquetas en porcentaje
                fig_seg = px.pie(df_seg, values='Valor Pedido', names='Segmento', hole=0.75)
                fig_seg.update_traces(textinfo='percent', hoverinfo='label+value')
                fig_seg.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), height=300, 
                    paper_bgcolor='#f8f9fa', legend=dict(orientation="h", y=-0.1)
                )
                st.plotly_chart(fig_seg, use_container_width=True)
            else:
                st.caption("No se registran transacciones monetarias en este periodo para graficar.")

    st.markdown("---")

    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        with st.container(border=True):
            st.markdown('<div class="titulo-seccion">Tipo de Cliente & Proceso Comercial</div>', unsafe_allow_html=True)
            
            df_tipo = df_filtrado['TIPO CLIENTE'].value_counts().reset_index()
            df_tipo.columns = ['Tipo', 'Cantidad']
            df_tipo['Porcentaje'] = (df_tipo['Cantidad'] / df_tipo['Cantidad'].sum() * 100).round(1)
            df_tipo['Texto_Etiqueta'] = df_tipo['Cantidad'].astype(str) + " (" + df_tipo['Porcentaje'].astype(str) + "%)"
            
            fig_tipo = px.bar(
                df_tipo, x='Cantidad', y='Tipo', orientation='h',
                text='Texto_Etiqueta', color_discrete_sequence=['#9c27b0']
            )
            fig_tipo.update_layout(
                xaxis_title="", yaxis_title="", showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10), height=250, paper_bgcolor='#f8f9fa', plot_bgcolor='#f8f9fa'
            )
            fig_tipo.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
            fig_tipo.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_tipo, use_container_width=True)

    with col_g4:
        with st.container(border=True):
            st.markdown('<div class="titulo-seccion">Estado de la Etapa Comercial</div>', unsafe_allow_html=True)
            
            df_etapas = df_filtrado['Etapa Comercial'].value_counts().reset_index()
            df_etapas.columns = ['Etapa', 'Cantidad']
            df_etapas['Porcentaje'] = (df_etapas['Cantidad'] / df_etapas['Cantidad'].sum() * 100).round(1)
            df_etapas['Texto_Etiqueta'] = df_etapas['Cantidad'].astype(str) + " (" + df_etapas['Porcentaje'].astype(str) + "%)"
            
            fig_etapas = px.bar(
                df_etapas, x='Cantidad', y='Etapa', orientation='h',
                text='Texto_Etiqueta', color_discrete_sequence=['#e91e63']
            )
            fig_etapas.update_layout(
                xaxis_title="", yaxis_title="", showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10), height=250, paper_bgcolor='#f8f9fa', plot_bgcolor='#f8f9fa'
            )
            fig_etapas.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
            fig_etapas.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_etapas, use_container_width=True)

    st.markdown("---")

    # 5. TABLA SOBRE RECTÁNGULO GRIS CLARO CON TAMAÑO CONTROLADO
    st.markdown('<div class="contenedor-tabla">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-seccion">💵 Detalle de Clientes que Generaron Pedidos Facturados</div>', unsafe_allow_html=True)
    
    clientes_compraron = df_filtrado[df_filtrado['Valor Pedido'] > 0]
    
    if not clientes_compraron.empty:
        columnas_interes = ['Cliente', 'Ciudad', 'Segmento', 'No. Factura', 'Valor Pedido', 'Metros Pedidos', 'Observaciones']
        df_tabla = clientes_compraron[columnas_interes].sort_values(by='Valor Pedido', ascending=False)
        # Ajustamos el formato visual para que la tabla no sea excesivamente grande
        st.dataframe(df_tabla, use_container_width=True, height=250)
    else:

