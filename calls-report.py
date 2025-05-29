from dotenv import load_dotenv
from dotmap import DotMap
from datetime import datetime
import os
import sys

import db
import sql.callsSql as sql

report = DotMap()

def callsCallback(items):
  if items.firstBatch:
    report.cols = items.cols
  for row in items.rows:
    keyParts = row[0:6]
    key = ','.join(str(x) if x is not None else "" for x in keyParts)
    values = [int(row[6]), int(row[7]), int(float(row[8]))]
    if key not in report.rows:
      report.rows[key] = values
    else:
      report.rows[key][0] += values[0]
      report.rows[key][1] += values[1]
      report.rows[key][2] += values[2]
  return

def writeReport(data):
  hdr = ','.join(data.cols)
  file.write(f"{hdr}\n")
  for key, values in data.rows.items():
    valueStr = ','.join(map(str, values))
    line = f"{key},{valueStr}"
    file.write(f"{line}\n")

load_dotenv()
username = os.getenv("USERNAME")
print(username)
password = os.getenv("PASSWORD")

acct = DotMap()
acctSid = sys.argv[1]
fromDtStr = sys.argv[2]
fromDt = datetime.strptime(fromDtStr, "%Y-%m-%d")
print(fromDt)
toDtStr = sys.argv[3]
toDt = datetime.strptime(toDtStr, "%Y-%m-%d")
daysPerbatch = int( sys.argv[4] )
fileName = sys.argv[5]
connection = db.connectToDb(username, password)
file = open(fileName, "a")
sql.fetchCalls(connection, fromDtStr, toDtStr, acctSid, daysPerbatch, callsCallback)
writeReport(report)
connection.close()
file.close()
