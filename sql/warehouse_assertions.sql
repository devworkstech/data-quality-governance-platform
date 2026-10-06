-- Duplicate transaction IDs should return zero rows.
SELECT transaction_id, COUNT(*) AS row_count
FROM analytics.transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- Critical completeness and domain checks.
SELECT
  SUM(CASE WHEN tenant_id IS NULL THEN 1 ELSE 0 END) AS missing_tenant_ids,
  SUM(CASE WHEN amount <= 0 THEN 1 ELSE 0 END) AS invalid_amounts,
  SUM(CASE WHEN currency NOT IN ('USD','CAD','EUR','GBP') THEN 1 ELSE 0 END) AS unsupported_currencies
FROM analytics.transactions;

-- Freshness check; threshold should be adapted to the dataset SLA.
SELECT MAX(event_time) AS latest_event_time,
       CURRENT_TIMESTAMP AS checked_at
FROM analytics.transactions;
