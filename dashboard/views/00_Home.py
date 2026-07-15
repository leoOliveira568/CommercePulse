import streamlit as st

# --- Página Principal ---
st.title("CommercePulse")
st.markdown("### Análise 360° do E-commerce Brasileiro")

st.markdown("---")

st.markdown("""
**Bem-vindo ao CommercePulse Dashboard!**

Este dashboard consolida as análises exploratórias do e-commerce brasileiro (Olist),
apresentando métricas de desempenho, análises geográficas, de categorias, logística,
vendedores e segmentação de clientes.

---

#### Navegação

Use o menu lateral para navegar entre as páginas:

| Página | Descrição |
|--------|-----------|
| **Visão Geral** | KPIs principais, receita mensal, visão macro do negócio |
| **Geográfica** | Análise por estado, concentração de receita, frete |
| **Categorias** | Top categorias, ticket médio, satisfação por segmento |
| **Logística** | Taxa de atraso, impacto na nota, tempo de entrega |
| **Vendedores** | Ranking de vendedores, concentração de atrasos |
| **Clientes (RFM)** | Segmentação de clientes por Recência, Frequência e Valor |

---

#### Sobre os Dados

- **Fonte:** Olist Store (Kaggle — Brazilian E-Commerce Public Dataset)
- **Período:** 2016 a 2018
- **Granularidade:** 1 linha por item vendido
- **Volume:** ~112.650 itens, ~98.666 pedidos, ~95.420 clientes únicos
""")

st.markdown("---")
st.caption("CommercePulse © 2026 — Análise de dados de e-commerce brasileiro")
