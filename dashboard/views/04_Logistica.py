"""
CommercePulse Dashboard — Análise de Logística.

Taxa de atraso, tempo de entrega, impacto na satisfação.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from dashboard.utils import (
    compute_state_metrics,
    format_integer,
    get_delivered_orders,
    load_data,
    plot_chart,
    set_page_style,
)

st.set_page_config(
    page_title="Logística — CommercePulse",
    page_icon=":material/local_shipping:",
    layout="wide",
)
set_page_style()

st.title("Logística e Entregas")
st.markdown("Análise de atrasos, tempo de entrega e impacto na satisfação do cliente.")

df = load_data()

# --- Filtros ---
st.sidebar.header("Filtros")
years = sorted(df["purchase_year"].unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years, key="log_year")

mask = df["purchase_year"].isin(selected_years)
df_filtered = df[mask]
delivered = get_delivered_orders(df_filtered)

if delivered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# --- KPIs de logística ---
st.markdown("### KPIs de Logística")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Taxa de Atraso", f"{delivered['is_late'].mean()*100:.1f}%")
col2.metric("Entrega Média", f"{delivered['delivery_days'].mean():.1f} dias")
col3.metric("Entrega Mediana", f"{delivered['delivery_days'].median():.0f} dias")
col4.metric("Pedidos Atrasados", format_integer(delivered["is_late"].sum()))

st.markdown("---")

# --- Distribuição do tempo de entrega ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Distribuição do Tempo de Entrega")
    fig = px.histogram(
        delivered,
        x="delivery_days",
        nbins=50,
        color_discrete_sequence=["#636EFA"],
        labels={"delivery_days": "Dias para Entrega", "count": "Frequência"},
        template="plotly_dark",
        height=400,
    )
    fig.add_vline(
        x=delivered["delivery_days"].mean(),
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Média: {delivered['delivery_days'].mean():.0f}d",
    )
    plot_chart(fig)

with col_right:
    st.markdown("### Distribuição dos Dias de Atraso")
    late = delivered[delivered["is_late"] == 1]
    if not late.empty:
        fig = px.histogram(
            late,
            x="delay_days",
            nbins=40,
            color_discrete_sequence=["#EF553B"],
            labels={"delay_days": "Dias de Atraso", "count": "Frequência"},
            template="plotly_dark",
            height=400,
        )
        fig.add_vline(
            x=late["delay_days"].mean(),
            line_dash="dash",
            line_color="yellow",
            annotation_text=f"Média: {late['delay_days'].mean():.0f}d",
        )
        plot_chart(fig)
    else:
        st.info("Nenhum pedido atrasado no período selecionado.")

st.markdown("---")

# --- Atraso vs Avaliação ---
st.markdown("### Avaliação por Status de Entrega")

col_left2, col_right2 = st.columns(2)

with col_left2:
    # Box plot: nota por status de atraso
    delivered_plot = delivered.copy()
    delivered_plot["status_entrega"] = delivered_plot["is_late"].map({0: "No Prazo", 1: "Atrasado"})

    fig = px.box(
        delivered_plot,
        x="status_entrega",
        y="review_score",
        color="status_entrega",
        color_discrete_map={"No Prazo": "#00CC96", "Atrasado": "#EF553B"},
        labels={"status_entrega": "Status da Entrega", "review_score": "Nota de Avaliação"},
        template="plotly_dark",
        height=450,
        title="Distribuição de Notas: No Prazo vs Atrasado",
    )
    fig.update_layout(showlegend=False, title_font_size=16)
    plot_chart(fig)

with col_right2:
    # Nota média por status
    avg_by_status = (
        delivered_plot.groupby("status_entrega")["review_score"]
        .agg(["mean", "median", "count"])
        .reset_index()
    )
    avg_by_status.columns = ["Status", "Nota Média", "Nota Mediana", "Qtd Pedidos"]

    st.markdown("#### Comparação de Notas")
    st.dataframe(avg_by_status, width="stretch", hide_index=True)

    # Nota média por faixa de atraso
    st.markdown("#### Nota por Faixa de Atraso")
    late_copy = late.copy()
    if not late_copy.empty:
        bins = [0, 3, 7, 14, 30, float("inf")]
        labels = ["1-3 dias", "4-7 dias", "8-14 dias", "15-30 dias", "30+ dias"]
        late_copy["faixa_atraso"] = pd.cut(
            late_copy["delay_days"], bins=bins, labels=labels, right=True
        )

        faixa = (
            late_copy.groupby("faixa_atraso", observed=True)["review_score"]
            .agg(["mean", "count"])
            .reset_index()
        )
        faixa.columns = ["Faixa de Atraso", "Nota Média", "Qtd Pedidos"]
        faixa["Nota Média"] = faixa["Nota Média"].round(2)
        st.dataframe(faixa, width="stretch", hide_index=True)

st.markdown("---")

# --- Taxa de atraso por estado ---
st.markdown("### Taxa de Atraso por Estado")

state_metrics = compute_state_metrics(df_filtered)
state_sorted = state_metrics.sort_values("delay_rate", ascending=False)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=state_sorted["customer_state"],
    y=state_sorted["delay_rate"] * 100,
    marker=dict(
        color=state_sorted["delay_rate"] * 100,
        colorscale="YlOrRd",
        showscale=True,
        colorbar=dict(title="Taxa de<br>Atraso (%)"),
    ),
    text=state_sorted["delay_rate"].apply(lambda x: f"{x*100:.1f}%"),
    textposition="outside",
))
fig.update_layout(
    template="plotly_dark", height=500,
    xaxis_title="Estado", yaxis_title="Taxa de Atraso (%)",
)
plot_chart(fig)

# --- Tempo médio de entrega por estado ---
st.markdown("### Tempo Médio de Entrega por Estado")

state_delivery = state_metrics.sort_values("avg_delivery_days", ascending=False)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=state_delivery["customer_state"],
    y=state_delivery["avg_delivery_days"],
    marker=dict(
        color=state_delivery["avg_delivery_days"],
        colorscale="Purples",
    ),
    text=state_delivery["avg_delivery_days"].apply(lambda x: f"{x:.0f}d"),
    textposition="outside",
))
fig.update_layout(
    template="plotly_dark", height=500,
    xaxis_title="Estado", yaxis_title="Tempo Médio (dias)",
)
plot_chart(fig)
