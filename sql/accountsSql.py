import db

def fetchAccount(connection, acctSid):
  acct = db.fetchOneRow(connection, f"""
  SELECT
    acct.sid AS account_sid,
    acct.friendly_name,
    acct.status,
    acct.date_created,
    acct.fraud_score
  FROM public.rawpii_accounts AS acct
  WHERE acct.sid = '{acctSid}'
  """)
  return acct

def countSubAccts(connection, acctSid):
  count = db.fetchCount(connection, f"""
  SELECT
    COUNT(*)
  FROM public.rawpii_accounts AS acct
  WHERE acct.parent_account_sid = '{acctSid}'
  AND acct.status = 'ACTIVE'
  """)
  return count

def fetchSubAccts(connection, acctSid):
  subAccts = db.fetchRows(connection, f"""
  SELECT
    acct.sid AS account_sid,
    acct.friendly_name,
    acct.status,
    acct.date_created,
    acct.fraud_score
  FROM public.rawpii_accounts AS acct
  WHERE acct.parent_account_sid = '{acctSid}'
  AND acct.status = 'ACTIVE'
  LIMIT 500
  """)
  return subAccts

def fetchSpendByProduct(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    bim.product_group_2 AS product_grp2,
    bim.product_group_1 AS product_grp1,
    SUM(ctr.num_events) AS events,
    SUM(ctr.quantity) AS quantity,
    SUM(CASE WHEN ctr.units = 'USD' THEN ctr.total ELSE ctr.total *  xrates.rate END) AS dollars
  FROM counters_by_billable_item_complete AS ctr
  LEFT JOIN billable_item_metadata_alex AS bim
    ON ctr.billable_item_sid = bim.sid
  LEFT JOIN currency_exchange_rates AS xrates
    ON ctr.units = xrates.from_curr
    AND (DATE_FORMAT(ctr.date , '%Y-%m-%d')) =
        (DATE_FORMAT(xrates.date , '%Y-%m-%d'))
    AND xrates.to_curr = 'USD'
  WHERE ctr.data_load_date >= date '{dates.start_date}'
  AND ctr.data_load_date < date '{dates.end_date_long_lag}'
  AND ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.subtype = 'revenue-sale'
  AND ctr.account_sid = '{acctSid}'
  GROUP BY 1, 2
  ORDER BY 5 DESC
  """)
  return rows

def fetchHighSpendSubAccts(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    acct.sid AS account_sid,
    acct.friendly_name AS account_name,
    acct.date_created,
    acct.fraud_score,
    SUM(ctr.total) AS total
  FROM public.counters_by_subaccount as ctr
  LEFT JOIN rawpii_accounts AS acct ON acct.sid = ctr.subaccount_sid
  WHERE ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.units = 'USD'
  AND acct.parent_account_sid = '{acctSid}'
  AND acct.status = 'ACTIVE'
  GROUP BY 1, 2, 3, 4
  HAVING SUM(ctr.total) > 100
  ORDER BY 5 DESC
  LIMIT 10
  """)
  return rows

def fetchSubAcctSpendByProduct(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    bim.product_group_2 AS product_grp2,
    bim.product_group_1 AS product_grp1,
    SUM(CASE WHEN ctr.units = 'USD' THEN ctr.total ELSE ctr.total *  xrates.rate END) AS dollars
  FROM public.counters_by_subaccount as ctr
  LEFT JOIN rawpii_accounts AS acct ON acct.sid = ctr.subaccount_sid
  LEFT JOIN billable_item_metadata_alex AS bim
    ON bim.sid = ctr.billable_item_sid
  LEFT JOIN currency_exchange_rates AS xrates
    ON ctr.units = xrates.from_curr
    AND (DATE_FORMAT(ctr.date , '%Y-%m-%d')) =
        (DATE_FORMAT(xrates.date , '%Y-%m-%d'))
    AND xrates.to_curr = 'USD'
  WHERE ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.units = 'USD'
  AND acct.sid = '{acctSid}'
  GROUP BY 1, 2
  HAVING SUM(ctr.total) > 30
  ORDER BY 3 DESC
  """)
  return rows

def fetchSpendByCountry(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    bim.country,
    SUM(CASE WHEN ctr.units = 'USD' THEN ctr.total ELSE ctr.total *  xrates.rate END) AS dollars
  FROM counters_by_billable_item_complete AS ctr
  LEFT JOIN billable_item_metadata_alex AS bim
    ON ctr.billable_item_sid = bim.sid
  LEFT JOIN currency_exchange_rates AS xrates
    ON ctr.units = xrates.from_curr
    AND (DATE_FORMAT(ctr.date , '%Y-%m-%d')) =
        (DATE_FORMAT(xrates.date , '%Y-%m-%d'))
    AND xrates.to_curr = 'USD'
  WHERE ctr.data_load_date >= date '{dates.start_date}'
  AND ctr.data_load_date < date '{dates.end_date_long_lag}'
  AND ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.subtype = 'revenue-sale'
  AND ctr.account_sid = '{acctSid}'
  GROUP BY 1
  HAVING SUM(ctr.total) > 30
  ORDER BY 2 DESC
  """)
  return rows

def fetchSubAcctSpendByCountry(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    bim.country,
    SUM(CASE WHEN ctr.units = 'USD' THEN ctr.total ELSE ctr.total *  xrates.rate END) AS dollars
  FROM public.counters_by_subaccount as ctr
  LEFT JOIN rawpii_accounts AS acct ON acct.sid = ctr.subaccount_sid
  LEFT JOIN billable_item_metadata_alex AS bim
    ON bim.sid = ctr.billable_item_sid
  LEFT JOIN currency_exchange_rates AS xrates
    ON ctr.units = xrates.from_curr
    AND (DATE_FORMAT(ctr.date , '%Y-%m-%d')) =
        (DATE_FORMAT(xrates.date , '%Y-%m-%d'))
    AND xrates.to_curr = 'USD'
  WHERE ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.units = 'USD'
  AND acct.sid = '{acctSid}'
  GROUP BY 1
  HAVING SUM(ctr.total) > 30
  ORDER BY 2 DESC
  """)
  return rows

def fetchSpendBySubAcct(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    acct.sid AS account_sid,
    acct.friendly_name AS account_name,
    SUM(ctr.total) AS total
  FROM public.counters_by_subaccount as ctr
  LEFT JOIN rawpii_accounts AS acct ON acct.sid = ctr.subaccount_sid
  LEFT JOIN billable_item_metadata_alex AS bim
    ON bim.sid = ctr.billable_item_sid
  WHERE ctr.date >= date '{dates.start_date}'
  AND ctr.date < date '{dates.end_date_long}'
  AND ctr.units = 'USD'
  AND acct.sid IN (
    SELECT sid FROM rawpii_accounts
    WHERE sid = '{acctSid}'
    OR parent_account_sid = '{acctSid}'
  )
  GROUP BY 1, 2
  HAVING SUM(ctr.total) > 100
  ORDER BY 3 DESC
  LIMIT 10
  """)
  return rows

