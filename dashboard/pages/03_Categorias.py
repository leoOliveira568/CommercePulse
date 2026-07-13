"""
CommercePulse Dashboard — Análise de Categorias.

Receita, volume e satisfação por categoria de produto.
"""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import load_data, compute_category_metrics, set_page_style, plot_chart

st.set_page_config(page_title="Categorias — CommercePulse", page_icon=":material/sell:", layout="wide")
set_page_style()

st.title("Análise por Categoria")
st.markdown("Performance de produtos, ticket médio e satisfação por categoria.")

df = load_data()

# --- Filtros ---
st.sidebar.header("Filtros")
years = sorted(df["purchase_year"].unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years, key="cat_year")

states = sorted(df["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect("Estado do Cliente", states, default=states, key="cat_state")

top_n = st.sidebar.slider("Top N categorias", min_value=5, max_value=30, value=15)

mask = df["purchase_year"].isin(selected_years) & df["customer_state"].isin(selected_states)
df_filtered = df[mask]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

cat_metrics = compute_category_metrics(df_filtered)

# --- Top categorias por receita ---
st.markdown(f"### Top {top_n} Categorias por Receita")

top_revenue = cat_metrics.sort_values("total_revenue", ascending=False).head(top_n)

fig = go.Figure()
fig.add_trace(go.Bar(
    y=top_revenue["product_category_name_english"][::-1],
    x=top_revenue["total_revenue"][::-1],
    orientation="h",
    marker=dict(
        color=top_revenue["total_revenue"][::-1],
        colorscale="Viridis",
    ),
    text=top_revenue["total_revenue"][::-1].apply(lambda x: f"R$ {x/1000:.0f}k"),
    textposition="outside",
))
fig.update_layout(
    template="plotly_dark", height=max(400, top_n * 28),
    xaxis_title="Receita (R$)", yaxis_title="",
    margin=dict(l=180),
)
plot_chart(fig)

st.markdown("---")

# --- Volume vs Receita ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"### Top {top_n} por Volume de Itens")
    top_items = cat_metrics.sort_values("total_items", ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_items["product_category_name_english"][::-1],
        x=top_items["total_items"][::-1],
        orientation="h",
        marker=dict(color=top_items["total_items"][::-1], colorscale="Blues"),
        text=top_items["total_items"][::-1].apply(lambda x: f"{x:,}"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(400, top_n * 28),
        xaxis_title="Itens Vendidos", yaxis_title="",
        margin=dict(l=180),
    )
    plot_chart(fig)

with col_right:
    st.markdown(f"### Top {top_n} por Preço Médio")
    top_price = cat_metrics.sort_values("avg_price", ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_price["product_category_name_english"][::-1],
        x=top_price["avg_price"][::-1],
        orientation="h",
        marker=dict(color=top_price["avg_price"][::-1], colorscale="Oranges"),
        text=top_price["avg_price"][::-1].apply(lambda x: f"R$ {x:.0f}"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(400, top_n * 28),
        xaxis_title="Preço Médio (R$)", yaxis_title="",
        margin=dict(l=180),
    )
    plot_chart(fig)

st.markdown("---")

# --- Satisfação por categoria ---
st.markdown("### Categorias com Maiores Taxas de Atraso")

tab1, tab2 = st.tabs(["Melhores", "Piores"])

min_items = st.sidebar.number_input("Volume mínimo de itens", min_value=10, value=50, key="min_items_cat")
cat_filtered = cat_metrics[cat_metrics["total_items"] >= min_items]

with tab1:
    best = cat_filtered.sort_values("avg_review", ascending=False).head(top_n)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=best["product_category_name_english"][::-1],
        x=best["avg_review"][::-1],
        orientation="h",
        marker=dict(color=best["avg_review"][::-1], colorscale="Greens"),
        text=best["avg_review"][::-1].apply(lambda x: f"{x:.2f} ⭐"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(400, top_n * 28),
        xaxis_title="Nota Média", yaxis_title="",
        xaxis_range=[1, 5.3],
        margin=dict(l=180),
        title=f"Top {top_n} Categorias com Melhor Satisfação (mín. {min_items} itens)",
    )
    plot_chart(fig)

with tab2:
    worst = cat_filtered.sort_values("avg_review", ascending=True).head(top_n)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=worst["product_category_name_english"],
        x=worst["avg_review"],
        orientation="h",
        marker=dict(color=worst["avg_review"], colorscale="Reds_r"),
        text=worst["avg_review"].apply(lambda x: f"{x:.2f} ⭐"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(400, top_n * 28),
        xaxis_title="Nota Média", yaxis_title="",
        xaxis_range=[1, 5.3],
        margin=dict(l=180),
        title=f"Top {top_n} Categorias com Pior Satisfação (mín. {min_items} itens)",
    )
    plot_chart(fig)

st.markdown("---")

# --- Scatter: Receita vs Nota ---
st.markdown("### Receita vs. Nota Média por Categoria")

fig = px.scatter(
    cat_filtered,
    x="total_revenue",
    y="avg_review",
    size="total_items",
    color="delay_rate",
    color_continuous_scale="RdYlGn_r",
    hover_name="product_category_name_english",
    labels={
        "total_revenue": "Receita Total (R$)",
        "avg_review": "Nota Média",
        "total_items": "Itens Vendidos",
        "delay_rate": "Taxa de Atraso",
    },
    template="plotly_dark",
    height=550,
)
plot_chart(fig)
