"""
CommercePulse Dashboard — Análise Geográfica.

GMV, frete e satisfação por estado do cliente.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.utils import (
    compute_state_metrics,
    format_currency,
    load_data,
    plot_chart,
    set_page_style,
)

st.set_page_config(
    page_title="Geográfica — CommercePulse",
    page_icon=":material/public:",
    layout="wide",
)
set_page_style()

st.title("Análise Geográfica")
st.markdown("Distribuição de pedidos, GMV e frete por estado do Brasil.")

df = load_data()

# --- Filtros ---
st.sidebar.header("Filtros")
years = sorted(df["purchase_year"].unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years, key="geo_year")

mask = df["purchase_year"].isin(selected_years)
df_filtered = df[mask]

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

state_metrics = compute_state_metrics(df_filtered)

# --- Top 10 estados por GMV ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Top 10 Estados por GMV")
    top_revenue = state_metrics.sort_values("total_revenue", ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_revenue["customer_state"],
        y=top_revenue["total_revenue"],
        marker=dict(
            color=top_revenue["total_revenue"],
            colorscale="Viridis",
        ),
        text=top_revenue["total_revenue"].apply(lambda x: f"R$ {x/1000:.0f}k"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=450,
        xaxis_title="Estado", yaxis_title="GMV (R$)",
    )
    plot_chart(fig)

with col_right:
    st.markdown("### Top 10 Estados por Volume de Pedidos")
    top_orders = state_metrics.sort_values("total_orders", ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_orders["customer_state"],
        y=top_orders["total_orders"],
        marker=dict(
            color=top_orders["total_orders"],
            colorscale="Blues",
        ),
        text=top_orders["total_orders"].apply(lambda x: f"{x:,}"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=450,
        xaxis_title="Estado", yaxis_title="Pedidos",
    )
    plot_chart(fig)

st.markdown("---")

# --- Frete médio e nota por estado ---
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.markdown("### Valor Médio de Frete por Estado")
    state_sorted_freight = state_metrics.sort_values("avg_freight", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=state_sorted_freight["customer_state"],
        y=state_sorted_freight["avg_freight"],
        marker=dict(
            color=state_sorted_freight["avg_freight"],
            colorscale="YlOrRd",
        ),
        text=state_sorted_freight["avg_freight"].apply(lambda x: f"R$ {x:.0f}"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=450,
        xaxis_title="Estado", yaxis_title="Frete Médio (R$)",
    )
    plot_chart(fig)

with col_right2:
    st.markdown("### Nota Média por Estado")
    state_sorted_review = state_metrics.sort_values("avg_review", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=state_sorted_review["customer_state"],
        y=state_sorted_review["avg_review"],
        marker=dict(
            color=state_sorted_review["avg_review"],
            colorscale="RdYlGn",
        ),
        text=state_sorted_review["avg_review"].apply(lambda x: f"{x:.2f}"),
        textposition="outside",
    ))
    fig.update_layout(
        template="plotly_dark", height=450,
        xaxis_title="Estado", yaxis_title="Nota Média",
        yaxis_range=[1, 5.3],
    )
    plot_chart(fig)

st.markdown("---")

# --- Scatter: Frete vs Nota ---
st.markdown("### Frete Médio vs. Nota Média por Estado")

fig = px.scatter(
    state_metrics,
    x="avg_freight",
    y="avg_review",
    size="total_orders",
    text="customer_state",
    color="delay_rate",
    color_continuous_scale="RdYlGn_r",
    labels={
        "avg_freight": "Frete Médio (R$)",
        "avg_review": "Nota Média",
        "total_orders": "Total de Pedidos",
        "delay_rate": "Taxa de Atraso",
    },
    template="plotly_dark",
    height=550,
)
fig.update_traces(textposition="top center")
plot_chart(fig)

# --- Tabela completa ---
st.markdown("### Tabela Completa por Estado")
display_df = state_metrics.copy()
display_df["total_revenue"] = display_df["total_revenue"].apply(format_currency)
display_df["avg_ticket"] = display_df["avg_ticket"].apply(format_currency)
display_df["avg_freight"] = display_df["avg_freight"].apply(format_currency)
display_df["avg_review"] = display_df["avg_review"].round(2)
display_df["delay_rate"] = display_df["delay_rate"].apply(lambda x: f"{x*100:.1f}%")
display_df["avg_delivery_days"] = display_df["avg_delivery_days"].round(1)

display_df.columns = [
    "Estado", "Pedidos", "GMV", "Ticket Médio",
    "Frete Médio", "Nota Média", "Entrega (dias)", "Taxa Atraso",
]
st.dataframe(
    display_df.sort_values("Pedidos", ascending=False),
    width="stretch",
    hide_index=True,
)
