# generate_data.py
import csv
import random
import string
import datetime
from faker import Faker
fake = Faker()

# ------------------------------
# Config
# ------------------------------
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 100
NUM_ORDERS = 1000

# Error injection ratios
ERROR_RATE_NULL = 0.1           # % null fields
ERROR_RATE_DUPLICATE = 0.05     # % duplicate rows
ERROR_RATE_INVALID = 0.1        # % invalid formats
ERROR_RATE_FUTURE_DATES = 0.05  # % future dates

def random_phone():
    return ''.join(random.choices(string.digits, k=10))

def random_email(name):
    if random.random() < ERROR_RATE_INVALID:
        # deliberately invalid domain
        return f"{name.lower()}@invalid"
    return f"{name.lower()}@{fake.free_email_domain()}"

def maybe_null(value):
    return "" if random.random() < ERROR_RATE_NULL else value

def maybe_future_date(date):
    if random.random() < ERROR_RATE_FUTURE_DATES:
        return date + datetime.timedelta(days=random.randint(30, 365))
    return date

# ------------------------------
# Customers
# ------------------------------
customers = []
for cid in range(1, NUM_CUSTOMERS + 1):
    name = fake.first_name()
    created_at = fake.date_between(start_date="-2y", end_date="today")
    customers.append({
        "customer_id": cid,
        "first_name": name,
        "last_name": fake.last_name(),
        "email": maybe_null(random_email(name)),
        "phone": maybe_null(random_phone()),
        "country": random.choice(["US", "IN", "MX", "UK", "CN", "DE"]),
        "created_at": created_at.isoformat()
    })

# inject duplicates
dup_count = int(NUM_CUSTOMERS * ERROR_RATE_DUPLICATE)
if dup_count:
    customers += random.choices(customers, k=dup_count)

with open("customers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(customers[0].keys()))
    writer.writeheader()
    writer.writerows(customers)

# ------------------------------
# Products
# ------------------------------
products = []
for pid in range(101, 101 + NUM_PRODUCTS):
    pname = fake.word().capitalize()
    price = random.randint(10, 2000)
    if random.random() < ERROR_RATE_INVALID:
        price = random.choice(["abc", -50, None])
    products.append({
        "product_id": pid,
        "sku": f"P{pid}",
        "product_name": maybe_null(pname),
        "category": random.choice(["Electronics", "Apparel", "Accessories"]),
        "price": price
    })

# inject duplicates
dup_count = int(NUM_PRODUCTS * ERROR_RATE_DUPLICATE)
if dup_count:
    products += random.choices(products, k=dup_count)

# ensure price field serialized (strings allowed)
with open("products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(products[0].keys()))
    writer.writeheader()
    writer.writerows(products)

# ------------------------------
# Orders
# ------------------------------
orders = []
for oid in range(5001, 5001 + NUM_ORDERS):
    cust = random.choice(customers)
    prod = random.choice(products)
    order_date = fake.date_between(start_date="-1y", end_date="today")
    order_date = maybe_future_date(order_date)
    qty = random.randint(1, 5)
    # try to derive price from product; handle bad prices
    try:
        price_val = int(prod["price"]) if isinstance(prod["price"], int) or (isinstance(prod["price"], str) and prod["price"].isdigit()) else int(prod["price"])
    except Exception:
        price_val = random.randint(10, 500)
    total = qty * price_val
    if random.random() < ERROR_RATE_INVALID:
        total = random.choice(["abc", -100, qty * 100])  # sometimes wrong
    # sometimes orphan customer id to generate orphan rows
    if random.random() < ERROR_RATE_INVALID:
        customer_id = 999999
    else:
        customer_id = cust["customer_id"]

    orders.append({
        "order_id": oid,
        "customer_id": customer_id,
        "product_id": prod["product_id"],
        "order_date": order_date.isoformat(),
        "quantity": qty,
        "total_amount": total
    })

with open("orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
    writer.writeheader()
    writer.writerows(orders)

print("Generated customers.csv, products.csv, orders.csv with DQ issues")
