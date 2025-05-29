import sql.numbersSql as numSql
import helpers

def profileNumbersWithinParentAcct(connection, acctSid):
  acctNumbersRaw = numSql.fetchNumbersWithinParentAcct(connection, acctSid)
  numbers = helpers.transformRowsAndColsToObjects(acctNumbersRaw)
  return numbers

def profileNumbersInAcct(connection, acctSid):
  acctNumbersRaw = numSql.fetchNumbersInAcct(connection, acctSid)
  numbers = helpers.transformRowsAndColsToObjects(acctNumbersRaw)
  return numbers

def profileShortcodesWithinParentAcct(connection, acctSid):
  acctShortcodesRaw = numSql.fetchShortcodesWithinParentAcct(connection, acctSid)
  shortcodes = helpers.transformRowsAndColsToObjects(acctShortcodesRaw)
  return shortcodes

def profileShortcodesInAcct(connection, acctSid):
  acctShortcodesRaw = numSql.fetchShortcodesInAcct(connection, acctSid)
  shortcodes = helpers.transformRowsAndColsToObjects(acctShortcodesRaw)
  return shortcodes