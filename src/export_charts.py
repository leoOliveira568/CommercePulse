"""
CommercePulse — Exportação de Gráficos para Relatórios.

Gera imagens PNG dos gráficos principais para incorporar em relatórios
executivos e apresentações.

Uso:
    python src/export_charts.py

Dependências:
    pip install plotly kaleido
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"

PLOTLY_TEMPLATE = "plotly_dark"


def load_data() -> pd.DataFrame:
    """Carrega a base processada."""
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


def get_delivered_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida métricas logísticas em uma linha por pedido entregue."""
    orders = df.groupby("order_id", as_index=False).agg(
        customer_state=("customer_state", "first"),
        review_score=("review_score", "first"),
        is_delivered=("is_delivered", "first"),
        is_late=("is_late", "first"),
    )
    return orders[(orders["is_delivered"] == 1) & orders["is_late"].notna()].copy()


def export_revenue_monthly(df: pd.DataFrame) -> None:
    """Exporta gráfico de GMV mensal."""
    monthly = df.groupby("purchase_year_month").agg(
        revenue=("item_revenue", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index().sort_values("purchase_year_month")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["purchase_year_month"],
        y=monthly["revenue"],
        mode="lines+markers",
        line=dict(color="#636EFA", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(99, 110, 250, 0.1)",
    ))
    fig.update_layout(
        title="Evolução do GMV Mensal",
        template=PLOTLY_TEMPLATE,
        height=400, width=900,
        xaxis_title="Mês", yaxis_title="GMV (R$)",
    )
    fig.write_image(str(CHARTS_DIR / "gmv_mensal.png"), scale=2)
    print("  [OK] gmv_mensal.png")


def export_top_states(df: pd.DataFrame) -> None:
    """Exporta gráfico de top estados por GMV."""
    state = df.groupby("customer_state").agg(
        revenue=("item_revenue", "sum"),
    ).reset_index().sort_values("revenue", ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=state["customer_state"],
        y=state["revenue"],
        marker=dict(color=state["revenue"], colorscale="Viridis"),
        text=state["revenue"].apply(lambda x: f"R$ {x/1e6:.1f}M"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Top 10 Estados por GMV",
        template=PLOTLY_TEMPLATE,
        height=400, width=800,
        xaxis_title="Estado", yaxis_title="GMV (R$)",
    )
    fig.write_image(str(CHARTS_DIR / "top_estados_gmv.png"), scale=2)
    print("  [OK] top_estados_gmv.png")


def export_top_categories(df: pd.DataFrame) -> None:
    """Exporta gráfico de top categorias por GMV."""
    cat = df.groupby("product_category_name_english").agg(
        revenue=("item_revenue", "sum"),
    ).reset_index().dropna().sort_values("revenue", ascending=True).tail(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cat["product_category_name_english"],
        x=cat["revenue"],
        orientation="h",
        marker=dict(color=cat["revenue"], colorscale="Viridis"),
        text=cat["revenue"].apply(lambda x: f"R$ {x/1e3:.0f}k"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Top 10 Categorias por GMV",
        template=PLOTLY_TEMPLATE,
        height=450, width=800,
        xaxis_title="GMV (R$)", yaxis_title="",
        margin=dict(l=180),
    )
    fig.write_image(str(CHARTS_DIR / "top_categorias_gmv.png"), scale=2)
    print("  [OK] top_categorias_gmv.png")


def export_delay_impact(df: pd.DataFrame) -> None:
    """Exporta gráfico de impacto do atraso na avaliação."""
    delivered = get_delivered_orders(df)
    delivered["status"] = delivered["is_late"].map({0: "No Prazo", 1: "Atrasado"})

    avg = delivered.groupby("status")["review_score"].mean().reset_index()

    fig = go.Figure()
    colors = {"No Prazo": "#00CC96", "Atrasado": "#EF553B"}
    fig.add_trace(go.Bar(
        x=avg["status"],
        y=avg["review_score"],
        marker_color=[colors[s] for s in avg["status"]],
        text=avg["review_score"].apply(lambda x: f"{x:.2f} ⭐"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Avaliação do Cliente por Status de Entrega",
        template=PLOTLY_TEMPLATE,
        height=400, width=600,
        xaxis_title="Status da Entrega", yaxis_title="Nota Média",
        yaxis_range=[0, 5.5],
    )
    fig.write_image(str(CHARTS_DIR / "impacto_atraso_avaliacao.png"), scale=2)
    print("  [OK] impacto_atraso_avaliacao.png")


def export_delay_by_state(df: pd.DataFrame) -> None:
    """Exporta gráfico de taxa de atraso por estado."""
    delivered = get_delivered_orders(df)
    state = delivered.groupby("customer_state").agg(
        delay_rate=("is_late", "mean"),
    ).reset_index().sort_values("delay_rate", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=state["customer_state"],
        y=state["delay_rate"] * 100,
        marker=dict(color=state["delay_rate"] * 100, colorscale="YlOrRd"),
        text=state["delay_rate"].apply(lambda x: f"{x*100:.1f}%"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Taxa de Atraso por Estado do Cliente",
        template=PLOTLY_TEMPLATE,
        height=400, width=900,
        xaxis_title="Estado", yaxis_title="Taxa de Atraso (%)",
    )
    fig.write_image(str(CHARTS_DIR / "atraso_por_estado.png"), scale=2)
    print("  [OK] atraso_por_estado.png")


def main():
    """Exporta todos os gráficos."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Carregando dados...")
    df = load_data()

    print(f"\nExportando gráficos para: {CHARTS_DIR}")
    export_revenue_monthly(df)
    export_top_states(df)
    export_top_categories(df)
    export_delay_impact(df)
    export_delay_by_state(df)

    print(f"\n{'='*50}")
    print(f"Exportação concluída! {len(list(CHARTS_DIR.glob('*.png')))} gráficos gerados.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
