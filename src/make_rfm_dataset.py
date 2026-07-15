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


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    PROCESSED_DIR = BASE_DIR / "data" / "processed"

    input_path = PROCESSED_DIR / "commercepulse_orders_items.csv"
    output_path = PROCESSED_DIR / "commercepulse_rfm.csv"

    print("Carregando base processada...")
    df = pd.read_csv(input_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")

    # Apenas pedidos entregues
    df_delivered = df[df["order_status"] == "delivered"].copy()

    # Data de referência: dia seguinte à última compra
    reference_date = df_delivered["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    print(f"Data de referência para Recency: {reference_date.date()}")

    # --- Calcular métricas RFM por cliente ---
    print("Calculando métricas RFM...")

    # Receita total por pedido (evita duplicação por item)
    order_revenue = df_delivered.groupby(["customer_unique_id", "order_id"]).agg(
        order_revenue=("item_revenue", "sum"),
        order_date=("order_purchase_timestamp", "first"),
    ).reset_index()

    rfm = order_revenue.groupby("customer_unique_id").agg(
        recency=("order_date", lambda x: (reference_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("order_revenue", "sum"),
    ).reset_index()

    # --- Scores RFM (1-5, usando quintis) ---
    print("Atribuindo scores RFM...")

    # Recency: menor = melhor (score 5)
    rfm["R_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)

    # Frequency: a maioria tem 1 compra, então usamos rank para evitar bins degenerados
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    # Monetary: maior = melhor (score 5)
    rfm["M_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    # Score combinado
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    # --- Segmentação ---
    print("Aplicando segmentação de clientes...")
    rfm["segment"] = rfm.apply(assign_rfm_segment, axis=1)

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
