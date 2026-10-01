import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard de Visitas Comerciales", layout="wide")
st.title("Control de Gestión y Control Comercial")
st.markdown("Tablero integral para la evaluación de la gestión de ventas y visitas.")

# 2. CARGA DEL ARCHIVO EXCEL
archivo = st.file_uploader("Por favor sube el archivo Excel de las visitas", type=["xlsx", "xls"])

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
    
    visitas_con_pedido = df_filtrado[df_filtrado['Valor Pedido'] > 0]['ID_Visita'].nunique()
    efectividad = (visitas_con_pedido / total_visitas * 100) if total_visitas > 0 else 0
    
    # --- ARANDELAS VISUALES: Enlazar iconos clásicos y forzar negrilla limpia ---
    st.markdown("""
        <!-- Cargamos la librería de iconos clásicos FontAwesome desde internet -->
        <link rel="stylesheet" href="https://cloudflare.com">
        
        <style>
        /* Forzar los números de las métricas en negrilla pura y tamaño perfecto */
        [data-testid="stMetricValue"] {
            font-weight: 800 !important;
            font-size: 24px !important;
            color: #111111 !important; /* Color negro/gris oscuro corporativo */
        }
        /* Ajustar el nombre de la métrica */
        [data-testid="stMetricLabel"] {
            display: none !important; /* Ocultamos el label nativo para usar nuestro diseño HTML limpio */
        }
        /* Estilo para nuestros títulos personalizados con icono */
        .titulo-kpi {
            font-size: 14px;
            font-weight: 500;
            color: #555555;
            margin-bottom: 5px;
        }
        .titulo-kpi i {
            margin-right: 6px;
            color: #222222; /* Iconos clásicos en negro */
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Renderizar las tarjetas ejecutivas en columnas sin desbordamiento
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        with st.container(border=True):
            st.markdown('<div class="titulo-kpi"><i class="fa-solid fa-dollar-sign"></i>Total Ventas Logradas</div>', unsafe_allow_html=True)
            st.metric(label="", value=f"${total_ventas:,.2f}")
            
    with kpi2:
        with st.container(border=True):
            st.markdown('<div class="titulo-kpi"><i class="fa-solid fa-users"></i>Total Visitas Ejecutadas</div>', unsafe_allow_html=True)
            st.metric(label="", value=f"{total_visitas} Clientes")
            
    with kpi3:
        with st.container(border=True):
            st.markdown('<div class="titulo-kpi"><i class="fa-solid fa-ruler"></i>Total Metros Pedidos</div>', unsafe_allow_html=True)
            st.metric(label="", value=f"{total_metros:,.1f} m")
            
    with kpi4:
        with st.container(border=True):
            st.markdown('<div class="titulo-kpi"><i class="fa-solid fa-chart-line"></i>Efectividad Comercial</div>', unsafe_allow_html=True)
            st.metric(label="", value=f"{efectividad:.2f}%")


    
    # 5. BLOQUE DE GRÁFICOS 1 y 2 (Lado a Lado)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Gestión de Prospectos")
        df_etapas = df_filtrado['Etapa Comercial'].value_counts().reset_index()
        df_etapas.columns = ['Etapa', 'Cantidad']
        fig_etapas = px.bar(df_etapas, x='Cantidad', y='Etapa', orientation='h', 
                            color='Etapa', text_auto=True)
        fig_etapas.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_etapas, use_container_width=True)
        
    with col2:
        st.subheader("Composición de Ventas por Categoría")
        df_seg = df_filtrado.groupby('Segmento')['Valor Pedido'].sum().reset_index()
        fig_seg = px.pie(df_seg, values='Valor Pedido', names='Segmento', hole=0.4)
        st.plotly_chart(fig_seg, use_container_width=True)
        
    st.markdown("---")
    
    # 6. BLOQUE DE GRÁFICOS 3 y 4 (Lado a Lado)
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Impacto del Muestrario en las Ventas")
        df_muestras = df_filtrado.groupby(['Muestrario', 'Genero Pedido']).size().reset_index(name='Cantidad')
        fig_muestras = px.bar(df_muestras, x='Muestrario', y='Cantidad', color='Genero Pedido', barmode='group', text_auto=True)
        st.plotly_chart(fig_muestras, use_container_width=True)
        
    with col4:
        st.subheader("Cobertura Geografica de la Visita")
        df_ciudad_g = df_filtrado['Ciudad'].value_counts().reset_index()
        df_ciudad_g.columns = ['Ciudad', 'Visitas']
        fig_ciudad = px.bar(df_ciudad_g, x='Ciudad', y='Visitas', color='Ciudad', text_auto=True)
        st.plotly_chart(fig_ciudad, use_container_width=True)

    st.markdown("---")

    # 7. LA TABLA SOLICITADA: Detalle de Clientes que Efectuaron Compras
    st.subheader("Detalle de Clientes con Compras Efectivas")
    
    # Filtrar solo los registros donde hubo venta
    clientes_compraron = df_filtrado[df_filtrado['Valor Pedido'] > 0]
    
    if not clientes_compraron.empty:
        columnas_interes = ['Cliente', 'Ciudad', 'Segmento', 'No. Factura', 'Valor Pedido', 'Metros Pedidos', 'Observaciones']
        # Mostramos la tabla formateada y bonita
        st.dataframe(clientes_compraron[columnas_interes].sort_values(by='Valor Pedido', ascending=False), use_container_width=True)
    else:
        st.warning("No se registran ventas para los filtros seleccionados.")
        
    st.markdown("---")
    
    # 8. TABLA GENERAL DE AUDITORÍA (Opcional, para ver todo el Excel si se necesita)
    st.subheader("Historial Completo de la Visitas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.info("👋 Por favor sube el archivo Excel en el campo de arriba para generar el dashboard automáticamente.")
