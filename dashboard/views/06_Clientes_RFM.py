"""
CommercePulse Dashboard — Segmentação de Clientes (RFM).

Análise de Recency, Frequency e Monetary dos clientes do e-commerce.
"""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import load_data, load_rfm, set_page_style, plot_chart

st.set_page_config(page_title="Clientes RFM — CommercePulse", page_icon=":material/group:", layout="wide")
set_page_style()

st.title("Segmentação de Clientes (RFM)")
st.markdown("Análise de comportamento dos clientes com base em **Recência**, **Frequência** e **Valor Monetário**.")

rfm = load_rfm()

if rfm is None:
    st.error(
        "A tabela RFM não foi encontrada. "
        "Execute `python src/make_rfm_dataset.py` para gerá-la."
    )
    st.stop()

# --- Definir cores por segmento ---
SEGMENT_COLORS = {
    "Champions": "#636EFA",
    "Loyal Customers": "#00CC96",
    "Potential Loyalists": "#AB63FA",
    "New Customers": "#FFA15A",
    "At Risk": "#EF553B",
    "Hibernating": "#FF6692",
    "Others": "#B6E880",
}

# --- KPIs ---
st.markdown("### Visão Geral da Base de Clientes")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Clientes", f"{len(rfm):,}")
col2.metric("Ticket Médio (Monetary)", f"R$ {rfm['monetary'].mean():,.2f}")
col3.metric("Frequência Média", f"{rfm['frequency'].mean():.2f}")
col4.metric("Recência Média", f"{rfm['recency'].mean():.0f} dias")

col5, col6, col7, col8 = st.columns(4)
col5.metric("% Compra Única", f"{(rfm['frequency'] == 1).mean() * 100:.1f}%")
col6.metric("Champions", f"{(rfm['segment'] == 'Champions').sum():,}")
col7.metric("At Risk", f"{(rfm['segment'] == 'At Risk').sum():,}")
col8.metric("Score RFM Médio", f"{rfm['RFM_score'].mean():.1f}")

st.markdown("---")

# --- Distribuição de Segmentos ---
st.markdown("### Distribuição por Segmento")

col_left, col_right = st.columns(2)

with col_left:
    seg_counts = rfm["segment"].value_counts().reset_index()
    seg_counts.columns = ["Segmento", "Clientes"]

    fig = px.pie(
        seg_counts,
        names="Segmento",
        values="Clientes",
        color="Segmento",
        color_discrete_map=SEGMENT_COLORS,
        hole=0.45,
        template="plotly_dark",
        height=450,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont_size=12,
    )
    fig.update_layout(
        showlegend=False,
        title="Proporção de Clientes por Segmento",
        title_font_size=16,
    )
    plot_chart(fig)

with col_right:
    fig = px.bar(
        seg_counts.sort_values("Clientes", ascending=True),
        x="Clientes",
        y="Segmento",
        orientation="h",
        color="Segmento",
        color_discrete_map=SEGMENT_COLORS,
        template="plotly_dark",
        height=450,
        text="Clientes",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        title="Quantidade de Clientes por Segmento",
        title_font_size=16,
        xaxis_title="Clientes",
        yaxis_title="",
    )
    plot_chart(fig)

st.markdown("---")

# --- Métricas por Segmento ---
st.markdown("### Métricas Médias por Segmento")

seg_metrics = rfm.groupby("segment").agg(
    clientes=("customer_unique_id", "count"),
    recency_media=("recency", "mean"),
    frequency_media=("frequency", "mean"),
    monetary_media=("monetary", "mean"),
    rfm_score_medio=("RFM_score", "mean"),
).reset_index().sort_values("monetary_media", ascending=False)

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.markdown("#### Valor Monetário Médio")
    fig = px.bar(
        seg_metrics.sort_values("monetary_media"),
        x="monetary_media",
        y="segment",
        orientation="h",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        template="plotly_dark",
        height=400,
        labels={"monetary_media": "Valor Monetário Médio (R$)", "segment": ""},
        text=seg_metrics.sort_values("monetary_media")["monetary_media"].apply(lambda x: f"R$ {x:,.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    plot_chart(fig)

with col_right2:
    st.markdown("#### Recência Média (dias)")
    fig = px.bar(
        seg_metrics.sort_values("recency_media"),
        x="recency_media",
        y="segment",
        orientation="h",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        template="plotly_dark",
        height=400,
        labels={"recency_media": "Recência Média (dias)", "segment": ""},
        text=seg_metrics.sort_values("recency_media")["recency_media"].apply(lambda x: f"{x:.0f}d"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    plot_chart(fig)

st.markdown("---")

# --- Scatter 3D: R x F x M ---
st.markdown("### Mapa 3D: Recência × Frequência × Valor Monetário")

# Amostragem para performance (scatter 3D com +90k pontos é pesado)
sample_size = min(5000, len(rfm))
rfm_sample = rfm.sample(n=sample_size, random_state=42)

fig = px.scatter_3d(
    rfm_sample,
    x="recency",
    y="frequency",
    z="monetary",
    color="segment",
    color_discrete_map=SEGMENT_COLORS,
    opacity=0.6,
    template="plotly_dark",
    height=600,
    labels={
        "recency": "Recência (dias)",
        "frequency": "Frequência",
        "monetary": "Valor Monetário (R$)",
        "segment": "Segmento",
    },
)
fig.update_layout(
    scene=dict(
        xaxis=dict(backgroundcolor="rgba(0,0,0,0)"),
        yaxis=dict(backgroundcolor="rgba(0,0,0,0)"),
        zaxis=dict(backgroundcolor="rgba(0,0,0,0)"),
    ),
    legend=dict(
        yanchor="top", y=0.99,
        xanchor="left", x=0.01,
        bgcolor="rgba(15, 23, 42, 0.8)",
    ),
)
plot_chart(fig)

st.caption(f"Exibindo amostra de {sample_size:,} clientes para melhor performance.")

st.markdown("---")

# --- Distribuição de Frequência ---
st.markdown("### Distribuição da Frequência de Compras")

freq_dist = rfm["frequency"].value_counts().sort_index().reset_index()
freq_dist.columns = ["Frequência", "Clientes"]

fig = px.bar(
    freq_dist.head(10),
    x="Frequência",
    y="Clientes",
    color_discrete_sequence=["#636EFA"],
    template="plotly_dark",
    height=400,
    text="Clientes",
    labels={"Frequência": "Nº de Compras", "Clientes": "Quantidade de Clientes"},
)
fig.update_traces(texttemplate="%{text:,}", textposition="outside")
fig.update_layout(title="Top 10 Frequências de Compra", title_font_size=16)
plot_chart(fig)

pct_single = (rfm["frequency"] == 1).mean() * 100
st.info(
    f"**{pct_single:.1f}%** dos clientes realizaram apenas **1 compra**. "
    "Isso revela uma grande oportunidade de retenção — "
    "programas de incentivo à segunda compra podem gerar receita incremental significativa."
)

st.markdown("---")

# --- Tabela de Segmentos ---
st.markdown("### Resumo por Segmento")

display_metrics = seg_metrics.copy()
display_metrics["monetary_media"] = display_metrics["monetary_media"].apply(lambda x: f"R$ {x:,.2f}")
display_metrics["recency_media"] = display_metrics["recency_media"].apply(lambda x: f"{x:.0f} dias")
display_metrics["frequency_media"] = display_metrics["frequency_media"].apply(lambda x: f"{x:.2f}")
display_metrics["rfm_score_medio"] = display_metrics["rfm_score_medio"].apply(lambda x: f"{x:.1f}")
display_metrics["clientes"] = display_metrics["clientes"].apply(lambda x: f"{x:,}")
display_metrics.columns = ["Segmento", "Clientes", "Recência Média", "Frequência Média",
                           "Valor Monetário Médio", "Score RFM Médio"]
st.dataframe(display_metrics, use_container_width=True, hide_index=True)

# --- Ações Recomendadas ---
st.markdown("### Ações Recomendadas por Segmento")

recommendations = {
    "Champions": "Programa de fidelidade VIP, acesso antecipado a promoções, programa de indicação com recompensas.",
    "Loyal Customers": "Cross-sell personalizado, cupons de aniversário, recompensas por indicação de novos clientes.",
    "Potential Loyalists": "Ofertas personalizadas por categoria, programas de pontos, comunicação frequente.",
    "New Customers": "Cupom de segunda compra (7-14 dias após entrega), e-mail de boas-vindas e onboarding.",
    "At Risk": "Campanha de retenção urgente: descontos agressivos, pesquisa de satisfação, re-engajamento.",
    "Hibernating": "Campanha de reativação com desconto generoso, lembrete por e-mail, oferta de frete grátis.",
    "Others": "Monitoramento contínuo e comunicação por categoria de interesse.",
}

for seg, rec in recommendations.items():
    count = (rfm["segment"] == seg).sum()
    if count > 0:
        st.markdown(f"**{seg}** ({count:,} clientes): {rec}")
