-- 02_mart_tests.sql
-- Day 3: Mart Layer Validation Tests

---------------------------------------------
-- 1. COMPLETENESS CHECKS
---------------------------------------------
-- Missing customer_id
SELECT COUNT(*) AS missing_customer_id
FROM orders_summary
WHERE customer_id IS NULL;

-- Missing country
SELECT COUNT(*) AS missing_country
FROM orders_summary
WHERE country IS NULL OR TRIM(country) = '';

-- Missing category
SELECT COUNT(*) AS missing_category
FROM orders_summary
WHERE category IS NULL OR TRIM(category) = '';

---------------------------------------------
-- 2. VALIDITY CHECKS
---------------------------------------------
-- Invalid quantity (null or <= 0)
SELECT COUNT(*) AS invalid_quantity
FROM orders_summary
WHERE quantity IS NULL OR quantity <= 0;

-- Invalid total_amount (null or <= 0)
SELECT COUNT(*) AS invalid_total_amount
FROM orders_summary
WHERE total_amount IS NULL OR total_amount <= 0;

-- Invalid price (null or <= 0)
SELECT COUNT(*) AS invalid_price
FROM orders_summary
WHERE price IS NULL OR price <= 0;

---------------------------------------------
-- 3. CONSISTENCY CHECKS
---------------------------------------------
-- total_amount ≈ quantity × price
SELECT COUNT(*) AS total_mismatch
FROM orders_summary
WHERE ABS(total_amount - (quantity * price)) > 0.01;

-- Missing product or customer links
SELECT COUNT(*) AS missing_links
FROM orders_summary
WHERE product_id IS NULL OR customer_id IS NULL;

---------------------------------------------
-- 4. UNIQUENESS CHECK
---------------------------------------------
-- Duplicate order_id
SELECT COUNT(*) AS duplicate_orders
FROM (
  SELECT order_id
  FROM orders_summary
  GROUP BY order_id
  HAVING COUNT(*) > 1
);

---------------------------------------------
-- 5. AGGREGATION / SANITY CHECKS
---------------------------------------------
-- Total revenue by country
SELECT country, SUM(total_amount) AS total_revenue
FROM orders_summary
GROUP BY country
ORDER BY total_revenue DESC;

-- Average price per category
SELECT category, AVG(price) AS avg_price
FROM orders_summary
GROUP BY category
ORDER BY avg_price DESC;
