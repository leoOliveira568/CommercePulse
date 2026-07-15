"""
CommercePulse Dashboard — Utilitários de Carregamento e Cache de Dados.

Centraliza o carregamento de dados e cacheamento para evitar reprocessamento
em cada interação do usuário com o dashboard Streamlit.
"""

from pathlib import Path

import pandas as pd
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
    """Filtra itens de pedidos entregues com dados completos de entrega."""
    mask = (df["is_delivered"] == 1) & df["is_late"].notna()
    return df[mask].copy()


def get_order_facts(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida a base de itens em uma linha por pedido.

    Métricas como avaliação, atraso e prazo de entrega pertencem ao pedido e
    não devem ser ponderadas pela quantidade de itens comprados.
    """
    return df.groupby("order_id", as_index=False).agg(
        purchase_year_month=("purchase_year_month", "first"),
        customer_state=("customer_state", "first"),
        order_revenue=("item_revenue", "sum"),
        order_total_value=("item_total_value", "sum"),
        order_freight=("freight_value", "sum"),
        review_score=("review_score", "first"),
        delivery_days=("delivery_days", "first"),
        delivery_delta_days=("delivery_delta_days", "first"),
        delay_days=("delay_days", "first"),
        is_late=("is_late", "first"),
        is_delivered=("is_delivered", "first"),
    )


def get_delivered_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna uma linha por pedido entregue com logística observável."""
    orders = get_order_facts(df)
    return orders[(orders["is_delivered"] == 1) & orders["is_late"].notna()].copy()


def get_order_seller_facts(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida a base em uma linha por combinação de pedido e vendedor."""
    return df.groupby(["order_id", "seller_id"], as_index=False).agg(
        total_items=("order_item_id", "count"),
        order_revenue=("item_revenue", "sum"),
        review_score=("review_score", "first"),
        delivery_days=("delivery_days", "first"),
        delay_days=("delay_days", "first"),
        is_late=("is_late", "first"),
        is_delivered=("is_delivered", "first"),
        seller_state=("seller_state", "first"),
        seller_city=("seller_city", "first"),
    )


def get_delivered_order_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna uma linha por pedido-vendedor entregue."""
    order_sellers = get_order_seller_facts(df)
    mask = (order_sellers["is_delivered"] == 1) & order_sellers["is_late"].notna()
    return order_sellers[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    """Calcula os KPIs principais do e-commerce."""
    orders = get_order_facts(df)
    delivered_orders = orders[(orders["is_delivered"] == 1) & orders["is_late"].notna()]

    return {
        "total_orders": len(orders),
        "total_items": len(df),
        "total_revenue": orders["order_revenue"].sum(),
        "total_revenue_freight": orders["order_total_value"].sum(),
        "avg_ticket": orders["order_revenue"].mean(),
        "avg_review": orders["review_score"].mean(),
        "avg_delivery_days": delivered_orders["delivery_days"].mean(),
        "delay_rate": delivered_orders["is_late"].mean(),
        "n_categories": df["product_category_name_english"].nunique(),
        "n_states": df["customer_state"].nunique(),
        "n_sellers": df["seller_id"].nunique(),
    }


def compute_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula GMV mensal agregado."""
    monthly_items = df.groupby("purchase_year_month").agg(
        revenue=("item_revenue", "sum"),
        total_value=("item_total_value", "sum"),
        items=("order_item_id", "count"),
    ).reset_index()

    orders = get_order_facts(df)
    monthly_orders = orders.groupby("purchase_year_month").agg(
        orders=("order_id", "count"),
        avg_review=("review_score", "mean"),
        ticket_medio=("order_revenue", "mean"),
    ).reset_index()

    monthly = monthly_items.merge(monthly_orders, on="purchase_year_month", how="left")
    monthly = monthly.sort_values("purchase_year_month")
    return monthly


def compute_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por estado do cliente."""
    orders = get_order_facts(df)
    state_sales = orders.groupby("customer_state").agg(
        total_orders=("order_id", "count"),
        total_revenue=("order_revenue", "sum"),
        avg_ticket=("order_revenue", "mean"),
        avg_freight=("order_freight", "mean"),
    ).reset_index()

    delivered_orders = orders[(orders["is_delivered"] == 1) & orders["is_late"].notna()]
    state_delivery = delivered_orders.groupby("customer_state").agg(
        avg_review=("review_score", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        delay_rate=("is_late", "mean"),
    ).reset_index()
    return state_sales.merge(state_delivery, on="customer_state", how="left")


def compute_category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por categoria de produto."""
    category_sales = df.groupby("product_category_name_english").agg(
        total_items=("order_item_id", "count"),
        total_revenue=("item_revenue", "sum"),
        avg_price=("price", "mean"),
        avg_freight=("freight_value", "mean"),
    ).reset_index()

    delivered = get_delivered(df)
    order_categories = delivered.groupby(
        ["order_id", "product_category_name_english"], as_index=False
    ).agg(
        review_score=("review_score", "first"),
        is_late=("is_late", "first"),
    )
    category_delivery = order_categories.groupby("product_category_name_english").agg(
        avg_review=("review_score", "mean"),
        delay_rate=("is_late", "mean"),
    ).reset_index()
    return category_sales.merge(
        category_delivery, on="product_category_name_english", how="left"
    )


def compute_seller_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas por vendedor."""
    order_sellers = get_order_seller_facts(df)
    seller_sales = order_sellers.groupby("seller_id").agg(
        total_items=("total_items", "sum"),
        total_orders=("order_id", "nunique"),
        total_revenue=("order_revenue", "sum"),
        seller_state=("seller_state", "first"),
        seller_city=("seller_city", "first"),
    ).reset_index()

    delivered = order_sellers[
        (order_sellers["is_delivered"] == 1) & order_sellers["is_late"].notna()
    ]
    seller_delivery = delivered.groupby("seller_id").agg(
        delivered_orders=("order_id", "nunique"),
        late_orders=("is_late", "sum"),
        avg_review=("review_score", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        delay_rate=("is_late", "mean"),
        avg_delay=("delay_days", "mean"),
    ).reset_index()
    return seller_sales.merge(seller_delivery, on="seller_id", how="left")


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira (valor completo)."""
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"

def format_currency_compact(value: float) -> str:
    """Formata valor monetário de forma abreviada (K, M, B) para dashboards."""
    if value >= 1_000_000_000:
        return f"R$ {value / 1_000_000_000:.2f} bi".replace(".", ",")
    elif value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} mi".replace(".", ",")
    elif value >= 1_000:
        return f"R$ {value / 1_000:.1f} mil".replace(".", ",")
    else:
        return f"R$ {value:.2f}".replace(".", ",")


def format_pct(value: float) -> str:
    """Formata valor como percentual."""
    return f"{value * 100:.1f}%"


def format_integer(value: int | float) -> str:
    """Formata inteiro com separador de milhar brasileiro."""
    return f"{value:,.0f}".replace(",", ".")

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

    logo_css = """
    /* Ajusta o botão de colapsar a sidebar para não sumir */
    [data-testid="collapsedControl"] {
        left: 15px !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-radius: 50% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    
    /* Aumenta o tamanho da logo nativa do Streamlit */
    [data-testid="stLogo"] {
        height: 60px !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
    }
    [data-testid="stLogo"] img {
        max-height: 100% !important;
        width: auto !important;
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
            padding: 2rem 2rem 2rem 2rem !important;
            padding-top: 2rem !important;
            backdrop-filter: blur(5px);
            margin-top: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
        
        /* Força a redução do espaço em branco no topo nativo do Streamlit */
        .stApp > header {{
            background-color: transparent !important;
        }}
        .stMainBlockContainer {{
            padding-top: 2rem !important;
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
    st.plotly_chart(fig, width="stretch", theme=None)
