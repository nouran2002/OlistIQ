import pandas as pd
import os


class OlistETLPipeline:
    def __init__(self, data_path="data", output_path="output"):
        self.data_path = data_path
        self.output_path = output_path

        os.makedirs(self.output_path, exist_ok=True)

        self.gold_file = os.path.join(self.output_path, "final_gold_table.parquet")

    # =========================
    # 1. LOAD DATA
    # =========================
    def load_data(self):

        base = self.data_path  # ✅ FIXED
    
        orders = pd.read_csv(os.path.join(base, "olist_orders_dataset.csv"))
        items = pd.read_csv(os.path.join(base, "olist_order_items_dataset.csv"))
        products = pd.read_csv(os.path.join(base, "olist_products_dataset.csv"))
    
        customers = pd.read_csv(os.path.join(base, "olist_customers_dataset.csv"))
        payments = pd.read_csv(os.path.join(base, "olist_order_payments_dataset.csv"))
        sellers = pd.read_csv(os.path.join(base, "olist_sellers_dataset.csv"))
        reviews = pd.read_csv(os.path.join(base, "olist_order_reviews_dataset.csv"))
        category = pd.read_csv(os.path.join(base, "product_category_name_translation.csv"))

        return orders, items, products, customers, payments, sellers, reviews, category
    # =========================
    # 2. CLEAN CORE TABLES
    # =========================
    def clean_orders_items_products(self, orders, items, products):

        orders["order_id"] = orders["order_id"].astype("string").str.strip()
        items["order_id"] = items["order_id"].astype("string").str.strip()
        items["product_id"] = items["product_id"].astype("string").str.strip()
        products["product_id"] = products["product_id"].astype("string").str.strip()

        orders_items = pd.merge(orders, items, on="order_id", how="inner")

        for col in ["price", "freight_value"]:
            if col in orders_items.columns:
                orders_items[col] = pd.to_numeric(orders_items[col], errors="coerce").abs()

        orders_items = orders_items.dropna(
            subset=["price", "order_approved_at", "order_delivered_customer_date"]
        )

        orders_items = orders_items[orders_items["price"] > 0]

        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "shipping_limit_date",
        ]

        for col in date_cols:
            if col in orders_items.columns:
                orders_items[col] = pd.to_datetime(orders_items[col],errors="coerce",infer_datetime_format=True)
        orders_items["total_item_price"] = (
            orders_items["price"] + orders_items["freight_value"]
        )

        master = pd.merge(orders_items, products, on="product_id", how="left")

        keep_cols = [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "order_item_id",
            "product_id",
            "seller_id",
            "price",
            "freight_value",
            "total_item_price",
            "product_category_name",
            "product_weight_g",
        ]

        master = master[keep_cols].dropna(
            subset=["product_category_name", "product_weight_g"]
        )

        return master

    # =========================
    # 3. ENRICH DATA
    # =========================
    def enrich(self, master, customers, payments, sellers, category):

        df = master.merge(customers, on="customer_id", how="left")
        df = df.merge(payments, on="order_id", how="left")
        df = df.merge(sellers, on="seller_id", how="left")
        df = df.merge(category, on="product_category_name", how="left")

        df["product_category_name_english"] = (
            df["product_category_name_english"]
            .fillna("other")
            .replace(
                {
                    "pc_gamer": "pc_gamer",
                    "portateis_cozinha_e_preparadores_de_alimentos": "kitchen_appliances",
                }
            )
        )

        df["payment_type"] = df["payment_type"].fillna("unknown").replace("not_defined", "unknown")
        df["payment_installments"] = df["payment_installments"].fillna(1).astype(int)

        return df

    # =========================
    # 4. AGGREGATION
    # =========================
    def aggregate(self, df):

        agg = df.groupby(
            ["order_id", "product_id", "payment_type", "product_category_name_english"]
        ).agg({
                
        "customer_id": "first",
        "customer_unique_id": "first",

        "order_status": "first",
        "seller_id": "first",

        "product_category_name": "first",

        "customer_city": "first",
        "customer_state": "first",
        "customer_zip_code_prefix": "first",

        "seller_city": "first",
        "seller_state": "first",
        "seller_zip_code_prefix": "first",

        "price": "sum",
        "freight_value": "sum",
        "total_item_price": "sum",
        "payment_value": "sum",

        "order_purchase_timestamp": "first",
        "order_approved_at": "first",
        "order_delivered_customer_date": "first",
        "order_estimated_delivery_date": "first",

        "product_weight_g": "first",

        "payment_installments": "max",

        "order_item_id": "max"

        }).reset_index()

        return agg

    # =========================
    # 5. REVIEWS
    # =========================
    def add_reviews(self, df, reviews):

        reviews_grouped = reviews.groupby("order_id", as_index=False)["review_score"].mean()

        final = df.merge(reviews_grouped, on="order_id", how="left")

        final["review_score"] = final["review_score"].fillna(0)

        return final

    # =========================
    # 6. BUILD PIPELINE
    # =========================
    def build(self, force=False):

        if os.path.exists(self.gold_file) and not force:
            return pd.read_parquet(self.gold_file)

        print("START")

        orders, items, products, customers, payments, sellers, reviews, category = self.load_data()
        print("LOADED")

        master = self.clean_orders_items_products(orders, items, products)
        print("CLEANED", master.shape)

        enriched = self.enrich(master, customers, payments, sellers, category)
        print("ENRICHED", enriched.shape)

        aggregated = self.aggregate(enriched)
        print("AGGREGATED", aggregated.shape)

        final = self.add_reviews(aggregated, reviews)
        print("REVIEWS DONE", final.shape)

        print("SAVING...")

        final.to_parquet(self.gold_file, index=False)
        

        
        return final
if __name__ == "__main__":
    pipeline = OlistETLPipeline()
    df = pipeline.build(force=True)
    print(df.info())
