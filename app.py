import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Radar Delivery | Paraíba", page_icon="📍", layout="wide", initial_sidebar_state="expanded")

# --- Gestão de Estado do Tema (Dark Mode Toggle) ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- Cores Dinâmicas baseadas nos Apps de Delivery (iFood, Uber Eats, 99Food) ---
if st.session_state.dark_mode:
    tema = {
        "bg_app": "#000000",          # Fundo escuro (Uber Eats)
        "bg_sidebar": "#121212",      # Lateral ligeiramente mais clara
        "bg_card": "#1C1C1C",         # Fundo dos cartões de métricas
        "text_main": "#FFFFFF",       # Texto principal branco
        "text_muted": "#A0A0A0",      # Texto secundário cinzento
        "border": "#2D2D2D",          # Bordas subtis
        "accent": "#EA1D2C",          # Vermelho iFood (Destaque)
        "status_bg": "#1A3626",       # Fundo verde escuro para status
        "status_txt": "#06C167",      # Verde Uber Eats (Sucesso)
        "logo_bg": "#EA1D2C",         # Fundo da logo
        "logo_icon": "#FFFFFF"
    }
else:
    tema = {
        "bg_app": "#F4F6F8",          # Fundo claro SaaS
        "bg_sidebar": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "text_main": "#0F172A",       # Texto escuro
        "text_muted": "#64748B",
        "border": "#E2E8F0",
        "accent": "#EA1D2C",          # Vermelho iFood
        "status_bg": "#E6F8F0",
        "status_txt": "#06C167",      # Verde Uber Eats
        "logo_bg": "#EA1D2C",
        "logo_icon": "#FFFFFF"
    }

# --- Injeção de CSS Dinâmico ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Fundos Globais */
    .stApp {{
        background-color: {tema['bg_app']} !important;
        color: {tema['text_main']};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {tema['bg_sidebar']} !important;
        border-right: 1px solid {tema['border']} !important;
    }}
    
    /* Tipografia e Títulos */
    * {{ font-family: 'Inter', 'Helvetica Neue', sans-serif; }}
    h1, h2, h3, h4, p, span {{ color: {tema['text_main']} !important; }}
    .text-muted {{ color: {tema['text_muted']} !important; }}
    
    /* Correção para a Barra de Ferramentas */
    [data-testid="stElementToolbar"] {{
        background-color: transparent !important;
        z-index: 9999;
    }}
    [data-testid="stElementToolbar"] button {{
        background-color: {tema['bg_card']} !important;
        border: 1px solid {tema['border']} !important;
    }}
    [data-testid="stElementToolbar"] svg {{
        stroke: {tema['text_main']} !important;
        fill: transparent !important;
    }}
    
    /* Cartões de Métricas */
    [data-testid="stMetric"] {{
        background-color: {tema['bg_card']} !important;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {tema['border']};
        border-left: 5px solid {tema['accent']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    [data-testid="stMetricLabel"] p {{
        font-size: 0.85rem !important;
        color: {tema['text_muted']} !important;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    [data-testid="stMetricValue"] div {{
        font-size: 2.2rem !important;
        color: {tema['text_main']} !important;
        font-weight: 800;
    }}
    
    /* Badges de Status e Github */
    .status-badge {{
        background-color: {tema['status_bg']};
        color: {tema['status_txt']};
        padding: 10px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid {tema['status_txt']}33;
    }}
    .status-badge span {{ color: {tema['status_txt']} !important; }}
    
    .github-link:hover {{
        opacity: 0.8;
        transform: translateY(-2px);
    }}
    
    /* Separadores (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: transparent; }}
    .stTabs [aria-selected="true"] {{
        color: {tema['accent']} !important;
        border-bottom: 3px solid {tema['accent']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Funções de Extração de Dados ---
@st.cache_data
def get_restaurants_pb():
    file_path = 'data/restaurantes_pb.csv'
    cols = ['Nome', 'Tipo', 'Lat', 'Lon']
    fallback = pd.DataFrame(columns=cols)
    if not os.path.exists(file_path): return fallback
    try:
        df = pd.read_csv(file_path)
        for col in cols: 
            if col not in df.columns: df[col] = None
        df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
        df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
        return df.dropna(subset=['Lat', 'Lon'])
    except: return fallback

@st.cache_data
def get_populacao_ibge_pb():
    file_path = 'data/populacao_pb.csv'
    cols = ['Município', 'População']
    fallback = pd.DataFrame(columns=cols)
    if not os.path.exists(file_path): return fallback
    try:
        df = pd.read_csv(file_path)
        for col in cols: 
            if col not in df.columns: df[col] = None
        df['População'] = pd.to_numeric(df['População'], errors='coerce').fillna(0).astype(int)
        return df
    except: return fallback

df_restaurantes = get_restaurants_pb()
df_populacao = get_populacao_ibge_pb()

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    # Logo Dinâmica
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; margin-top: 10px;">
        <div style="background-color: {tema['logo_bg']}; color: {tema['logo_icon']}; padding: 10px; border-radius: 12px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 2a10 10 0 0 1 10 10"></path>
                <path d="M12 12L22 12"></path>
                <circle cx="12" cy="12" r="2"></circle>
            </svg>
        </div>
        <div style="line-height: 1.1;">
            <span style="font-weight: 800; font-size: 20px; display: block; color: {tema['text_main']};">RADAR</span>
            <span style="font-weight: 500; font-size: 14px; color: {tema['text_muted']};">Delivery</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toggle("Modo Escuro 🌙", key="dark_mode")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='font-size: 0.85rem; color: {tema['text_muted']}; text-transform: uppercase; font-weight: 600;'>Status da Operação</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="status-badge">
        <span style="font-size: 1.2rem;">●</span> Pipeline de Dados: OK
    </div>
    <div class="status-badge">
        <span style="font-size: 1.2rem;">●</span> Fallback Local: Ativo
    </div>
    """, unsafe_allow_html=True)

    # --- Adição do Perfil do GitHub ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.85rem; color: {tema['text_muted']}; text-transform: uppercase; font-weight: 600;'>Desenvolvido por</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <a href="https://github.com/yxngvitu-glitch" target="_blank" style="text-decoration: none;">
        <div class="github-link" style="display: flex; align-items: center; gap: 10px; padding: 12px; background-color: {tema['bg_card']}; border: 1px solid {tema['border']}; border-radius: 8px; transition: all 0.3s ease;">
            <svg height="24" width="24" viewBox="0 0 16 16" fill="{tema['text_main']}">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            <span style="color: {tema['text_main']}; font-weight: 600; font-size: 0.95rem;">@yxngvitu-glitch</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

# --- Cabeçalho Principal (Descrições Adicionadas) ---
st.markdown(f"<h1 style='font-size: 2.2rem; font-weight: 800; margin-bottom: -15px;'>Radar Delivery</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='text-muted' style='font-size: 1rem; margin-bottom: 10px;'>Inteligência Espacial • Estado da Paraíba</p>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 1rem; color: {tema['text_muted']}; margin-bottom: 30px; line-height: 1.6;'>Plataforma analítica desenvolvida para o mapeamento e monitoramento da saturação do mercado de delivery. O painel identifica zonas estratégicas de alta demanda (hotzones) e potenciais áreas de expansão comercial (desertos de entrega) com base em dados demográficos e concentração de parceiros.</p>", unsafe_allow_html=True)

# --- Painel de Métricas ---
col1, col2, col3 = st.columns(3)
with col1: st.metric("Total de Parceiros", f"{len(df_restaurantes):,}".replace(",", "."))
with col2:
    tipo_comum = "N/A"
    if not df_restaurantes.empty and 'Tipo' in df_restaurantes.columns:
        modas = df_restaurantes['Tipo'].mode()
        if not modas.empty:
            t = modas[0].title()
            tipo_comum = "Restaurante" if t == "Restaurant" else "Fast Food" if t == "Fast_Food" else "Cafetaria" if t == "Cafe" else t
    st.metric("Categoria Dominante", tipo_comum)
with col3: st.metric("Praças Ativas", len(df_populacao))

st.write("")

# --- Separadores ---
tab1, tab2 = st.tabs(["📍 Heatmap Operacional", "📊 Demografia de Mercado"])

with tab1:
    st.markdown(f"<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>Saturação vs Desertos de Entrega</h3>", unsafe_allow_html=True)
    if not df_restaurantes.empty:
        
        # Configuração Base do Mapa
        if st.session_state.dark_mode:
            tiles_map = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            attr_map = "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"
        else:
            tiles_map = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
            attr_map = "Tiles &copy; Esri &mdash; Source: Esri"
        
        mapa_calor = folium.Map(location=[-7.11532, -34.8610], zoom_start=9, tiles=tiles_map, attr=attr_map)
        coordenadas = df_restaurantes[['Lat', 'Lon']].values.tolist()
        
        if coordenadas:
            # 1. Adicionar o Mapa de Calor
            HeatMap(
                coordenadas, 
                radius=18, 
                blur=12, 
                min_opacity=0.4, 
                gradient={0.2: '#00E676', 0.6: '#FFEA00', 1.0: '#EA1D2C'}
            ).add_to(mapa_calor)
            
            # 2. Adicionar a camada de Nomes das Cidades no modo escuro por cima do calor
            if st.session_state.dark_mode:
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri",
                    name="Rótulos",
                    overlay=True,
                    control=False
                ).add_to(mapa_calor)
            
            # 3. Renderizar o mapa no Streamlit
            st_folium(
                mapa_calor, 
                use_container_width=True, 
                height=550, 
                returned_objects=[],
                key=f"mapa_calor_{st.session_state.dark_mode}"
            )
            
            col_leg1, col_leg2, col_leg3 = st.columns(3)
            with col_leg1:
                st.markdown("🔴 **Alta Densidade (Hotzones)**<br><span class='text-muted' style='font-size: 0.9rem;'>Ideal para campanhas de fidelização e logística otimizada.</span>", unsafe_allow_html=True)
            with col_leg2:
                st.markdown("🟡 **Média Densidade**<br><span class='text-muted' style='font-size: 0.9rem;'>Oportunidade de aquisição de parceiros e consolidação.</span>", unsafe_allow_html=True)
            with col_leg3:
                st.markdown("🟢 **Desertos (Coldzones)**<br><span class='text-muted' style='font-size: 0.9rem;'>Áreas com alto potencial para expansão territorial e Dark Kitchens.</span>", unsafe_allow_html=True)
        else:
            st.warning("Coordenadas inválidas. Por favor, verifique a integridade da base de dados.")
    else:
        st.info("A aguardar sincronização de dados do pipeline.")
        
with tab2:
    col_dem1, col_dem2 = st.columns([2, 1])
    with col_dem1:
        st.markdown("<h3 style='font-size: 1.2rem;'>Top 10 Mercados por Demografia</h3>", unsafe_allow_html=True)
        if not df_populacao.empty and df_populacao['População'].sum() > 0:
            df_top_pop = df_populacao.sort_values(by='População', ascending=False).head(10)
            st.bar_chart(data=df_top_pop, x='Município', y='População', color=tema['accent'])
            
    with col_dem2:
        mostrar_todos = st.toggle("Desbloquear base completa")
        
        titulo = "Base Completa de Parceiros" if mostrar_todos else "Amostra de Base (Preview)"
        st.markdown(f"<h3 style='font-size: 1.2rem;'>{titulo}</h3>", unsafe_allow_html=True)
        
        if not df_restaurantes.empty:
            df_view = df_restaurantes[['Nome', 'Tipo']] if mostrar_todos else df_restaurantes[['Nome', 'Tipo']].head(15)
            
            st.dataframe(df_view, use_container_width=True, hide_index=True, height=350)
            
            if not mostrar_todos:
                st.caption("Visão reduzida ativada por padrão para proteção de dados sensíveis da operação.")
            else:
                st.caption(f"A exibir o total de {len(df_restaurantes)} registos operacionais disponíveis.")