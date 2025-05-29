import db

def fetchCalls(connection, fromDtStr, toDtStr, acctSid, daysPerbatch, callback):
  sql = f"""SELECT
  YEAR(call.start_time) AS year,
  DATE_FORMAT(call.start_time, '%m') AS month,
  acct.friendly_name AS acct_name,
  call.account_sid AS account_sid,
  CASE
    WHEN callvi.callee_country_code = 'US' THEN 'US'
    ELSE 'Intl'
  END as region,
  callvi.callee_info_carrier AS MNO,
  count(*) AS calls,
  sum(call.duration) as tot_dur,
  sum(vxn.quantity) as tot_price
  FROM rawpii_calls AS call
  LEFT JOIN rawpii_accounts AS acct
    ON call.account_sid = acct.sid
  LEFT JOIN redacted_voice_insights_call_summary_lite AS callvi
    ON call.sid = callvi.call_sid
  LEFT JOIN stored_value_transactions AS vxn
    ON call.sid = vxn.calculated_sid
  WHERE bitwise_and(call.flags,1) = 0
  AND call.start_time >= date '%fromDtStr%'
  AND call.start_time < date '%toDtStr%'
  AND call.data_load_date >= date '%fromDtStr%'
  AND call.data_load_date < date '%lagDtStr%'
  AND callvi.data_load_date >= date '%fromDtStr%'
  AND callvi.data_load_date < date '%lagDtStr%'
  AND vxn.data_load_date >= date '%fromDtStr%'
  AND vxn.data_load_date < date '%lagDtStr%'
  AND acct.sid IN (
    SELECT sid FROM rawpii_accounts
    WHERE sid = '{acctSid}'
    OR parent_account_sid = '{acctSid}'
  )
  GROUP BY 1, 2, 3, 4, 5, 6
  HAVING count(*) > 50
  ORDER BY 1, 2, 3, 4, 5, 6
  """

  db.fetchRowsByDateRange(connection, sql, fromDtStr, toDtStr, daysPerbatch, callback)
  return