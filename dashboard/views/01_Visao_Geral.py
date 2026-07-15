"""
CommercePulse Dashboard — Visão Geral.

KPIs principais, GMV mensal e visão macro do e-commerce.
"""

import plotly.graph_objects as go
import streamlit as st

from dashboard.utils import (
    compute_kpis,
    compute_monthly_revenue,
    format_currency,
    format_currency_compact,
    format_integer,
    format_pct,
    load_data,
    plot_chart,
    set_page_style,
)

st.set_page_config(
    page_title="Visão Geral — CommercePulse",
    page_icon=":material/analytics:",
    layout="wide",
)
set_page_style()

st.title("Visão Geral")
st.markdown("KPIs principais e evolução do valor bruto de mercadorias (GMV).")

# --- Carregar dados ---
df = load_data()

# --- Filtros na sidebar ---
st.sidebar.header("Filtros")
years = sorted(df["purchase_year"].unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years)

states = sorted(df["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect("Estado do Cliente", states, default=states)

# Aplicar filtros
mask = df["purchase_year"].isin(selected_years) & df["customer_state"].isin(selected_states)
df_filtered = df[mask]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# --- KPIs ---
kpis = compute_kpis(df_filtered)

st.markdown("### KPIs Principais")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Pedidos", format_integer(kpis["total_orders"]))
col2.metric(
    "GMV (Produtos)",
    format_currency_compact(kpis["total_revenue"]),
    help=format_currency(kpis["total_revenue"]),
)
col3.metric(
    "Ticket Médio",
    format_currency_compact(kpis["avg_ticket"]),
    help=format_currency(kpis["avg_ticket"]),
)
col4.metric("Nota Média", f"{kpis['avg_review']:.2f}")
col5.metric("Taxa de Atraso", format_pct(kpis["delay_rate"]))

col6, col7, col8, col9, col10 = st.columns(5)
col6.metric("Itens em Pedidos", format_integer(kpis["total_items"]))
col7.metric(
    "GMV + Frete",
    format_currency_compact(kpis["total_revenue_freight"]),
    help=format_currency(kpis["total_revenue_freight"]),
)
col8.metric("Entrega Média", f"{kpis['avg_delivery_days']:.0f} dias")
col9.metric("Categorias", f"{kpis['n_categories']}")
col10.metric("Vendedores", format_integer(kpis["n_sellers"]))

st.markdown("---")

# --- GMV Mensal ---
st.markdown("### Evolução do GMV Mensal")

monthly = compute_monthly_revenue(df_filtered)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=monthly["purchase_year_month"],
    y=monthly["revenue"],
    mode="lines+markers",
    name="GMV (Produtos)",
    line=dict(color="#636EFA", width=2.5),
    marker=dict(size=6),
    fill="tozeroy",
    fillcolor="rgba(99, 110, 250, 0.1)",
))

fig.add_trace(go.Scatter(
    x=monthly["purchase_year_month"],
    y=monthly["total_value"],
    mode="lines+markers",
    name="GMV (Produtos + Frete)",
    line=dict(color="#00CC96", width=2, dash="dot"),
    marker=dict(size=5),
))

fig.update_layout(
    template="plotly_dark",
    height=450,
    title_font_size=16,
    xaxis_title="Mês",
    yaxis_title="GMV (R$)",
    legend=dict(x=0.01, y=0.99),
    hovermode="x unified",
)
plot_chart(fig)

# --- Pedidos e Ticket Médio ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Pedidos e Itens por Mês")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=monthly["purchase_year_month"],
        y=monthly["orders"],
        name="Pedidos",
        marker_color="#636EFA",
        opacity=0.8,
    ))
    fig2.add_trace(go.Bar(
        x=monthly["purchase_year_month"],
        y=monthly["items"],
        name="Itens",
        marker_color="#EF553B",
        opacity=0.6,
    ))
    fig2.update_layout(
        template="plotly_dark",
        height=400,
        barmode="group",
        xaxis_title="Mês",
        yaxis_title="Quantidade",
        legend=dict(x=0.01, y=0.99),
    )
    plot_chart(fig2)

with col_right:
    st.markdown("### Ticket Médio Mensal")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=monthly["purchase_year_month"],
        y=monthly["ticket_medio"],
        mode="lines+markers",
        line=dict(color="#FFA15A", width=2.5),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(255, 161, 90, 0.1)",
    ))
    fig3.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title="Mês",
        yaxis_title="Ticket Médio (R$)",
    )
    plot_chart(fig3)

# --- Nota média mensal ---
st.markdown("### Nota Média Mensal")
fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=monthly["purchase_year_month"],
    y=monthly["avg_review"],
    mode="lines+markers",
    line=dict(color="#AB63FA", width=2.5),
    marker=dict(size=7),
))

# Linhas de referência
fig4.add_hline(y=monthly["avg_review"].mean(), line_dash="dash",
               line_color="rgba(255,255,255,0.3)",
               annotation_text=f"Média: {monthly['avg_review'].mean():.2f}")

fig4.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="Mês",
    yaxis_title="Nota Média",
    yaxis_range=[1, 5.2],
)
plot_chart(fig4)
