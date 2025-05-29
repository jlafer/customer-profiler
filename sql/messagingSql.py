import db

def countMsgServicesWithinParentAcct(connection, acctSid):
  count = db.fetchCount(connection, f"""
  SELECT
    count(*) AS count
  FROM messaging_services AS msvc
  WHERE status = 'active'
  AND msvc.account_sid IN (
    SELECT sid FROM rawpii_accounts
    WHERE sid = '{acctSid}'
    OR parent_account_sid='{acctSid}'
  )
  """)
  return count

def countMsgServicesInAcct(connection, acctSid):
  count = db.fetchCount(connection, f"""
  SELECT
    count(*) AS count
  FROM messaging_services AS msvc
  WHERE status = 'active'
  AND msvc.account_sid = '{acctSid}'
  """)
  return count

def fetchMsgSendsInAcct(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    msg.messaging_app_sid AS messaging_service,
    msg.caller AS sender,
    count(*) AS count
  FROM rawpii_sms_kafka AS msg
  WHERE msg.account_sid = '{acctSid}'
  AND msg.date_created >= date '{dates.start_date}'
  AND msg.date_created < date '{dates.end_date_short}'
  AND msg.data_load_date >= date '{dates.start_date}'
  AND msg.data_load_date < date '{dates.end_date_short_lag}'
  AND bitwise_and(msg.flags, 1) = 0
  GROUP BY 1, 2
  HAVING count(*) > 1000
  ORDER BY 3 DESC
  LIMIT 20
""")
  return rows

def countOptOutsInAcct(connection, acctSid, dates):
  rows = db.fetchRows(connection, f"""
  SELECT
    CASE
      WHEN bl.twilio_number LIKE 'MG%' THEN 'messaging service'
      ELSE 'phone number'
    END AS record_type,
    bl.twilio_number AS sender,
    COUNT(*) AS count
  FROM sms_internal_blacklist AS bl
  LEFT JOIN rawpii_accounts AS acct ON bl.account_sid = acct.sid
  WHERE bl.allowed = 0
  AND bl.date_updated >= date '{dates.start_date}'
  AND bl.date_updated < date '{dates.end_date_short}'
  AND bl.account_sid = '{acctSid}'
  GROUP BY 1, 2
  LIMIT 200
  """)
  return rows
