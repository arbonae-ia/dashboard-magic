import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import re
import os
import html
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

def esc(s):
    """Escapa caracteres HTML para renderizado seguro."""
    return html.escape(str(s if s is not None and str(s) != 'nan' else ""))

def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return ""

LOGO_B64 = get_logo_base64()

# Importar Plotly para gráficos interactivos
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==========================================
# ESTILOS CSS REFINADOS
# ==========================================
st.markdown(f"""
<style>
    /* Ocultar barra superior y menú por defecto de Streamlit */
    #MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important;
    }}

    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
        font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    }}

    /* Contenedor principal centrado */
    .block-container {{
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 50px !important;
        max-width: 1300px !important;
        margin: 0 auto !important;
    }}

    /* Estilo del Header superior */
    .header-banner {{
        background: #ffffff;
        border-bottom: 2px solid {LINE_COLOR};
        border-top: 4px solid {NAVY};
        padding: 16px 2rem;
        margin: 0 -2rem 16px -2rem;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
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

    /* Cajas y contenedores con borde (st.container border=True) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #ffffff !important;
        border: 1px solid {LINE_COLOR} !important;
        border-radius: 12px !important;
        padding: 16px 18px 20px 18px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        margin-bottom: 14px !important;
        box-sizing: border-box !important;
    }}

    /* Asegurar que las tarjetas en columnas queden alineadas y con altura armónica */
    div[data-testid="column"] > div > div[data-testid="stVerticalBlockBorderWrapper"] {{
        min-height: 440px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }}

    /* Tarjetas KPI (idénticas a index.html) */
    .kpi-container {{
        display: grid;
        grid-template-columns: 1fr 1fr 1.6fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 16px;
    }}
    @media (max-width: 960px) {{
        .kpi-container {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
    .kpi-card {{
        background: #ffffff;
        border: 1px solid {LINE_COLOR};
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
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

    /* Pie de página */
    .custom-footer {{
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid {LINE_COLOR};
        color: {MUTED_COLOR};
        font-size: 12.5px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES AUXILIARES DE LIMPIEZA
# ==========================================
def noacc(s):
    if not s or pd.isna(s):
        return ""
    s = str(s).strip()
    s = re.sub(r'[áàäâ]', 'a', s, flags=re.I)
    s = re.sub(r'[éèëê]', 'e', s, flags=re.I)
    s = re.sub(r'[íìïî]', 'i', s, flags=re.I)
    s = re.sub(r'[óòöô]', 'o', s, flags=re.I)
    s = re.sub(r'[úùüû]', 'u', s, flags=re.I)
    return s.lower()

def clean_number(v):
    if pd.isna(v) or v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace('$', '').replace('€', '').replace('COP', '').strip()
    s = re.sub(r'[^\d,\.-]', '', s)
    if not s or s == '-':
        return 0.0
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s and '.' not in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return 0.0

def parse_date_clean(v):
    if pd.isna(v) or v is None:
        return ""
    if isinstance(v, (datetime, pd.Timestamp)):
        return v.strftime('%Y-%m-%d')
    s = str(v).strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return m.group(0)
    m = re.match(r'^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    try:
        dt = pd.to_datetime(s, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return ""

def load_local_fallback():
    current_dir = os.path.dirname(__file__)
    excel_candidates = [
        "Ajustado VISITA_COLOMBIAMODA_MODELO_DASHBOARD.xlsx",
        "visitas_limpias.csv",
        "datos_visitas.csv"
    ]
    for candidate in excel_candidates:
        full_p = os.path.join(current_dir, candidate)
        if os.path.exists(full_p):
            try:
                if candidate.endswith('.xlsx'):
                    df_loc = pd.read_excel(full_p)
                else:
                    df_loc = pd.read_csv(full_p)
                return df_loc.to_dict(orient='records'), candidate
            except Exception:
                continue
    return [], "Sin archivo local"

@st.cache_data(ttl=300)
def fetch_data_and_source():
    """Carga los datos de Google Apps Script en segundo plano, o del archivo local."""
    try:
        res = requests.get(DEFAULT_URL, timeout=8, allow_redirects=True)
        if res.status_code == 200:
            j = res.json()
            if isinstance(j, dict) and j.get('ok') and isinstance(j.get('data'), list) and len(j.get('data')) > 0:
                return j['data'], f"Google Apps Script en vivo ({len(j['data'])} visitas)"
    except Exception:
        pass
    recs, name = load_local_fallback()
    if recs:
        return recs, f"Archivo local {name} ({len(recs)} visitas)"
    return [], "Sin datos"

def prepare_dataframe(records):
    if not records:
        return pd.DataFrame()
    processed = []
    for r in records:
        id_vis = str(r.get('ID_Visita', '')).strip()
        if not id_vis or id_vis == 'nan' or not re.search(r'\d+', id_vis):
            if not r.get('Cliente'):
                continue

        f = parse_date_clean(r.get('Fecha_Visita'))
        cli = str(r.get('Cliente', '')).strip()
        tipo = str(r.get('TIPO CLIENTE', '')).strip()
        ciu = str(r.get('Ciudad', '')).strip().upper()
        seg = str(r.get('Segmento', '')).strip().upper()
        
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
# ENCABEZADO SUPERIOR (Marca y Logo)
# ==========================================
logo_img_tag = f'<img src="data:image/jpeg;base64,{LOGO_B64}" class="header-logo">' if LOGO_B64 else '<div class="header-logo" style="background:#1C2363;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:22px;">MP</div>'

st.markdown(f"""
<div class="header-banner">
    {logo_img_tag}
    <div class="header-brand">
        <h1>Visitas comerciales</h1>
        <p>Seguimiento de visitas, pedidos y conversión</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SECCIÓN: CARGA DE ARCHIVO EXCEL / CSV (VISIBILIDAD DIRECTA)
# ==========================================
# Obtener fuente base por defecto
default_records, default_source = fetch_data_and_source()

with st.container(border=True):
    col_u1, col_u2 = st.columns([3.2, 1.3], vertical_alignment="center")
    with col_u1:
        st.markdown(
            f'<div style="font-size:13.5px; font-weight:700; color:{NAVY}; margin-bottom:4px;">'
            f'📁 Cargar archivo Excel de visitas comerciales (.xlsx / .csv):'
            f'</div>',
            unsafe_allow_html=True
        )
        uploaded_file = st.file_uploader(
            "Cargar archivo Excel",
            type=['xlsx', 'xls', 'csv'],
            label_visibility="collapsed",
            help="Sube tu archivo de Excel o CSV para analizar tus datos en el dashboard",
            key="excel_uploader_main"
        )
    with col_u2:
        if uploaded_file is not None:
            st.success(f"**Archivo cargado:**<br>{esc(uploaded_file.name)}", icon="✅")
        else:
            st.info(f"**Fuente activa:**<br>{default_source}", icon="📊")
        if st.button("🔄 Recargar datos en línea", use_container_width=True, help="Recarga la fuente de datos oficial"):
            st.cache_data.clear()
            st.rerun()

# Determinar datos a procesar
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_up = pd.read_csv(uploaded_file)
        else:
            df_up = pd.read_excel(uploaded_file)
        raw_records = df_up.to_dict(orient='records')
    except Exception as e:
        st.error(f"Error al leer el archivo subido: {e}")
        raw_records = default_records
else:
    raw_records = default_records

df = prepare_dataframe(raw_records)

if df.empty:
    st.warning("No hay datos disponibles para mostrar. Por favor sube un archivo Excel válido o revisa la conexión.")
    st.stop()

# ==========================================
# PANEL DE FILTROS DINÁMICOS
# ==========================================
with st.container(border=True):
    unique_ciudades = sorted([c for c in df['ciu'].unique() if c])
    unique_segmentos = sorted([s for s in df['seg'].unique() if s])
    unique_tipos = sorted([t for t in df['tipo'].unique() if t])
    unique_etapas = sorted([e for e in df['etapa'].unique() if e])
    unique_estados = sorted([es for es in df['est'].unique() if es])

    dates_with_val = [d for d in df['f'].unique() if d]
    min_date = min(dates_with_val) if dates_with_val else None
    max_date = max(dates_with_val) if dates_with_val else None

    col_f1, col_f2, col_f3, col_f4, col_f5, col_f6, col_f7, col_f8 = st.columns(
        [1.3, 1.3, 1.4, 1.4, 1.4, 1.4, 1.4, 1.0],
        vertical_alignment="center"
    )

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
        st.write("")
        if st.button("Limpiar", help="Restablecer todos los filtros", use_container_width=True):
            st.session_state.filtro_ciu = "Todas"
            st.session_state.filtro_seg = "Todos"
            st.session_state.filtro_tipo = "Todos"
            st.session_state.filtro_etapa = "Todas"
            st.session_state.filtro_est = "Todos"
            st.rerun()

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

valor_str = f"$ {total_valor:,.0f}".replace(",", ".")

# Renderizado HTML limpio de los 5 KPIs
kpi_html = (
    f'<div class="kpi-container">'
    f'<div class="kpi-card b-navy"><span class="kpi-label">Visitas</span><b class="kpi-value">{n_visitas:,}</b><small class="kpi-subtext">En el filtro actual</small></div>'
    f'<div class="kpi-card b-green"><span class="kpi-label">Pedidos</span><b class="kpi-value">{pedidos_count:,}</b><small class="kpi-subtext">{conversion_pct:.1f}% de conversión</small></div>'
    f'<div class="kpi-card b-navy"><span class="kpi-label">Valor de pedidos</span><b class="kpi-value">{valor_str}</b><small class="kpi-subtext">{ticket_str}</small></div>'
    f'<div class="kpi-card b-green"><span class="kpi-label">Metros pedidos</span><b class="kpi-value">{total_metros:,.0f}</b><small class="kpi-subtext">En el filtro actual</small></div>'
    f'<div class="kpi-card b-cyan"><span class="kpi-label">Visitas exportación</span><b class="kpi-value">{export_pct:.0f}%</b><small class="kpi-subtext">{export_count} de {n_visitas} visitas</small></div>'
    f'</div>'
)
st.markdown(kpi_html, unsafe_allow_html=True)

# ==========================================
# FILA 1 DE GRÁFICOS: TENDENCIA & ETAPA
# ==========================================
col_g1, col_g2 = st.columns([1.6, 1.0])

# Gráfico 1: Visitas y valor de pedidos por día
with col_g1:
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:16px; font-weight:700; color:{NAVY}; margin-bottom:10px;">'
            f'Visitas y valor de pedidos por día'
            f'</div>',
            unsafe_allow_html=True
        )
        
        if n_visitas > 0:
            df_trend = df_filt[df_filt['f'] != ""].groupby('f').agg(
                visitas=('cli', 'count'),
                valor=('val', 'sum')
            ).reset_index().sort_values('f')
            
            df_trend['fecha_lbl'] = df_trend['f'].apply(lambda x: f"{x[8:10]}/{x[5:7]}")

            if HAS_PLOTLY:
                fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
                fig_trend.add_trace(
                    go.Bar(
                        x=df_trend['fecha_lbl'],
                        y=df_trend['visitas'],
                        name="Visitas",
                        marker=dict(color=CYAN, cornerradius=4),
                        hovertemplate="<b>%{x}</b><br>Visitas: %{y}<extra></extra>"
                    ),
                    secondary_y=False
                )
                fig_trend.add_trace(
                    go.Scatter(
                        x=df_trend['fecha_lbl'],
                        y=df_trend['valor'],
                        name="Valor de pedidos",
                        line=dict(color=GREEN, width=3, shape='spline'),
                        mode="lines+markers",
                        marker=dict(size=7, color=GREEN),
                        hovertemplate="<b>%{x}</b><br>Valor: $ %{y:,.0f}<extra></extra>"
                    ),
                    secondary_y=True
                )
                fig_trend.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=310,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
                    font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
                    xaxis=dict(showgrid=False, tickfont=dict(color=MUTED_COLOR)),
                    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(color=MUTED_COLOR), rangemode="tozero", title=dict(text="Visitas", font=dict(color=NAVY, size=11))),
                    yaxis2=dict(showgrid=False, overlaying='y', side='right', tickfont=dict(color=MUTED_COLOR), rangemode="tozero", title=dict(text="Valor ($)", font=dict(color=GREEN, size=11)))
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            else:
                st.bar_chart(df_trend.set_index('fecha_lbl')['visitas'], color=CYAN, height=280)
        else:
            st.info("Sin visitas con los filtros seleccionados.")

# Gráfico 2: Visitas por etapa comercial
with col_g2:
    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:16px; font-weight:700; color:{NAVY}; margin-bottom:10px;">'
            f'Visitas por etapa comercial'
            f'</div>',
            unsafe_allow_html=True
        )
        
        if n_visitas > 0:
            df_etapa = df_filt['etapa'].value_counts().reset_index()
            df_etapa.columns = ['etapa', 'visitas']
            df_etapa = df_etapa.sort_values('visitas', ascending=True)

            if HAS_PLOTLY:
                fig_etapa = go.Figure(go.Bar(
                    x=df_etapa['visitas'],
                    y=df_etapa['etapa'],
                    orientation='h',
                    marker=dict(color=NAVY, cornerradius=4),
                    text=df_etapa['visitas'].astype(str),
                    textposition='outside',
                    textfont=dict(color=NAVY, size=11, family="Segoe UI"),
                    hovertemplate="<b>%{y}</b><br>Visitas: %{x}<extra></extra>"
                ))
                fig_etapa.update_layout(
                    margin=dict(l=10, r=35, t=10, b=10),
                    height=310,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
                    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", rangemode="tozero"),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_etapa, use_container_width=True, config={'displayModeBar': False})
            else:
                st.bar_chart(df_etapa.set_index('etapa')['visitas'], color=NAVY, height=280)
        else:
            st.info("Sin datos de etapas.")

# ==========================================
# FILA 2 DE GRÁFICOS: ALCANCE GEOGRÁFICO & SEGMENTOS (ALINEADOS)
# ==========================================
col_g3, col_g4 = st.columns([1.0, 1.0])

# Gráfico 3: Alcance geográfico de las visitas
with col_g3:
    with st.container(border=True):
        geo_counts = df_filt[df_filt['ciu'] != 'SIN DATO']['ciu'].value_counts()
        real_ciudades = len(geo_counts)
        txt_ciu = "ciudad impactada" if real_ciudades == 1 else "ciudades impactadas"

        st.markdown(
            f'<div style="font-size:16px; font-weight:700; color:{NAVY}; margin-bottom:2px;">'
            f'Alcance geográfico de las visitas'
            f'</div>'
            f'<div style="color:{MUTED_COLOR}; font-size:13px; margin-bottom:8px;">'
            f'<b style="color:{GREEN}; font-size:14px;">{real_ciudades}</b> {txt_ciu} · {n_visitas:,} visitas'
            f'</div>',
            unsafe_allow_html=True
        )

        if n_visitas > 0 and len(geo_counts) > 0:
            top_8_geo = geo_counts.head(8)
            rest_geo = geo_counts.iloc[8:].sum() if len(geo_counts) > 8 else 0

            geo_labels = list(top_8_geo.index)
            geo_values = list(top_8_geo.values)
            geo_colors = [GREEN] * len(geo_values)

            if rest_geo > 0:
                geo_labels.append(f"Otras ({len(geo_counts) - 8} ciudades)")
                geo_values.append(rest_geo)
                geo_colors.append(CYAN)

            df_geo_plot = pd.DataFrame({'ciudad': geo_labels, 'visitas': geo_values, 'color': geo_colors}).iloc[::-1]

            if HAS_PLOTLY:
                max_geo_val = max(df_geo_plot['visitas']) if len(df_geo_plot) > 0 else 14
                fig_geo = go.Figure(go.Bar(
                    x=df_geo_plot['visitas'],
                    y=df_geo_plot['ciudad'],
                    orientation='h',
                    marker=dict(color=df_geo_plot['color'].tolist(), cornerradius=4),
                    hovertemplate="<b>%{y}</b><br>Visitas: %{x} (%{customdata:.1f}%)<extra></extra>",
                    customdata=(df_geo_plot['visitas'] / n_visitas * 100),
                    text=[f"{v} - {(v/n_visitas*100):.0f}%" for v in df_geo_plot['visitas']],
                    textposition='outside',
                    textfont=dict(color=NAVY, size=11, family="Segoe UI")
                ))
                fig_geo.update_layout(
                    margin=dict(l=10, r=45, t=10, b=25),
                    height=355,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
                    xaxis=dict(showgrid=True, gridcolor="#E2E8F0", rangemode="tozero", dtick=2, range=[0, max_geo_val + 2], tickfont=dict(color=MUTED_COLOR, size=11)),
                    yaxis=dict(showgrid=False, tickfont=dict(color=TEXT_COLOR, size=11.5))
                )
                st.plotly_chart(fig_geo, use_container_width=True, config={'displayModeBar': False})
            else:
                st.bar_chart(df_geo_plot.set_index('ciudad')['visitas'], color=GREEN, height=340)
        else:
            st.info("Sin datos geográficos.")

# Gráfico 4: Visitas por segmento con barras proporcionales y pills
with col_g4:
    with st.container(border=True):
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
            f'<span style="font-size:16px; font-weight:700; color:{NAVY};">Visitas por segmento</span>'
            f'<span style="background:#eef0fa; color:{NAVY}; font-size:11px; font-weight:700; border-radius:6px; padding:3px 8px;">Top 10</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if n_visitas > 0:
            seg_counts = df_filt['seg'].value_counts()
            top_10 = seg_counts.head(10)
            rest_count = len(seg_counts) - 10
            rest_sum = seg_counts.iloc[10:].sum() if rest_count > 0 else 0

            # Preparar lista con Top 10 + Otros nichos (como en index.html)
            items_seg = []
            for i, (s_name, s_val) in enumerate(top_10.items()):
                items_seg.append((s_name, s_val, SEGC[i % len(SEGC)]))
            
            if rest_sum > 0:
                items_seg.append((f"Otros nichos ({rest_count})", rest_sum, '#9aa0c8'))

            max_v = max([x[1] for x in items_seg]) if items_seg else 1
            
            # Generar lista de barras de segmento en una sola cadena limpia
            seg_items = []
            for s_name, s_val, c_color in items_seg:
                width_pct = (s_val / max_v) * 100
                pct_val = (s_val / n_visitas) * 100
                safe_name = esc(s_name)
                seg_items.append(
                    f'<div style="display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:5px; font-size:12px;">'
                    f'<div style="width:130px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:600; color:{TEXT_COLOR};" title="{safe_name}">{safe_name}</div>'
                    f'<div style="flex:1; height:8px; background:#eef1f5; border-radius:6px; overflow:hidden;">'
                    f'<div style="width:{width_pct}%; height:100%; background:{c_color}; border-radius:6px;"></div>'
                    f'</div>'
                    f'<div style="min-width:75px; text-align:right; font-weight:700; color:{NAVY}; font-size:11.5px;">{s_val} ({pct_val:.1f}%)</div>'
                    f'</div>'
                )
            
            p_count = pedidos_count
            sp_count = n_visitas - p_count
            p_pct = (p_count / n_visitas * 100) if n_visitas > 0 else 0
            sp_pct = (sp_count / n_visitas * 100) if n_visitas > 0 else 0

            pills_html = (
                f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:14px; margin-bottom:4px;">'
                f'<div style="background:#e6f4ee; border:1px solid #9fd5bf; border-radius:10px; text-align:center; padding:10px 8px; color:{GREEN};">'
                f'<div style="font-size:11px; font-weight:700; letter-spacing:0.04em;">CON PEDIDO</div>'
                f'<div style="font-size:18px; font-weight:800; margin-top:2px;">{p_count} ({p_pct:.1f}%)</div>'
                f'</div>'
                f'<div style="background:#e6f8fd; border:1px solid #9fe0f3; border-radius:10px; text-align:center; padding:10px 8px; color:{NAVY};">'
                f'<div style="font-size:11px; font-weight:700; letter-spacing:0.04em;">SIN PEDIDO</div>'
                f'<div style="font-size:18px; font-weight:800; margin-top:2px;">{sp_count} ({sp_pct:.1f}%)</div>'
                f'</div>'
                f'</div>'
            )

            st.markdown("".join(seg_items) + pills_html, unsafe_allow_html=True)
        else:
            st.info("Sin datos de segmentos.")

# ==========================================
# SECCIÓN: ÚLTIMAS VISITAS (TABLA ESTILIZADA)
# ==========================================
with st.container(border=True):
    st.markdown(
        f'<div style="font-size:16px; font-weight:700; color:{NAVY}; margin-bottom:12px;">'
        f'Últimas visitas'
        f'</div>',
        unsafe_allow_html=True
    )

    if n_visitas > 0:
        df_table = df_filt.sort_values('f', ascending=False).copy()
        
        # Generar filas HTML limpias sin indentaciones que rompan Markdown
        rows_list = []
        for _, row in df_table.iterrows():
            f_clean = f"{row['f'][8:10]}/{row['f'][5:7]}/{row['f'][0:4]}" if row['f'] else ""
            cli_safe = esc(row['cli'])
            ciu_safe = esc(row['ciu'])
            etapa_safe = esc(row['etapa'])
            obs_safe = esc(row['obs'])
            
            if row['ped']:
                ped_badge = f'<span style="display:inline-block; white-space:nowrap; background:#e6f4ee; color:{GREEN}; border-radius:20px; padding:2px 12px; font-size:12.5px; font-weight:600;">$ {row["val"]:,.0f}</span>'.replace(",", ".")
            else:
                ped_badge = '<span style="color:#94a3b8;">—</span>'
            
            rows_list.append(
                f'<tr style="border-bottom:1px solid {LINE_COLOR};">'
                f'<td style="white-space:nowrap; padding:9px 8px; font-size:13px; color:#475569;">{f_clean}</td>'
                f'<td style="padding:9px 8px; font-size:13px; font-weight:700; color:{NAVY};">{cli_safe}</td>'
                f'<td style="padding:9px 8px; font-size:13px; color:#334155;">{ciu_safe}</td>'
                f'<td style="padding:9px 8px; font-size:13px; color:#334155;">{etapa_safe}</td>'
                f'<td style="white-space:nowrap; padding:9px 8px;">{ped_badge}</td>'
                f'<td style="padding:9px 8px; font-size:12.5px; color:#64748b; max-width:420px;">{obs_safe}</td>'
                f'</tr>'
            )

        table_html = (
            f'<div style="overflow-x:auto; width:100%; margin-bottom:14px;">'
            f'<table style="width:100%; border-collapse:collapse; font-size:13.5px; font-family:inherit;">'
            f'<thead><tr style="border-bottom:2px solid {LINE_COLOR}; text-align:left;">'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Fecha</th>'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Cliente</th>'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Ciudad</th>'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Etapa</th>'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Pedido</th>'
            f'<th style="padding:8px 8px; color:{NAVY}; font-size:13px; font-weight:700;">Observaciones</th>'
            f'</tr></thead>'
            f'<tbody>{"".join(rows_list)}</tbody>'
            f'</table></div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

        # Botones de exportación (CSV y Excel)
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
    else:
        st.info("No hay visitas con los filtros seleccionados.")

# ==========================================
# FOOTER
# ==========================================
st.markdown(f"""
<div class="custom-footer">
    <b>Magic Print</b> · Dashboard comercial de visitas · Desarrollado para la Dirección General y Comercial
</div>
""", unsafe_allow_html=True)
