from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dashboard.utils import (  # noqa: E402
    compute_category_metrics,
    compute_kpis,
    compute_seller_metrics,
    compute_state_metrics,
    get_delivered_orders,
)
from src.make_rfm_dataset import build_rfm, frequency_score, percentile_score  # noqa: E402


def sample_items() -> pd.DataFrame:
    common = {
        "purchase_year_month": "2018-01",
        "product_category_name_english": "category_a",
        "seller_state": "SP",
        "seller_city": "sao paulo",
    }
    rows = [
        {
            **common,
            "order_id": "o1",
            "order_item_id": 1,
            "seller_id": "s1",
            "customer_state": "SP",
            "price": 10.0,
            "freight_value": 2.0,
            "item_revenue": 10.0,
            "item_total_value": 12.0,
            "review_score": 5.0,
            "delivery_days": 10.0,
            "delivery_delta_days": -2.0,
            "delay_days": 0.0,
            "is_late": 0.0,
            "is_delivered": 1,
        },
        {
            **common,
            "order_id": "o1",
            "order_item_id": 2,
            "seller_id": "s1",
            "customer_state": "SP",
            "price": 20.0,
            "freight_value": 3.0,
            "item_revenue": 20.0,
            "item_total_value": 23.0,
            "review_score": 5.0,
            "delivery_days": 10.0,
            "delivery_delta_days": -2.0,
            "delay_days": 0.0,
            "is_late": 0.0,
            "is_delivered": 1,
        },
        {
            **common,
            "order_id": "o2",
            "order_item_id": 1,
            "seller_id": "s2",
            "customer_state": "SP",
            "price": 30.0,
            "freight_value": 4.0,
            "item_revenue": 30.0,
            "item_total_value": 34.0,
            "review_score": 1.0,
            "delivery_days": 20.0,
            "delivery_delta_days": 5.0,
            "delay_days": 5.0,
            "is_late": 1.0,
            "is_delivered": 1,
        },
        {
            **common,
            "order_id": "o3",
            "order_item_id": 1,
            "seller_id": "s1",
            "customer_state": "RJ",
            "price": 40.0,
            "freight_value": 5.0,
            "item_revenue": 40.0,
            "item_total_value": 45.0,
            "review_score": np.nan,
            "delivery_days": np.nan,
            "delivery_delta_days": np.nan,
            "delay_days": np.nan,
            "is_late": np.nan,
            "is_delivered": 0,
        },
    ]
    return pd.DataFrame(rows)


def test_order_level_kpis_do_not_weight_multi_item_orders() -> None:
    kpis = compute_kpis(sample_items())

    assert kpis["total_orders"] == 3
    assert kpis["total_items"] == 4
    assert kpis["avg_review"] == 3.0
    assert kpis["delay_rate"] == 0.5
    assert kpis["avg_delivery_days"] == 15.0


def test_state_ticket_is_average_order_value() -> None:
    state = compute_state_metrics(sample_items()).set_index("customer_state")

    assert state.loc["SP", "avg_ticket"] == 30.0
    assert state.loc["SP", "avg_freight"] == 4.5
    assert state.loc["SP", "avg_review"] == 3.0


def test_category_quality_counts_each_order_once() -> None:
    category = compute_category_metrics(sample_items()).set_index(
        "product_category_name_english"
    )

    assert category.loc["category_a", "total_items"] == 4
    assert category.loc["category_a", "avg_review"] == 3.0
    assert category.loc["category_a", "delay_rate"] == 0.5


def test_seller_performance_uses_order_seller_granularity() -> None:
    sellers = compute_seller_metrics(sample_items()).set_index("seller_id")

    assert sellers.loc["s1", "total_items"] == 3
    assert sellers.loc["s1", "total_orders"] == 2
    assert sellers.loc["s1", "delivered_orders"] == 1
    assert sellers.loc["s1", "late_orders"] == 0
    assert sellers.loc["s2", "late_orders"] == 1


def test_delivered_orders_are_unique() -> None:
    delivered = get_delivered_orders(sample_items())

    assert delivered["order_id"].is_unique
    assert set(delivered["order_id"]) == {"o1", "o2"}


def test_rfm_scores_preserve_ties_and_real_frequency() -> None:
    values = pd.Series([10, 10, 100])
    scores = percentile_score(values)
    assert scores.iloc[0] == scores.iloc[1]

    frequencies = pd.Series([1, 1, 2, 3, 4, 5, 8])
    assert frequency_score(frequencies).tolist() == [1, 1, 2, 3, 4, 5, 5]


def test_build_rfm_never_promotes_single_purchase_by_tie_breaking() -> None:
    rows = []
    for customer, purchases in {"c1": 1, "c2": 1, "c3": 2, "c4": 5}.items():
        for index in range(purchases):
            rows.append(
                {
                    "customer_unique_id": customer,
                    "order_id": f"{customer}-{index}",
                    "order_status": "delivered",
                    "order_purchase_timestamp": pd.Timestamp("2018-01-01")
                    + pd.Timedelta(days=index),
                    "item_revenue": 10.0 + index,
                }
            )

    rfm = build_rfm(pd.DataFrame(rows)).set_index("customer_unique_id")
    assert (rfm.loc[["c1", "c2"], "F_score"] == 1).all()
    assert rfm.loc["c3", "F_score"] == 2
    assert rfm.loc["c4", "F_score"] == 5

