import streamlit as st
from utils import set_page_style

st.set_page_config(
    page_title="CommercePulse — E-commerce Analytics",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Customizado Global ---
set_page_style()

# --- Logo Nativa do Streamlit ---
import os
st.logo("dashboard/assets/logo_with_text.png", icon_image="dashboard/assets/logo.png", size="large")

# --- Navegação Nativa do Streamlit (Sem Piscar) ---
pages = {
    "Navegação": [
        st.Page("views/00_Home.py", title="Início", icon=":material/home:"),
        st.Page("views/01_Visao_Geral.py", title="Visão Geral", icon=":material/analytics:"),
        st.Page("views/02_Geografica.py", title="Geográfica", icon=":material/public:"),
        st.Page("views/03_Categorias.py", title="Categorias", icon=":material/sell:"),
        st.Page("views/04_Logistica.py", title="Logística", icon=":material/local_shipping:"),
        st.Page("views/05_Vendedores.py", title="Vendedores", icon=":material/storefront:"),
    ]
}

pg = st.navigation(pages)
pg.run()
