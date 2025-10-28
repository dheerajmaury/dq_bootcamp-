import pandas as pd
import numpy as np
from datetime import datetime

# ---------- LOAD DATA ----------
customers = pd.read_csv("customers.csv")
orders = pd.read_csv("orders.csv")
products = pd.read_csv("products.csv")

dq_issues = []

def add_issue(row_num, file, column, issue, dimension, example):
    dq_issues.append({
        "row_num": row_num,
        "file": file,
        "column": column,
        "issue": issue,
        "dimension": dimension,
        "example": example
    })

# ==============================================================
# 1️⃣ COMPLETENESS
# ==============================================================
for i, row in customers[customers["email"].isna() | (customers["email"] == "")].iterrows():
    add_issue(i, "customers.csv", "email", "Missing email", "Completeness", "")

for i, row in customers[customers["phone"].isna() | (customers["phone"] == "")].iterrows():
    add_issue(i, "customers.csv", "phone", "Missing phone", "Completeness", "")

for i, row in products[products["product_name"].isna() | (products["product_name"] == "")].iterrows():
    add_issue(i, "products.csv", "product_name", "Missing product name", "Completeness", "")

for i, row in orders[orders["total_amount"].isna() | orders["quantity"].isna()].iterrows():
    add_issue(i, "orders.csv", "total_amount/quantity", "Missing total or quantity", "Completeness", "")

# ==============================================================
# 2️⃣ VALIDITY
# ==============================================================
# Invalid email format
invalid_email = customers[~customers["email"].astype(str).str.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", na=False)]
for i, row in invalid_email.iterrows():
    add_issue(i, "customers.csv", "email", "Invalid email format", "Validity", row["email"])

# Invalid phone numbers (not 10 digits)
invalid_phone = customers[~customers["phone"].astype(str).str.match(r"^\d{10}$", na=False)]
for i, row in invalid_phone.iterrows():
    add_issue(i, "customers.csv", "phone", "Invalid phone number", "Validity", row["phone"])

# Invalid or negative price
invalid_price = products[
    ~pd.to_numeric(products["price"], errors="coerce").notna() |
    (pd.to_numeric(products["price"], errors="coerce") < 0)
]
for i, row in invalid_price.iterrows():
    add_issue(i, "products.csv", "price", "Invalid or negative price", "Validity", row["price"])

# Invalid total_amount (non-numeric or negative)
invalid_total = orders[
    ~pd.to_numeric(orders["total_amount"], errors="coerce").notna() |
    (pd.to_numeric(orders["total_amount"], errors="coerce") < 0)
]
for i, row in invalid_total.iterrows():
    add_issue(i, "orders.csv", "total_amount", "Invalid or negative total_amount", "Validity", row["total_amount"])

# ==============================================================
# 3️⃣ UNIQUENESS
# ==============================================================
dup_sku = products[products["sku"].duplicated(keep=False)]
for i, row in dup_sku.iterrows():
    add_issue(i, "products.csv", "sku", "Duplicate SKU", "Uniqueness", row["sku"])

dup_orders = orders[orders["order_id"].duplicated(keep=False)]
for i, row in dup_orders.iterrows():
    add_issue(i, "orders.csv", "order_id", "Duplicate order_id", "Uniqueness", row["order_id"])

dup_customers = customers[customers["email"].duplicated(keep=False)]
for i, row in dup_customers.iterrows():
    add_issue(i, "customers.csv", "email", "Duplicate email", "Uniqueness", row["email"])

# ==============================================================
# 4️⃣ TIMELINESS
# ==============================================================
orders["order_date_parsed"] = pd.to_datetime(orders["order_date"], errors="coerce")
future_orders = orders[orders["order_date_parsed"] > datetime.now()]
for i, row in future_orders.iterrows():
    add_issue(i, "orders.csv", "order_date", "Future order date", "Timeliness", row["order_date"])

# ==============================================================
# 5️⃣ CONSISTENCY
# ==============================================================
invalid_customer_orders = orders[~orders["customer_id"].isin(customers["customer_id"])]
for i, row in invalid_customer_orders.iterrows():
    add_issue(i, "orders.csv", "customer_id", "Orphan order (customer_id not found)", "Consistency", row["customer_id"])

invalid_product_orders = orders[~orders["product_id"].isin(products["product_id"])]
for i, row in invalid_product_orders.iterrows():
    add_issue(i, "orders.csv", "product_id", "Orphan order (product_id not found)", "Consistency", row["product_id"])

valid_categories = ["Electronics", "Apparel", "Accessories"]
invalid_category = products[~products["category"].isin(valid_categories)]
for i, row in invalid_category.iterrows():
    add_issue(i, "products.csv", "category", "Invalid category value", "Consistency", row["category"])

# ==============================================================
# 6️⃣ ACCURACY
# ==============================================================

orders["quantity_num"] = pd.to_numeric(orders["quantity"], errors="coerce")
orders["total_num"] = pd.to_numeric(orders["total_amount"], errors="coerce")

for i, row in orders.iterrows():
    if pd.notna(row["quantity_num"]) and pd.notna(row["total_num"]):
        product_price = products.loc[products["product_id"] == row["product_id"], "price"]
        if not product_price.empty:
            try:
                p = float(product_price.values[0])
                expected_total = row["quantity_num"] * p
                if abs(row["total_num"] - expected_total) > 0.01:
                    add_issue(i, "orders.csv", "total_amount", "Mismatch with quantity×price", "Accuracy", f"{row['total_amount']} vs {expected_total}")
            except:
                pass

# ==============================================================
# 7️⃣ DATA TYPE CHECKS (NEW - to generate 20+ issues)
# ==============================================================
# Customers
for i, row in customers.iterrows():
    if not isinstance(row["customer_id"], (int, np.integer)):
        add_issue(i, "customers.csv", "customer_id", "Wrong data type (should be int)", "Data Type", row["customer_id"])
    if not isinstance(row["email"], str):
        add_issue(i, "customers.csv", "email", "Wrong data type (should be str)", "Data Type", row["email"])
    if not isinstance(row["phone"], (str, int)):
        add_issue(i, "customers.csv", "phone", "Wrong data type (should be str)", "Data Type", row["phone"])

# Products
for i, row in products.iterrows():
    if not isinstance(row["product_id"], (int, np.integer)):
        add_issue(i, "products.csv", "product_id", "Wrong data type (should be int)", "Data Type", row["product_id"])
    if not isinstance(row["price"], (int, float, np.number)):
        add_issue(i, "products.csv", "price", "Wrong data type (should be numeric)", "Data Type", row["price"])
    if not isinstance(row["category"], str):
        add_issue(i, "products.csv", "category", "Wrong data type (should be str)", "Data Type", row["category"])

# Orders
for i, row in orders.iterrows():
    if not isinstance(row["order_id"], (int, np.integer)):
        add_issue(i, "orders.csv", "order_id", "Wrong data type (should be int)", "Data Type", row["order_id"])
    if not isinstance(row["customer_id"], (int, np.integer)):
        add_issue(i, "orders.csv", "customer_id", "Wrong data type (should be int)", "Data Type", row["customer_id"])
    if not isinstance(row["product_id"], (int, np.integer)):
        add_issue(i, "orders.csv", "product_id", "Wrong data type (should be int)", "Data Type", row["product_id"])
    if not isinstance(row["quantity"], (int, float, np.number)):
        add_issue(i, "orders.csv", "quantity", "Wrong data type (should be numeric)", "Data Type", row["quantity"])
    if not isinstance(row["total_amount"], (int, float, np.number)):
        add_issue(i, "orders.csv", "total_amount", "Wrong data type (should be numeric)", "Data Type", row["total_amount"])
    if not isinstance(row["order_date_parsed"], pd.Timestamp):
        add_issue(i, "orders.csv", "order_date", "Wrong data type (should be datetime)", "Data Type", row["order_date"])

# ==============================================================
# EXPORT RESULTS
# ==============================================================
dq_df = pd.DataFrame(dq_issues)
dq_df.to_csv("dq_issues_day1.csv", index=False)
dq_df.to_excel("dq_issues_day1.xlsx", index=False)

print(f"✅ Data Quality Report generated: dq_issues_day1.csv & dq_issues_day1.xlsx ({len(dq_df)} issues found!)")
