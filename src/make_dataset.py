import pandas as pd
import numpy as np
from pathlib import Path

def main():
    # Caminhos dos diretórios
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data" / "raw"
    PROCESSED_DIR = BASE_DIR / "data" / "processed"
    
    # Criar pasta processed se não existir
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Carregando datasets...")
    # Carregar os CSVs
    try:
        orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
        items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
        payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
        reviews = pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv")
        customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
        sellers = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
        products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
        category_translation = pd.read_csv(RAW_DIR / "product_category_name_translation.csv")
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
        return
    
    print("Processando datas...")
    # Converter colunas de data da tabela de pedidos
    date_columns = [
        "order_purchase_timestamp", 
        "order_approved_at", 
        "order_delivered_carrier_date", 
        "order_delivered_customer_date", 
        "order_estimated_delivery_date"
    ]
    for col in date_columns:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")
        
    print("Agregando pagamentos e avaliações...")
    # Agregar pagamentos por order_id
    payments_agg = payments.groupby("order_id")["payment_value"].sum().reset_index()
    payments_agg.rename(columns={"payment_value": "total_payment_value"}, inplace=True)
    
    # Agregar avaliações por order_id (média em caso de múltiplas avaliações)
    reviews_agg = reviews.groupby("order_id")["review_score"].mean().reset_index()
    
    print("Juntando bases...")
    # Juntar pedidos e clientes
    df = orders.merge(customers, on="customer_id", how="left")
    
    # Adicionar itens (garantindo que cada linha será um item vendido)
    df = df.merge(items, on="order_id", how="inner")
    
    # Adicionar informações de produtos, vendedores, traduções, pagamentos e avaliações
    df = df.merge(products, on="product_id", how="left")
    df = df.merge(category_translation, on="product_category_name", how="left")
    df = df.merge(sellers, on="seller_id", how="left")
    # ATENÇÃO: total_payment_value está no nível do pedido e será repetido por item.
    # Para análises de receita, prefira item_revenue ou item_total_value.
    df = df.merge(payments_agg, on="order_id", how="left")
    df = df.merge(reviews_agg, on="order_id", how="left")
    
    print("Criando novas colunas...")
    # purchase_date, purchase_year, purchase_month, purchase_year_month
    df["purchase_date"] = df["order_purchase_timestamp"].dt.date
    df["purchase_year"] = df["order_purchase_timestamp"].dt.year
    df["purchase_month"] = df["order_purchase_timestamp"].dt.month
    df["purchase_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    
    # delivery_days (diferença em dias)
    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    
    # estimated_delivery_days
    df["estimated_delivery_days"] = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.days
    
    # delivery_delta_days: negativo = entregou antes, positivo = entregou depois
    df["delivery_delta_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days
    
    # delay_days: somente atraso positivo (entregas antecipadas viram 0)
    df["delay_days"] = df["delivery_delta_days"].apply(
        lambda x: max(0, x) if pd.notnull(x) else np.nan
    )
    
    # is_late: NaN para pedidos sem data de entrega (evita classificar cancelados como "no prazo")
    df["is_late"] = np.where(
        df["order_delivered_customer_date"].notna(),
        (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]).astype(int),
        np.nan,
    )
    
    # is_delivered
    df["is_delivered"] = (df["order_status"] == "delivered").astype(int)
    
    # item_revenue (valor do produto)
    df["item_revenue"] = df["price"]
    
    # item_total_value (produto + frete)
    df["item_total_value"] = df["price"] + df["freight_value"]
    
    output_path = PROCESSED_DIR / "commercepulse_orders_items.csv"
    print(f"Salvando dataset processado em: {output_path}")
    df.to_csv(output_path, index=False)
    
    print("-" * 30)
    print("Processamento concluído com sucesso!")
    print(f"Quantidade de linhas geradas: {df.shape[0]}")
    print(f"Quantidade de colunas geradas: {df.shape[1]}")
    print("-" * 30)

if __name__ == "__main__":
    main()