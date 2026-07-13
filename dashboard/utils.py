"""
CommercePulse Dashboard — Utilitários de Carregamento e Cache de Dados.

Centraliza o carregamento de dados e cacheamento para evitar reprocessamento
em cada interação do usuário com o dashboard Streamlit.
"""

from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    """Carrega a base processada de pedidos e itens."""
    df = pd.read_csv(PROCESSED_DIR / "commercepulse_orders_items.csv")

    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date", "purchase_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


@st.cache_data(ttl=3600)
def load_rfm() -> pd.DataFrame | None:
    """Carrega a tabela RFM se existir."""
    rfm_path = PROCESSED_DIR / "commercepulse_rfm.csv"
    if rfm_path.exists():
        return pd.read_csv(rfm_path)
    return None


def get_delivered(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra pedidos entregues com dados completos de entrega."""
    mask = (df["is_delivered"] == 1) & df["is_late"].notna()
    return df[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    """Calcula os KPIs principais do e-commerce."""
    orders_revenue = df.groupby("order_id")["item_revenue"].sum()
    delivered = get_delivered(df)

    return {
        "total_orders": df["order_id"].nunique(),
        "total_items": len(df),
        "total_revenue": df["item_revenue"].sum(),
        "total_revenue_freight": df["item_total_value"].sum(),
        "avg_ticket": orders_revenue.mean(),
        "avg_review": df["review_score"].mean(),
        "avg_delivery_days": delivered["delivery_days"].mean(),
        "delay_rate": delivered["is_late"].mean(),
        "n_categories": df["product_category_name_english"].nunique(),
        "n_states": df["customer_state"].nunique(),
        "n_sellers": df["seller_id"].nunique(),
    }


def compute_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula receita mensal agregada."""
    monthly = df.groupby("purchase_year_month").agg(
        revenue=("item_revenue", "sum"),
        total_value=("item_total_value", "sum"),
        orders=("order_id", "nunique"),
        items=("order_item_id", "count"),
        avg_review=("review_score", "mean"),
    ).reset_index()

    monthly["ticket_medio"] = monthly["revenue"] / monthly["orders"]
    monthly = monthly.sort_values("purchase_year_month")
    return monthly


def compute_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por estado do cliente."""
    delivered = get_delivered(df)
    state = delivered.groupby("customer_state").agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("item_revenue", "sum"),
        avg_ticket=("item_revenue", "mean"),
        avg_freight=("freight_value", "mean"),
        avg_review=("review_score", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        delay_rate=("is_late", "mean"),
    ).reset_index()
    return state


def compute_category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por categoria de produto."""
    delivered = get_delivered(df)
    cat = delivered.groupby("product_category_name_english").agg(
        total_items=("order_item_id", "count"),
        total_revenue=("item_revenue", "sum"),
        avg_price=("price", "mean"),
        avg_review=("review_score", "mean"),
        avg_freight=("freight_value", "mean"),
        delay_rate=("is_late", "mean"),
    ).reset_index()
    cat = cat.dropna(subset=["product_category_name_english"])
    return cat


def compute_seller_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por vendedor."""
    delivered = get_delivered(df)
    seller = delivered.groupby("seller_id").agg(
        total_items=("order_item_id", "count"),
        total_orders=("order_id", "nunique"),
        total_revenue=("item_revenue", "sum"),
        avg_review=("review_score", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        delay_rate=("is_late", "mean"),
        avg_delay=("delay_days", "mean"),
        seller_state=("seller_state", "first"),
        seller_city=("seller_city", "first"),
    ).reset_index()
    return seller


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {value:,.2f}"


def format_pct(value: float) -> str:
    """Formata valor como percentual."""
    return f"{value * 100:.1f}%"

import base64

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_page_style():
    """Applies a custom premium aesthetic with background and logo."""
    # Configuração Global de Transparência para Gráficos Plotly
    import plotly.io as pio
    pio.templates["plotly_dark"].layout.paper_bgcolor = "rgba(0,0,0,0)"
    pio.templates["plotly_dark"].layout.plot_bgcolor = "rgba(0,0,0,0)"

    # Logo e nome no topo da sidebar
    logo_path = BASE_DIR / "dashboard" / "assets" / "logo.png"
    logo_css = ""
    if logo_path.exists():
        logo_b64 = get_base64_of_bin_file(str(logo_path))
        st.sidebar.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 20px 0 25px 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;">
            <img src="data:image/png;base64,{logo_b64}" width="68" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);">
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">CommercePulse</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu customizado 100% à prova de falhas (ordem natural)
        st.sidebar.page_link("app.py", label="Início", icon=":material/home:")
        st.sidebar.page_link("pages/01_Visao_Geral.py", label="Visão Geral", icon=":material/analytics:")
        st.sidebar.page_link("pages/02_Geografica.py", label="Geográfica", icon=":material/public:")
        st.sidebar.page_link("pages/03_Categorias.py", label="Categorias", icon=":material/sell:")
        st.sidebar.page_link("pages/04_Logistica.py", label="Logística", icon=":material/local_shipping:")
        st.sidebar.page_link("pages/05_Vendedores.py", label="Vendedores", icon=":material/storefront:")
        st.sidebar.markdown("---")
        
        logo_css = """
        /* Esconde a navegação padrão do Streamlit (vamos usar a nossa customizada) */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Estilo dos links customizados para manter a vibe premium */
        [data-testid="stSidebar"] a {
            text-decoration: none !important;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] a:hover {
            transform: translateX(4px);
        }

        /* Ajusta o botão de colapsar a sidebar para não sumir */
        [data-testid="collapsedControl"] {
            left: 15px !important;
            background-color: rgba(15, 23, 42, 0.8) !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        }
        """

    # Carregar background
    bg_path = BASE_DIR / "dashboard" / "assets" / "background_new.png"
    bg_ext = "png"
    
    if bg_path.exists():
        bin_str = get_base64_of_bin_file(str(bg_path))
        page_bg_img = f"""
        <style>
        {logo_css}
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/{bg_ext};base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0);
        }}
        [data-testid="stToolbar"] {{
            right: 2rem;
        }}
        /* Escurecer um pouco o fundo para facilitar leitura (overlay) */
        [data-testid="stAppViewBlockContainer"] {{
            background: rgba(14, 17, 23, 0.4);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(5px);
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Glassmorphism KPI Cards */
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(15, 23, 42, 0.85);
        }

        /* Metric Labels */
        div[data-testid="stMetric"] label {
            color: #94a3b8 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Metric Values - Gradient Text */
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            background: -webkit-linear-gradient(45deg, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Headers Modernization */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }

        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Streamlit Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(99, 110, 250, 0.2);
            border-bottom-color: #636EFA !important;
        }
    </style>
    """, unsafe_allow_html=True)


def plot_chart(fig):
    """Garante que o gráfico Plotly renderize com fundo totalmente transparente."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel_bgcolor="rgba(15, 23, 42, 0.95)",
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)
