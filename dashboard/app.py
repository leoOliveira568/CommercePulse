from pathlib import Path
import sys

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.utils import set_page_style

st.set_page_config(
    page_title="CommercePulse — E-commerce Analytics",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Customizado Global ---
set_page_style()

# --- Logo Nativa do Streamlit ---
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
st.logo(
    str(ASSETS_DIR / "logo_with_text.png"),
    icon_image=str(ASSETS_DIR / "logo.png"),
    size="large",
)

# --- Navegação Nativa do Streamlit (Sem Piscar) ---
pages = {
    "Navegação": [
        st.Page("views/00_Home.py", title="Início", icon=":material/home:"),
        st.Page("views/01_Visao_Geral.py", title="Visão Geral", icon=":material/analytics:"),
        st.Page("views/02_Geografica.py", title="Geográfica", icon=":material/public:"),
        st.Page("views/03_Categorias.py", title="Categorias", icon=":material/sell:"),
        st.Page("views/04_Logistica.py", title="Logística", icon=":material/local_shipping:"),
        st.Page("views/05_Vendedores.py", title="Vendedores", icon=":material/storefront:"),
        st.Page("views/06_Clientes_RFM.py", title="Clientes (RFM)", icon=":material/group:"),
    ]
}

pg = st.navigation(pages)
pg.run()
