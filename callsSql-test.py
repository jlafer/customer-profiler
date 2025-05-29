from dotenv import load_dotenv
from dotmap import DotMap
import os
import sys

import db
import sql.callsSql as callsSql

def makeCallsCallback(file):
  def callsCallback(items):
    if items.firstBatch:
      header = ', '.join(items.cols)
      file.write(f"{header}\n")
    for row in items.rows:
      print(f"""row = {row}""")
      line = ','.join(str(x) if x is not None else "" for x in row)
      file.write(f"{line}\n")
  return callsCallback

load_dotenv()
username = os.getenv("USERNAME")
print(username)
password = os.getenv("PASSWORD")

acct = DotMap()
acctSid = sys.argv[1]
fromDtStr = sys.argv[2]
toDtStr = sys.argv[3]
daysPerbatch = int( sys.argv[4] )
connection = db.connectToDb(username, password)
file = open("CallingSummary.txt", "w")
callbackFn = makeCallsCallback(file)
callsSql.fetchCalls(connection, fromDtStr, toDtStr, acctSid, daysPerbatch, callbackFn)

connection.close()
file.close()