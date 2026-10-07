import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import re
import os
import base64
from datetime import datetime

# ==========================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Visitas comerciales - Magic Print",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CONSTANTES Y COLORES (Basados en index.html)
# ==========================================
NAVY = "#1C2363"
GREEN = "#008257"
CYAN = "#00BEEA"
BG_COLOR = "#F4F7F9"
TEXT_COLOR = "#2D2D2D"
MUTED_COLOR = "#6B7280"
LINE_COLOR = "#E1E6EC"

DEFAULT_URL = "https://script.google.com/macros/s/AKfycbyz_8q8OisAzCiXDRw9ivnol0S-Oh0fdJkR9aD8RDxPCz4wvFmoShLXmwSf-qdUZzTD9Q/exec"

SEGC = [NAVY, GREEN, CYAN, '#5b66b8', '#4fb596', '#e0457b', '#8a5fd0', '#f08a24', '#7fdcf3', '#2f6fa8']

# Obtener logo en base64
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except:
            pass
    # Fallback predeterminado Magic Print
    return ""

LOGO_B64 = get_logo_base64()

# Intentar importar plotly para gráficos interactivos idénticos a Chart.js
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==========================================
# ESTILOS CSS (Réplica exacta de index.html)
# ==========================================
st.markdown(f"""
<style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
        font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    }}

    /* Contenedor principal sin padding superior */
    .block-container {{
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 60px !important;
        max-width: 1320px !important;
        margin: 0 auto !important;
    }}

    /* Header superior */
    .header-top {{
        background: #ffffff;
        border-bottom: 1px solid {LINE_COLOR};
        padding: 16px 2rem;
        margin: 0 -2rem 0 -2rem;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .header-logo {{
        width: 68px;
        height: 68px;
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .header-brand h1 {{
        margin: 0 !important;
        padding: 0 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        color: {NAVY} !important;
        line-height: 1.2 !important;
    }}
    .header-brand p {{
        margin: 3px 0 0 0 !important;
        color: {MUTED_COLOR} !important;
        font-size: 14px !important;
    }}

    /* Barra de control azul Navy */
    .header-bar {{
        background: {NAVY};
        border-top: 3px solid {CYAN};
        padding: 12px 2rem;
        margin: 0 -2rem 18px -2rem;
        color: white;
    }}

    /* Tarjetas KPI (idénticas a index.html) */
    .kpi-container {{
        display: grid;
        grid-template-columns: 1fr 1fr 1.6fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 16px;
    }}
    @media (max-width: 900px) {{
        .kpi-container {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    .kpi-card {{
        background: #ffffff;
        border: 1px solid {LINE_COLOR};
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        position: relative;
    }}
    .kpi-card.b-navy {{ border-top: 4px solid {NAVY}; }}
    .kpi-card.b-green {{ border-top: 4px solid {GREEN}; }}
    .kpi-card.b-cyan {{ border-top: 4px solid {CYAN}; }}

    .kpi-label {{
        display: block;
        color: {MUTED_COLOR};
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 2px;
    }}
    .kpi-value {{
        display: block;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.2;
        color: {NAVY};
        margin: 2px 0;
        white-space: nowrap;
    }}
    .kpi-subtext {{
        color: {MUTED_COLOR};
        font-size: 12px;
    }}

    /* Contenedor de filtros */
    .filters-box {{
        background: #ffffff;
        border: 1px solid {LINE_COLOR};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}

    /* Tarjetas de gráficos */
    .chart-card {{
        background: #ffffff;
        border: 1px solid {LINE_COLOR};
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 14px;
        height: 100%;
    }}
    .chart-card h2 {{
        margin: 0 0 10px 0 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: {NAVY} !important;
    }}
    .chart-sub {{
        margin: -6px 0 10px 0;
        color: {MUTED_COLOR};
        font-size: 13px;
    }}
    .chart-sub b {{
        color: {GREEN};
        font-size: 14px;
    }}

    /* Barras de segmento estilo HTML */
    .seg-row {{
        display: grid;
        grid-template-columns: minmax(110px, 160px) 1fr auto;
        gap: 10px;
        align-items: center;
        font-size: 12.5px;
        margin-bottom: 7px;
    }}
    .seg-name {{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-weight: 600;
        color: {TEXT_COLOR};
    }}
    .seg-track {{
        height: 9px;
        background: #eef1f5;
        border-radius: 6px;
        overflow: hidden;
    }}
    .seg-fill {{
        height: 100%;
        border-radius: 6px;
    }}
    .seg-val {{
        font-weight: 700;
        color: {NAVY};
        white-space: nowrap;
        text-align: right;
        min-width: 75px;
        font-size: 12px;
    }}

    /* Pills inferiores de segmento */
    .pills-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 14px;
    }}
    .pill-card {{
        border-radius: 10px;
        text-align: center;
        padding: 8px;
        border: 1px solid;
    }}
    .pill-card small {{
        display: block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .04em;
    }}
    .pill-card b {{
        font-size: 18px;
        font-weight: 800;
    }}
    .pill-card.green {{
        background: #e6f4ee;
        border-color: #9fd5bf;
        color: {GREEN};
    }}
    .pill-card.cyan {{
        background: #e6f8fd;
        border-color: #9fe0f3;
        color: {NAVY};
    }}

    /* Badge de pedidos en tabla */
    .order-pill {{
        display: inline-block;
        white-space: nowrap;
        background: #e6f4ee;
        color: {GREEN};
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 12.5px;
        font-weight: 700;
    }}

    /* Botones de acción */
    .stButton > button {{
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: 1px solid {LINE_COLOR} !important;
        background: #ffffff !important;
        color: {NAVY} !important;
        padding: 6px 14px !important;
    }}
    .stButton > button:hover {{
        border-color: {NAVY} !important;
        background: #eff6ff !important;
    }}

    /* Footer */
    .custom-footer {{
        margin-top: 30px;
        border-top: 1px solid {LINE_COLOR};
        text-align: center;
        padding: 16px 0;
        font-size: 13px;
        color: {MUTED_COLOR};
        background: #ffffff;
        margin: 30px -2rem 0 -2rem;
    }}
    .custom-footer b {{
        color: {NAVY};
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE CARGA Y NORMALIZACIÓN DE DATOS
# ==========================================
def parse_date_clean(val):
    """Normaliza fechas desde Excel (números seriales), strings ISO o DD/MM/YYYY a YYYY-MM-DD."""
    if pd.isna(val) or val == "" or val is None:
        return ""
    if isinstance(val, (int, float)):
        try:
            return (pd.to_datetime('1899-12-30') + pd.to_timedelta(val, 'D')).strftime('%Y-%m-%d')
        except:
            pass
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt):
            return dt.strftime('%Y-%m-%d')
    except:
        pass
    return ""

def clean_number(v):
    """Extrae valores numéricos limpios."""
    if isinstance(v, (int, float)):
        return float(v) if pd.notna(v) else 0.0
    s = str(v or '').strip()
    s = re.sub(r'[^\d.-]', '', s)
    try:
        return float(s) if s and s != '-' else 0.0
    except:
        return 0.0

def noacc(s):
    """Normaliza texto sin acentos y en minúsculas."""
    s = str(s or '').strip().lower()
    return re.sub(r'[\u0300-\u036f]', '', s)

@st.cache_data(ttl=180)
def fetch_from_api(url):
    """Consulta la API de Google Apps Script con timeout y seguimiento de redirecciones."""
    try:
        res = requests.get(url, timeout=12, allow_redirects=True)
        if res.status_code == 200:
            json_data = res.json()
            if json_data.get('ok') and 'data' in json_data:
                return json_data['data']
    except Exception as e:
        pass
    return None

def load_local_fallback():
    """Carga datos desde archivos locales si la API no está disponible."""
    possible_files = [
        "visitas_limpias.csv",
        "datos_visitas.csv",
        "Ajustado VISITA_COLOMBIAMODA_MODELO_DASHBOARD.xlsx",
        "VISITA COLOMBIAMODA.xlsx"
    ]
    for pf in possible_files:
        full_p = os.path.join(os.path.dirname(__file__), pf)
        if os.path.exists(full_p):
            try:
                if pf.endswith('.csv'):
                    df = pd.read_csv(full_p)
                else:
                    df = pd.read_excel(full_p)
                return df.to_dict(orient='records')
            except:
                continue
    return []

def prepare_dataframe(records):
    """Estandariza los registros para que coincidan con la estructura de index.html."""
    processed = []
    for r in records:
        # Excluir fila de control sin ID_Visita si aplica
        id_vis = str(r.get('ID_Visita', '')).strip()
        if not id_vis or id_vis == 'nan' or not re.search(r'\d+', id_vis):
            if not r.get('Cliente'):
                continue

        f = parse_date_clean(r.get('Fecha_Visita'))
        cli = str(r.get('Cliente', '')).strip()
        tipo = str(r.get('TIPO CLIENTE', '')).strip()
        ciu = str(r.get('Ciudad', '')).strip().upper()
        seg = str(r.get('Segmento', '')).strip().upper()
        
        # Pedido boolean
        gen_ped = noacc(r.get('Genero Pedido', ''))
        ped = ('si' in gen_ped)
        
        est = str(r.get('Estado del Pedido', '')).strip()
        val = clean_number(r.get('Valor Pedido', 0))
        m = clean_number(r.get('Metros Pedidos', 0))
        etapa = str(r.get('Etapa Comercial', '')).strip()
        obs = str(r.get('Observaciones', '')).strip()

        processed.append({
            'f': f,
            'cli': cli,
            'tipo': tipo if tipo else 'Sin dato',
            'ciu': ciu if ciu else 'SIN DATO',
            'seg': seg if seg else 'SIN DATO',
            'ped': ped,
            'est': est if est else 'Sin dato',
            'val': val,
            'm': m,
            'etapa': etapa if etapa else 'Sin dato',
            'obs': obs
        })
    return pd.DataFrame(processed)

# ==========================================
# GESTIÓN DE ESTADO (SESSION STATE)
# ==========================================
if 'api_url' not in st.session_state:
    st.session_state.api_url = DEFAULT_URL
if 'last_status' not in st.session_state:
    st.session_state.last_status = ("Conectando a la fuente de datos...", "info")
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0

# ==========================================
# ENCABEZADO SUPERIOR (Marca y Logo)
# ==========================================
logo_img_tag = f'<img src="data:image/jpeg;base64,{LOGO_B64}" class="header-logo">' if LOGO_B64 else '<div class="header-logo" style="background:#1C2363;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:22px;">MP</div>'

st.markdown(f"""
<div class="header-top">
    {logo_img_tag}
    <div class="header-brand">
        <h1>Visitas comerciales</h1>
        <p>Seguimiento de visitas, pedidos y conversión</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# BARRA DE CONEXIÓN Y CONTROLES (NAVY BAR)
# ==========================================
with st.container():
    st.markdown('<div class="header-bar">', unsafe_allow_html=True)
    c_url, c_btn, c_stat = st.columns([5.5, 1.5, 3], vertical_alignment="center")
    
    with c_url:
        url_input = st.text_input(
            "URL Apps Script",
            value=st.session_state.api_url,
            label_visibility="collapsed",
            placeholder="Pega aquí el link de Apps Script (termina en /exec)"
        )
        if url_input != st.session_state.api_url:
            st.session_state.api_url = url_input

    with c_btn:
        if st.button("Actualizar datos", use_container_width=True, type="primary"):
            st.session_state.refresh_trigger += 1
            st.cache_data.clear()

    with c_stat:
        status_text, status_type = st.session_state.last_status
        stat_color = "#7fe3bd" if status_type == "ok" else ("#ffb4b4" if status_type == "err" else "#b9bff0")
        st.markdown(f'<div style="font-size:12.5px; color:{stat_color}; font-weight:500;">{status_text}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Opción opcional para cargar archivo manual si se desea
with st.expander("📁 ¿Deseas cargar un archivo Excel o CSV manual en lugar del link en línea?", expanded=False):
    uploaded_file = st.file_uploader("Subir base de datos de visitas", type=['xlsx', 'xls', 'csv'])

# ==========================================
# CARGA DE DATOS
# ==========================================
raw_records = []
source_name = ""

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_up = pd.read_csv(uploaded_file)
        else:
            df_up = pd.read_excel(uploaded_file)
        raw_records = df_up.to_dict(orient='records')
        source_name = f"Archivo subido: {uploaded_file.name}"
        st.session_state.last_status = (f"Cargado desde {uploaded_file.name} · {len(raw_records)} registros", "ok")
    except Exception as e:
        st.error(f"Error al leer archivo subido: {e}")

if not raw_records and st.session_state.api_url:
    api_data = fetch_from_api(st.session_state.api_url)
    if api_data:
        raw_records = api_data
        source_name = "Google Apps Script en vivo"
        now_str = datetime.now().strftime('%H:%M:%S')
        st.session_state.last_status = (f"Actualizado a las {now_str} · {len(raw_records)} registros", "ok")
    else:
        # Fallback local
        raw_records = load_local_fallback()
        if raw_records:
            source_name = "Copia local de respaldo"
            st.session_state.last_status = (f"Usando datos locales de respaldo · {len(raw_records)} registros", "ok")
        else:
            st.session_state.last_status = ("No se pudo conectar a la URL ni cargar datos locales", "err")

if not raw_records:
    st.warning("No hay datos disponibles para mostrar. Revisa la URL de Apps Script o sube un archivo Excel.")
    st.stop()

# Procesar DataFrame
df = prepare_dataframe(raw_records)

if df.empty:
    st.warning("El archivo de datos no contiene registros válidos.")
    st.stop()

# ==========================================
# PANEL DE FILTROS DINÁMICOS (Idéntico a index.html)
# ==========================================
st.markdown('<div class="filters-box">', unsafe_allow_html=True)

# Obtener valores únicos ordenados para cada filtro
unique_ciudades = sorted([c for c in df['ciu'].unique() if c])
unique_segmentos = sorted([s for s in df['seg'].unique() if s])
unique_tipos = sorted([t for t in df['tipo'].unique() if t])
unique_etapas = sorted([e for e in df['etapa'].unique() if e])
unique_estados = sorted([es for es in df['est'].unique() if es])

dates_with_val = [d for d in df['f'].unique() if d]
min_date = min(dates_with_val) if dates_with_val else None
max_date = max(dates_with_val) if dates_with_val else None

# Fila de filtros
col_f1, col_f2, col_f3, col_f4, col_f5, col_f6, col_f7, col_f8 = st.columns([1.3, 1.3, 1.4, 1.4, 1.4, 1.4, 1.4, 1.0], vertical_alignment="center")

with col_f1:
    f_desde = st.date_input(
        "Desde",
        value=datetime.strptime(min_date, '%Y-%m-%d').date() if min_date else None,
        key="filtro_desde",
        help="Fecha inicial"
    )

with col_f2:
    f_hasta = st.date_input(
        "Hasta",
        value=datetime.strptime(max_date, '%Y-%m-%d').date() if max_date else None,
        key="filtro_hasta",
        help="Fecha final"
    )

with col_f3:
    sel_ciu = st.selectbox("Ciudad", ["Todas"] + unique_ciudades, key="filtro_ciu")

with col_f4:
    sel_seg = st.selectbox("Segmento", ["Todos"] + unique_segmentos, key="filtro_seg")

with col_f5:
    sel_tipo = st.selectbox("Tipo de cliente", ["Todos"] + unique_tipos, key="filtro_tipo")

with col_f6:
    sel_etapa = st.selectbox("Etapa comercial", ["Todas"] + unique_etapas, key="filtro_etapa")

with col_f7:
    sel_est = st.selectbox("Estado del pedido", ["Todos"] + unique_estados, key="filtro_est")

with col_f8:
    st.write("") # Alineación vertical
    if st.button("Limpiar", help="Restablecer todos los filtros", use_container_width=True):
        st.session_state.filtro_ciu = "Todas"
        st.session_state.filtro_seg = "Todos"
        st.session_state.filtro_tipo = "Todos"
        st.session_state.filtro_etapa = "Todas"
        st.session_state.filtro_est = "Todos"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# APLICAR FILTROS AL DATAFRAME
# ==========================================
df_filt = df.copy()

if f_desde:
    d1_str = f_desde.strftime('%Y-%m-%d')
    df_filt = df_filt[df_filt['f'] >= d1_str]

if f_hasta:
    d2_str = f_hasta.strftime('%Y-%m-%d')
    df_filt = df_filt[df_filt['f'] <= d2_str]

if sel_ciu != "Todas":
    df_filt = df_filt[df_filt['ciu'] == sel_ciu]

if sel_seg != "Todos":
    df_filt = df_filt[df_filt['seg'] == sel_seg]

if sel_tipo != "Todos":
    df_filt = df_filt[df_filt['tipo'] == sel_tipo]

if sel_etapa != "Todas":
    df_filt = df_filt[df_filt['etapa'] == sel_etapa]

if sel_est != "Todos":
    df_filt = df_filt[df_filt['est'] == sel_est]

# ==========================================
# CÁLCULO DE KPIS
# ==========================================
n_visitas = len(df_filt)
pedidos_count = int(df_filt['ped'].sum())
conversion_pct = (pedidos_count / n_visitas * 100) if n_visitas > 0 else 0.0

total_valor = df_filt['val'].sum()
ticket_prom = (total_valor / pedidos_count) if pedidos_count > 0 else 0.0
ticket_str = f"Ticket promedio $ {ticket_prom:,.0f}".replace(",", ".") if pedidos_count > 0 else "Sin pedidos"

total_metros = df_filt['m'].sum()

export_count = int(df_filt['seg'].str.contains(r'\(EXP\)', regex=True).sum())
export_pct = (export_count / n_visitas * 100) if n_visitas > 0 else 0.0

# Formato moneda COP
valor_str = f"$ {total_valor:,.0f}".replace(",", ".")

# Renderizado HTML de los 5 KPIs
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card b-navy">
        <span class="kpi-label">Visitas</span>
        <b class="kpi-value">{n_visitas:,}</b>
        <small class="kpi-subtext">En el filtro actual</small>
    </div>
    <div class="kpi-card b-green">
        <span class="kpi-label">Pedidos</span>
        <b class="kpi-value">{pedidos_count:,}</b>
        <small class="kpi-subtext">{conversion_pct:.1f}% de conversión</small>
    </div>
    <div class="kpi-card b-navy">
        <span class="kpi-label">Valor de pedidos</span>
        <b class="kpi-value">{valor_str}</b>
        <small class="kpi-subtext">{ticket_str}</small>
    </div>
    <div class="kpi-card b-green">
        <span class="kpi-label">Metros pedidos</span>
        <b class="kpi-value">{total_metros:,.0f}</b>
        <small class="kpi-subtext">En el filtro actual</small>
    </div>
    <div class="kpi-card b-cyan">
        <span class="kpi-label">Visitas exportación</span>
        <b class="kpi-value">{export_pct:.0f}%</b>
        <small class="kpi-subtext">{export_count} de {n_visitas} visitas</small>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# FILA 1 DE GRÁFICOS: TENDENCIA & ETAPA
# ==========================================
col_g1, col_g2 = st.columns([1.6, 1.0])

# Gráfico 1: Visitas y valor de pedidos por día
with col_g1:
    st.markdown('<div class="chart-card"><h2>Visitas y valor de pedidos por día</h2>', unsafe_allow_html=True)
    
    if n_visitas > 0:
        # Agrupar por fecha
        df_trend = df_filt[df_filt['f'] != ""].groupby('f').agg(
            visitas=('cli', 'count'),
            valor=('val', 'sum')
        ).reset_index().sort_values('f')
        
        # Formatear etiquetas de fecha a DD/MM
        df_trend['fecha_lbl'] = df_trend['f'].apply(lambda x: f"{x[8:10]}/{x[5:7]}")

        if HAS_PLOTLY:
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Barras para visitas
            fig_trend.add_trace(
                go.Bar(
                    x=df_trend['fecha_lbl'],
                    y=df_trend['visitas'],
                    name="Visitas",
                    marker_color=CYAN,
                    marker_line_width=0,
                    opacity=0.9
                ),
                secondary_y=False
            )
            
            # Línea para valor de pedidos
            fig_trend.add_trace(
                go.Scatter(
                    x=df_trend['fecha_lbl'],
                    y=df_trend['valor'],
                    name="Valor pedidos ($)",
                    mode="lines+markers",
                    line=dict(color=GREEN, width=3, shape='spline'),
                    marker=dict(size=7, color=GREEN)
                ),
                secondary_y=True
            )
            
            fig_trend.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=290,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                font=dict(family="Segoe UI", size=12, color=TEXT_COLOR)
            )
            fig_trend.update_yaxes(title_text="Visitas", secondary_y=False, showgrid=True, gridcolor="#F1F5F9", rangemode="tozero")
            fig_trend.update_yaxes(title_text="Valor ($ COP)", secondary_y=True, showgrid=False, rangemode="tozero")
            
            st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        else:
            st.bar_chart(df_trend.set_index('fecha_lbl')[['visitas']], color=CYAN, height=270)
    else:
        st.info("No hay datos en el rango seleccionado.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Gráfico 2: Visitas por etapa comercial
with col_g2:
    st.markdown('<div class="chart-card"><h2>Visitas por etapa comercial</h2>', unsafe_allow_html=True)
    
    if n_visitas > 0:
        etapa_counts = df_filt['etapa'].value_counts().reset_index()
        etapa_counts.columns = ['etapa', 'conteo']
        etapa_counts = etapa_counts.sort_values('conteo', ascending=True)

        if HAS_PLOTLY:
            fig_etapa = go.Figure(go.Bar(
                x=etapa_counts['conteo'],
                y=etapa_counts['etapa'],
                orientation='h',
                marker_color=NAVY,
                text=etapa_counts['conteo'],
                textposition='inside',
                insidetextanchor='end',
                textfont=dict(color='white', size=12, family="Segoe UI")
            ))
            fig_etapa.update_layout(
                margin=dict(l=10, r=20, t=10, b=10),
                height=290,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_etapa, use_container_width=True, config={'displayModeBar': False})
        else:
            st.bar_chart(etapa_counts.set_index('etapa'), color=NAVY, height=270)
    else:
        st.info("Sin registros.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FILA 2 DE GRÁFICOS: ALCANCE GEOGRÁFICO & SEGMENTOS
# ==========================================
col_g3, col_g4 = st.columns([1.0, 1.0])

# Gráfico 3: Alcance geográfico de las visitas
with col_g3:
    if n_visitas > 0:
        ciu_counts = df_filt['ciu'].value_counts()
        real_ciudades = len([c for c in ciu_counts.index if c != 'SIN DATO'])
        sub_text = f"<b>{real_ciudades}</b> {'ciudad impactada' if real_ciudades == 1 else 'ciudades impactadas'} · {n_visitas} visitas"
    else:
        sub_text = "0 ciudades"

    st.markdown(f'<div class="chart-card"><h2>Alcance geográfico de las visitas</h2><p class="chart-sub">{sub_text}</p>', unsafe_allow_html=True)

    if n_visitas > 0:
        top_ciu = ciu_counts.head(8)
        rest_val = ciu_counts.iloc[8:].sum() if len(ciu_counts) > 8 else 0
        
        labels_ciu = list(top_ciu.index)
        vals_ciu = list(top_ciu.values)
        colors_ciu = [GREEN] * len(labels_ciu)
        
        if rest_val > 0:
            labels_ciu.append(f"Otras ({len(ciu_counts)-8} ciudades)")
            vals_ciu.append(rest_val)
            colors_ciu.append(CYAN)

        # Invertir para mostrar de mayor a menor en gráfico horizontal
        df_geo_plot = pd.DataFrame({
            'ciudad': labels_ciu,
            'visitas': vals_ciu,
            'color': colors_ciu
        }).iloc[::-1]

        df_geo_plot['pct'] = (df_geo_plot['visitas'] / n_visitas * 100).round(1)
        df_geo_plot['text_label'] = df_geo_plot.apply(lambda r: f"{int(r['visitas'])} · {r['pct']:.0f}%", axis=1)

        if HAS_PLOTLY:
            fig_geo = go.Figure(go.Bar(
                x=df_geo_plot['visitas'],
                y=df_geo_plot['ciudad'],
                orientation='h',
                marker_color=df_geo_plot['color'],
                text=df_geo_plot['text_label'],
                textposition='outside',
                textfont=dict(color=NAVY, size=11, family="Segoe UI")
            ))
            fig_geo.update_layout(
                margin=dict(l=10, r=45, t=10, b=10),
                height=300,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_geo, use_container_width=True, config={'displayModeBar': False})
        else:
            st.bar_chart(df_geo_plot.set_index('ciudad')['visitas'], color=GREEN, height=290)
    else:
        st.info("Sin datos geográficos.")

    st.markdown('</div>', unsafe_allow_html=True)

# Gráfico 4: Visitas por segmento con barras y pills
with col_g4:
    st.markdown("""
    <div class="chart-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h2 style="margin:0;">Visitas por segmento</h2>
            <span style="background:#eef0fa; color:#1C2363; font-size:11px; font-weight:700; border-radius:6px; padding:2px 8px;">Top 10</span>
        </div>
    """, unsafe_allow_html=True)

    if n_visitas > 0:
        seg_counts = df_filt['seg'].value_counts()
        top_10 = seg_counts.head(10)
        max_v = max(top_10.values) if len(top_10) > 0 else 1
        
        # Generar lista de barras en HTML
        seg_html = ""
        for i, (seg_name, seg_val) in enumerate(top_10.items()):
            c_color = SEGC[i % len(SEGC)]
            width_pct = (seg_val / max_v) * 100
            pct_val = (seg_val / n_visitas) * 100
            seg_html += f"""
            <div class="seg-row">
                <span class="seg-name" title="{seg_name}">{seg_name}</span>
                <span class="seg-track"><i class="seg-fill" style="display:block; width:{width_pct}%; background:{c_color};"></i></span>
                <span class="seg-val">{seg_val} ({pct_val:.1f}%)</span>
            </div>
            """
        
        # Con pedido / Sin pedido pills
        p_count = pedidos_count
        sp_count = n_visitas - p_count
        p_pct = (p_count / n_visitas * 100) if n_visitas > 0 else 0
        sp_pct = (sp_count / n_visitas * 100) if n_visitas > 0 else 0

        pills_html = f"""
        <div class="pills-grid">
            <div class="pill-card green">
                <small>CON PEDIDO</small>
                <b>{p_count} ({p_pct:.1f}%)</b>
            </div>
            <div class="pill-card cyan">
                <small>SIN PEDIDO</small>
                <b>{sp_count} ({sp_pct:.1f}%)</b>
            </div>
        </div>
        """

        st.markdown(f'<div style="margin-top:4px;">{seg_html}</div>{pills_html}', unsafe_allow_html=True)
    else:
        st.info("Sin datos de segmentos.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECCIÓN: ÚLTIMAS VISITAS (TABLA ESTILIZADA)
# ==========================================
st.markdown('<div class="chart-card" style="margin-top:14px;"><h2>Últimas visitas</h2>', unsafe_allow_html=True)

if n_visitas > 0:
    # Ordenar por fecha descendente
    df_table = df_filt.sort_values('f', ascending=False).copy()
    
    # Formatear columnas
    df_table['Fecha'] = df_table['f'].apply(lambda x: f"{x[8:10]}/{x[5:7]}/{x[0:4]}" if x else "")
    df_table['Cliente'] = df_table['cli']
    df_table['Ciudad'] = df_table['ciu']
    df_table['Etapa'] = df_table['etapa']
    df_table['Pedido'] = df_table.apply(
        lambda r: f'<span class="order-pill">$ {r["val"]:,.0f}</span>' if r['ped'] else '—',
        axis=1
    )
    df_table['Observaciones'] = df_table['obs']

    # Renderizar tabla HTML estilizada
    rows_html = ""
    for _, row in df_table.iterrows():
        rows_html += f"""
        <tr>
            <td style="white-space:nowrap;">{row['Fecha']}</td>
            <td><strong>{row['Cliente']}</strong></td>
            <td>{row['Ciudad']}</td>
            <td>{row['Etapa']}</td>
            <td style="white-space:nowrap;">{row['Pedido']}</td>
            <td style="font-size:12.5px; color:#475569;">{row['Observaciones']}</td>
        </tr>
        """

    st.markdown(f"""
    <div style="overflow-x:auto;">
        <table style="width:100%; border-collapse:collapse; font-size:13.5px;">
            <thead>
                <tr style="border-bottom:2px solid {LINE_COLOR};">
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Fecha</th>
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Cliente</th>
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Ciudad</th>
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Etapa</th>
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Pedido</th>
                    <th style="text-align:left; color:{NAVY}; padding:8px 6px;">Observaciones</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Botones de exportación (CSV y Excel)
    st.markdown('<div style="margin-top:14px;">', unsafe_allow_html=True)
    c_exp_csv, c_exp_xls, c_spacer = st.columns([1.5, 1.5, 7])
    
    with c_exp_csv:
        csv_data = df_filt.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name="visitas_comerciales_filtradas.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c_exp_xls:
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            df_filt.to_excel(writer, index=False, sheet_name='Visitas Filtradas')
        st.download_button(
            label="Descargar Excel",
            data=output_excel.getvalue(),
            file_name="visitas_comerciales_filtradas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("No hay visitas con los filtros seleccionados.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER FIJO
# ==========================================
st.markdown("""
<div class="custom-footer">
    <b>Magic Print</b> · Dashboard comercial de visitas · Desarrollado para la Dirección General y Comercial
</div>
""", unsafe_allow_html=True)
