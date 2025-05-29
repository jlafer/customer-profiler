import db

def fetchNumbersWithinParentAcct(connection, acctSid):
  rows = db.fetchRows(connection, f"""
  SELECT
    CASE
    WHEN pn.type = 1  THEN 'domestic'
    WHEN pn.type = 2  THEN 'international'
    WHEN pn.type = 3  THEN 'premium'
    WHEN pn.type = 4  THEN 'unknown'
    WHEN pn.type = 5  THEN 'tollfree'
    WHEN pn.type = 6  THEN 'domestic_invalid'
    WHEN pn.type = 7  THEN 'shortcode'
    WHEN pn.type = 8  THEN 'twilio_client'
    WHEN pn.type = 9  THEN 'sip'
    WHEN pn.type = 10  THEN 'mobile'
    WHEN pn.type = 11  THEN 'national'
    ELSE 'unknown'
    END AS type_name,
    count(1) AS cnt
  FROM rawpii_phone_numbers AS pn
  WHERE pn.active = 1
  AND pn.account_sid IN (
    SELECT sid FROM rawpii_accounts
    WHERE sid = '{acctSid}'
    OR parent_account_sid = '{acctSid}'
  )
  GROUP BY 1
  ORDER BY 1
  """)
  return rows

def fetchNumbersInAcct(connection, acctSid):
  rows = db.fetchRows(connection, f"""
  SELECT
    CASE
    WHEN pn.type = 1  THEN 'domestic'
    WHEN pn.type = 2  THEN 'international'
    WHEN pn.type = 3  THEN 'premium'
    WHEN pn.type = 4  THEN 'unknown'
    WHEN pn.type = 5  THEN 'tollfree'
    WHEN pn.type = 6  THEN 'domestic_invalid'
    WHEN pn.type = 7  THEN 'shortcode'
    WHEN pn.type = 8  THEN 'twilio_client'
    WHEN pn.type = 9  THEN 'sip'
    WHEN pn.type = 10  THEN 'mobile'
    WHEN pn.type = 11  THEN 'national'
    ELSE 'unknown'
    END AS type_name,
    count(1) AS cnt
  FROM rawpii_phone_numbers AS pn
  LEFT JOIN rawpii_accounts AS acct ON acct.sid = pn.account_sid
  WHERE pn.active = 1
  AND pn.account_sid  = '{acctSid}'
  GROUP BY 1
  ORDER BY 1
  """)
  return rows

def fetchShortcodesWithinParentAcct(connection, acctSid):
  rows = db.fetchRows(connection, f"""
  SELECT
    sc.friendly_name AS name,
    providers.friendly_name AS provider,
    sc.short_code_region AS region
  FROM public.short_codes AS sc
  LEFT JOIN providers AS providers ON sc.provider_sid = providers.sid
  WHERE sc.active = 1
  AND sc.account_sid IN (
    SELECT sid FROM rawpii_accounts
    WHERE sid = '{acctSid}'
    OR parent_account_sid = '{acctSid}'
  )
  """)
  return rows

def fetchShortcodesInAcct(connection, acctSid):
  rows = db.fetchRows(connection, f"""
  SELECT
    sc.friendly_name AS name,
    providers.friendly_name AS provider,
    sc.short_code_region AS region
  FROM public.short_codes AS sc
  LEFT JOIN providers AS providers ON sc.provider_sid = providers.sid
  WHERE sc.active = 1
  AND sc.account_sid = '{acctSid}'
  """)
  return rows

