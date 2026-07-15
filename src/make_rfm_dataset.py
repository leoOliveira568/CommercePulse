"""
CommercePulse — Geração da Tabela de Segmentação RFM.

Calcula Recency, Frequency e Monetary para cada cliente único
da base processada e aplica segmentação em categorias de negócio.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def assign_rfm_segment(row: pd.Series) -> str:
    """Atribui um segmento de negócio com base nos scores RFM (1-5)."""
    r, f, m = row["R_score"], row["F_score"], row["M_score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2 and m <= 2:
        return "New Customers"
    elif r >= 3 and f >= 1 and m >= 2:
        return "Potential Loyalists"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 2 and f >= 1 and m >= 1:
        return "Hibernating"
    else:
        return "Others"


def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """Converte uma métrica contínua em score de 1 a 5 preservando empates."""
    percentile = series.rank(method="average", pct=True)
    score = np.ceil(percentile * 5).clip(1, 5).astype(int)
    return score if higher_is_better else 6 - score


def frequency_score(series: pd.Series) -> pd.Series:
    """Pontua frequência sem separar artificialmente clientes empatados.

    A base Olist é muito concentrada em uma única compra. Faixas de negócio
    mantêm todos os clientes com a mesma frequência no mesmo score.
    """
    return pd.Series(
        np.select(
            [series <= 1, series == 2, series == 3, series == 4],
            [1, 2, 3, 4],
            default=5,
        ),
        index=series.index,
        dtype="int64",
    )


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a tabela RFM a partir da base processada de itens."""
    df = df.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )

    df_delivered = df[df["order_status"] == "delivered"].copy()
    if df_delivered.empty:
        raise ValueError("A base não contém pedidos entregues para calcular RFM.")

    reference_date = df_delivered["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    order_revenue = df_delivered.groupby(["customer_unique_id", "order_id"]).agg(
        order_revenue=("item_revenue", "sum"),
        order_date=("order_purchase_timestamp", "first"),
    ).reset_index()

    rfm = order_revenue.groupby("customer_unique_id").agg(
        recency=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("order_revenue", "sum"),
    ).reset_index()

    rfm["R_score"] = percentile_score(rfm["recency"], higher_is_better=False)
    rfm["F_score"] = frequency_score(rfm["frequency"])
    rfm["M_score"] = percentile_score(rfm["monetary"])
    rfm["RFM_score"] = rfm[["R_score", "F_score", "M_score"]].sum(axis=1)
    rfm["segment"] = rfm.apply(assign_rfm_segment, axis=1)
    return rfm


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    PROCESSED_DIR = BASE_DIR / "data" / "processed"

    input_path = PROCESSED_DIR / "commercepulse_orders_items.csv"
    output_path = PROCESSED_DIR / "commercepulse_rfm.csv"

    print("Carregando base processada...")
    df = pd.read_csv(input_path)
    print("Calculando métricas e segmentos RFM...")
    rfm = build_rfm(df)

    # --- Salvar ---
    rfm.to_csv(output_path, index=False)

    print("-" * 40)
    print(f"Tabela RFM salva em: {output_path}")
    print(f"Total de clientes segmentados: {len(rfm):,}")
    print()
    print("Distribuição por segmento:")
    print(rfm["segment"].value_counts().to_string())
    print("-" * 40)


if __name__ == "__main__":
    main()
