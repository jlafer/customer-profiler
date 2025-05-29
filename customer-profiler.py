from dotenv import load_dotenv
from dotmap import DotMap
import os
import sys

import db
import helpers
import sql.accountsSql as acctSql
import accounts

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

acctSid = sys.argv[1]
folderPath = sys.argv[2]

acct = DotMap()

connection = db.connectToDb(username, password)
dates = helpers.makeDatesFromToday('month', 'week', 2)
print("reporting period:", dates)
file = open(f"{folderPath}/account.json", "w")
acct = acctSql.fetchAccount(connection, acctSid)
print(f"processing account: {acct.friendly_name}")
accounts.profileParentAccount(connection, acct, dates)
if acct.cntSubAccts > 0:
  acct.highSpendSubAccts = accounts.fetchHighSpendSubAccts(connection, acctSid, dates)
else:
  acct.highSpendSubAccts = []
if len(acct.highSpendSubAccts) > 0:
  accounts.profileSubAccts(connection, acct, dates)
accounts.writeAccount(file, acct)
file.close()

connection.close()