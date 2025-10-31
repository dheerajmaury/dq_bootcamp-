-- 01_create_mart.sql (safe version)
CREATE OR REPLACE TABLE orders_summary AS
SELECT 
  o.order_id,
  o.customer_id,
  c.country,
  o.product_id,
  p.category,
  o.order_date,
  TRY_CAST(o.quantity AS DOUBLE)        AS quantity,
  TRY_CAST(o.total_amount AS DOUBLE)    AS total_amount,
  TRY_CAST(p.price AS DOUBLE)           AS price
FROM read_csv_auto('../orders.csv') o
LEFT JOIN read_csv_auto('../customers.csv') c
  ON o.customer_id = c.customer_id
LEFT JOIN read_csv_auto('../products.csv') p
  ON o.product_id = p.product_id;
