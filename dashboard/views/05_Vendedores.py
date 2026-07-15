"""
CommercePulse Dashboard — Análise de Vendedores.

Ranking de vendedores, concentração de atrasos e métricas de performance.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from dashboard.utils import (
    compute_seller_metrics,
    format_currency,
    format_integer,
    get_delivered_order_sellers,
    load_data,
    plot_chart,
    set_page_style,
)

st.set_page_config(
    page_title="Vendedores — CommercePulse",
    page_icon=":material/storefront:",
    layout="wide",
)
set_page_style()

st.title("Análise de Vendedores")
st.markdown("Ranking de performance, concentração de atrasos e métricas por vendedor.")

df = load_data()

# --- Filtros ---
st.sidebar.header("Filtros")
years = sorted(df["purchase_year"].unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years, key="seller_year")
min_orders = st.sidebar.slider("Mín. de pedidos por vendedor", 1, 100, 30, key="min_orders")

mask = df["purchase_year"].isin(selected_years)
df_filtered = df[mask]
delivered = get_delivered_order_sellers(df_filtered)

if delivered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

seller_metrics = compute_seller_metrics(df_filtered)

# --- KPIs de vendedores ---
st.markdown("### Visão Geral dos Vendedores")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Vendedores", format_integer(len(seller_metrics)))
col2.metric(
    f"Com ≥ {min_orders} pedidos",
    format_integer((seller_metrics["total_orders"] >= min_orders).sum()),
)
col3.metric("GMV Médio / Vendedor", format_currency(seller_metrics["total_revenue"].mean()))
col4.metric("Taxa Atraso Média", f"{seller_metrics['delay_rate'].mean()*100:.1f}%")

st.markdown("---")

# Filtrar por volume mínimo
sellers_filtered = seller_metrics[seller_metrics["total_orders"] >= min_orders].copy()
sellers_filtered = sellers_filtered.sort_values("delay_rate", ascending=False)

# --- Top vendedores com mais atrasos ---
st.markdown(f"### Vendedores com Maiores Taxas de Atraso (mín. {min_orders} pedidos)")

top20 = sellers_filtered.head(20)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=top20["seller_id"].str[:8] + "...",
    y=top20["delay_rate"] * 100,
    marker=dict(
        color=top20["delay_rate"] * 100,
        colorscale="Reds",
        showscale=True,
        colorbar=dict(title="Taxa de<br>Atraso (%)"),
    ),
    text=top20["delay_rate"].apply(lambda x: f"{x*100:.1f}%"),
    textposition="outside",
))
fig.update_layout(
    template="plotly_dark", height=500,
    xaxis_title="Vendedor (ID parcial)", yaxis_title="Taxa de Atraso (%)",
    xaxis_tickangle=-45,
)
plot_chart(fig)

st.markdown("---")

# --- Pareto ---
st.markdown("### Concentração de Atrasos (Pareto)")

all_sellers = seller_metrics.copy()
pareto = all_sellers[all_sellers["late_orders"] > 0].sort_values(
    "late_orders", ascending=False
).reset_index(drop=True)
pareto["cumulative_late"] = pareto["late_orders"].cumsum()
pareto["cumulative_pct"] = pareto["cumulative_late"] / pareto["late_orders"].sum() * 100

n_80 = int((pareto["cumulative_pct"] <= 80).sum()) + 1
pct_sellers_80 = n_80 / len(all_sellers) * 100

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=list(range(1, len(pareto) + 1)),
        y=pareto["late_orders"],
        name="Pedidos Atrasados",
        marker_color="#EF553B",
        opacity=0.7,
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=list(range(1, len(pareto) + 1)),
        y=pareto["cumulative_pct"],
        name="% Acumulado",
        line=dict(color="#00CC96", width=2.5),
    ),
    secondary_y=True,
)
fig.add_hline(y=80, line_dash="dash", line_color="yellow", opacity=0.5, secondary_y=True)

fig.update_layout(
    title=f"{n_80} vendedores ({pct_sellers_80:.0f}%) concentram 80% dos atrasos",
    template="plotly_dark", height=450,
    xaxis_title="Vendedores (ordenados por atrasos)",
    legend=dict(x=0.65, y=0.3),
    title_font_size=16,
)
fig.update_yaxes(title_text="Pedidos Atrasados", secondary_y=False)
fig.update_yaxes(title_text="% Acumulado", secondary_y=True)
plot_chart(fig)

st.info(
    f"**{n_80} vendedores** ({pct_sellers_80:.1f}% do total) estão "
    "associados a 80% dos pedidos atrasados."
)

st.markdown("---")

# --- Scatter: Atraso vs Nota ---
st.markdown("### Taxa de Atraso vs. Nota Média por Vendedor")

fig = px.scatter(
    sellers_filtered,
    x="delay_rate",
    y="avg_review",
    size="total_orders",
    color="seller_state",
    hover_data=["seller_id", "total_orders", "total_revenue"],
    labels={
        "delay_rate": "Taxa de Atraso",
        "avg_review": "Nota Média",
        "total_orders": "Total de Pedidos",
        "seller_state": "Estado",
    },
    template="plotly_dark",
    height=550,
)
fig.update_layout(xaxis_tickformat=".0%")
plot_chart(fig)

st.markdown("---")

# --- Taxa de atraso por estado do vendedor ---
st.markdown("### Taxa de Atraso por Estado do Vendedor")

state_seller = delivered.groupby("seller_state").agg(
    total_sellers=("seller_id", "nunique"),
    avg_delay_rate=("is_late", "mean"),
    total_orders=("order_id", "nunique"),
    avg_review=("review_score", "mean"),
    total_revenue=("order_revenue", "sum"),
).reset_index().sort_values("avg_delay_rate", ascending=False)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=state_seller["seller_state"],
    y=state_seller["avg_delay_rate"] * 100,
    marker=dict(
        color=state_seller["avg_delay_rate"] * 100,
        colorscale="YlOrRd",
    ),
    text=state_seller["avg_delay_rate"].apply(lambda x: f"{x*100:.1f}%"),
    textposition="outside",
))
fig.update_layout(
    template="plotly_dark", height=500,
    xaxis_title="Estado do Vendedor", yaxis_title="Taxa de Atraso (%)",
)
plot_chart(fig)

# --- Tabela ---
st.markdown("### Tabela: Top Vendedores por GMV")
top_revenue_sellers = sellers_filtered.sort_values("total_revenue", ascending=False).head(30).copy()
top_revenue_sellers["seller_id_short"] = top_revenue_sellers["seller_id"].str[:12] + "..."
display_cols = ["seller_id_short", "seller_state", "seller_city", "total_orders",
                "total_revenue", "avg_review", "delay_rate", "avg_delivery_days"]
display_df = top_revenue_sellers[display_cols].copy()
display_df["total_revenue"] = display_df["total_revenue"].apply(format_currency)
display_df["avg_review"] = display_df["avg_review"].round(2)
display_df["delay_rate"] = display_df["delay_rate"].apply(lambda x: f"{x*100:.1f}%")
display_df["avg_delivery_days"] = display_df["avg_delivery_days"].round(1)
display_df.columns = [
    "Vendedor", "Estado", "Cidade", "Pedidos", "GMV", "Nota", "Atraso",
    "Entrega (dias)",
]
st.dataframe(display_df, width="stretch", hide_index=True)
