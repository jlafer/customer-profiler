from datetime import datetime
from datetime import timedelta
from dotmap import DotMap
import prestodb

def connectToDb(username, password):
  connection = prestodb.dbapi.connect(
    host='odin.prod.twilio.com',
    port=8443,
    http_scheme='https',
    catalog='hive',
    user=username,
    auth=prestodb.auth.BasicAuthentication(username, password),
    http_headers={'X-Presto-Extra-Credential': 'routing=default0'}
  )
  return connection

def fetchCount(connection, query):
  cursor = connection.cursor()
  cursor.execute(query)
  count = cursor.fetchone()[0]
  cursor.close()
  return count

def fetchRows(connection, query):
  cursor = connection.cursor()
  cursor.execute(query)
  columns = [desc[0] for desc in cursor.description]
  rows = cursor.fetchall()
  cursor.close()
  return DotMap({'cols': columns, 'rows': rows})

def fetchRowsByDateRange(connection, query, fromDtStr, toDtStr, daysPerbatch, callback):
  fromDt = datetime.strptime(fromDtStr, "%Y-%m-%d")
  toDt = datetime.strptime(toDtStr, "%Y-%m-%d")
  batchStartDt = fromDt
  firstBatch = True
  while batchStartDt < toDt:
    batchEndDt = min( toDt, batchStartDt + timedelta(days=daysPerbatch) )
    batchLagDt = batchEndDt + timedelta(days=2)
    print(f"batch = {batchStartDt} to {batchEndDt}")
    batchStartDtStr = batchStartDt.strftime("%Y-%m-%d")
    batchEndDtStr = batchEndDt.strftime("%Y-%m-%d")
    batchLagDtStr = batchLagDt.strftime("%Y-%m-%d")
    sql = substituteDatesInQuery(query, batchStartDtStr, batchEndDtStr, batchLagDtStr)
    #print(f"""sql = {sql}""")
    rcds = fetchRows(connection, sql)
    if firstBatch:
      rcds.firstBatch = True
      firstBatch = False
    #print(f"""rcds = {rcds}""")
    callback(rcds)
    batchStartDt = batchEndDt

def substituteDatesInQuery(query, fromDtStr, toDtStr, batchLagDtStr):
  return query.replace('%fromDtStr%', fromDtStr).replace('%toDtStr%', toDtStr).replace('%lagDtStr%', batchLagDtStr)

def fetchOneRow(connection, query):
  cursor = connection.cursor()
  cursor.execute(query)
  columns = [desc[0] for desc in cursor.description]
  row = cursor.fetchone()
  tuples = zip(columns, row)
  rcd = DotMap(tuples)
  cursor.close()
  return rcd
