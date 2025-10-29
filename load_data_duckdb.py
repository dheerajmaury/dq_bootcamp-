import duckdb

# Create a DuckDB database file
con = duckdb.connect("dq_project.duckdb")

# Load CSVs as tables
con.execute("""
CREATE OR REPLACE TABLE customers AS 
SELECT * FROM read_csv_auto('customers.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE products AS 
SELECT * FROM read_csv_auto('products.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE orders AS 
SELECT * FROM read_csv_auto('orders.csv');
""")

print("✅ All CSVs loaded successfully into DuckDB!")
