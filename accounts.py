from dotmap import DotMap
import json

import sql.accountsSql as acctSql
import sql.messagingSql as msgSql
import helpers
import numbersAndSenders as nums

def profileParentAccount(connection, acct, dates):
  acctSid = acct.account_sid
  spendByProductRaw = acctSql.fetchSpendByProduct(connection, acctSid, dates)
  acct.spendByProduct = helpers.transformRowsAndColsToObjects(spendByProductRaw)
  spendByCountryRaw = acctSql.fetchSpendByCountry(connection, acctSid, dates)
  acct.spendByCountry = helpers.transformRowsAndColsToObjects(spendByCountryRaw)
  acct.cntSubAccts = acctSql.countSubAccts(connection, acctSid)
  print(f"there are {acct.cntSubAccts} subaccounts")
  acct.ownNumbers = nums.profileNumbersInAcct(connection, acctSid)
  acct.allNumbers = nums.profileNumbersWithinParentAcct(connection, acctSid)
  acct.ownShortcodes = nums.profileShortcodesInAcct(connection, acctSid)
  if ( len(acct.ownShortcodes) > 0 ):
    scObj = DotMap()
    scObj.type_name = "shortcode"
    scObj.cnt = len(acct.ownShortcodes)
    acct.ownNumbers.append(scObj)
  acct.allShortcodes = nums.profileShortcodesWithinParentAcct(connection, acctSid)
  if ( len(acct.allShortcodes) > 0 ):
    scObj = DotMap()
    scObj.type_name = "shortcode"
    scObj.cnt = len(acct.allShortcodes)
    acct.allNumbers.append(scObj)
  acct.cntOwnMsgServices = msgSql.countMsgServicesInAcct(connection, acctSid)
  acct.cntAllMsgServices = msgSql.countMsgServicesWithinParentAcct(connection, acctSid)
  ownMsgSendsRaw = msgSql.fetchMsgSendsInAcct(connection, acctSid, dates)
  acct.ownMsgSends = helpers.transformRowsAndColsToObjects(ownMsgSendsRaw)
  acct.ownMsgSvcSends = aggregateMsgSendsByMsgSvc(acct.ownMsgSends)
  acct.ownSenderSends = filterMsgSendsWithoutMsgSvc(acct.ownMsgSends)
  cntOwnOptOutsRaw = msgSql.countOptOutsInAcct(connection, acctSid, dates)
  acct.cntOwnOptOuts = helpers.transformRowsAndColsToObjects(cntOwnOptOutsRaw)
  mergeOptOutsIntoMsgSends(acct.ownMsgSvcSends, acct.ownSenderSends, acct.cntOwnOptOuts)

def profileSubAccts(connection, acct, dates):
  for subAcct in acct.highSpendSubAccts:
    print(f"\nprocessing subaccount: {subAcct.account_name} ({subAcct.account_sid})")
    spendByProductRaw = acctSql.fetchSubAcctSpendByProduct(connection, subAcct.account_sid, dates)
    subAcct.spendByProduct = helpers.transformRowsAndColsToObjects(spendByProductRaw)
    spendByCountryRaw = acctSql.fetchSubAcctSpendByCountry(connection, subAcct.account_sid, dates)
    subAcct.spendByCountry = helpers.transformRowsAndColsToObjects(spendByCountryRaw)
    subAcct.ownNumbers = nums.profileNumbersInAcct(connection, subAcct.account_sid)
    subAcct.ownShortcodes = nums.profileShortcodesInAcct(connection, subAcct.account_sid)
    if ( len(subAcct.ownShortcodes) > 0 ):
      scObj = DotMap()
      scObj.type_name = "shortcode"
      scObj.cnt = len(subAcct.ownShortcodes)
      subAcct.ownNumbers.append(scObj)
    subAcct.cntOwnMsgServices = msgSql.countMsgServicesInAcct(connection, subAcct.account_sid)
    ownMsgSendsRaw = msgSql.fetchMsgSendsInAcct(connection, subAcct.account_sid, dates)
    subAcct.ownMsgSends = helpers.transformRowsAndColsToObjects(ownMsgSendsRaw)
    subAcct.ownMsgSvcSends = aggregateMsgSendsByMsgSvc(subAcct.ownMsgSends)
    subAcct.ownSenderSends = filterMsgSendsWithoutMsgSvc(subAcct.ownMsgSends)
    cntOwnOptOutsRaw = msgSql.countOptOutsInAcct(connection, subAcct.account_sid, dates)
    subAcct.cntOwnOptOuts = helpers.transformRowsAndColsToObjects(cntOwnOptOutsRaw)
    mergeOptOutsIntoMsgSends(subAcct.ownMsgSvcSends, subAcct.ownSenderSends, subAcct.cntOwnOptOuts)

def aggregateMsgSendsByMsgSvc(msgSends):
  msgSendsByMsgSvc = {}
  for msgSend in msgSends:
    if msgSend.messaging_service != None:
      if msgSend.messaging_service not in msgSendsByMsgSvc:
        msgSendsByMsgSvc[msgSend.messaging_service] = DotMap()
        msgSendsByMsgSvc[msgSend.messaging_service].cnt = 0
      msgSendsByMsgSvc[msgSend.messaging_service].cnt += msgSend.count
  # convert the dictionary to a list of DotMap objects
  msgSendsByMsgSvcList = [DotMap({"messaging_service": k, "cnt": v.cnt}) for k, v in msgSendsByMsgSvc.items()]
  return msgSendsByMsgSvcList

def filterMsgSendsWithoutMsgSvc(msgSends):
  msgSendsWithoutMsgSvc = []
  for msgSend in msgSends:
    if msgSend.messaging_service == None:
      msgSendsWithoutMsgSvc.append(msgSend)
  # convert the list to a list of DotMap objects
  msgSendsWithoutMsgSvcList = [DotMap({"sender": v.sender, "cnt": v.count}) for v in msgSendsWithoutMsgSvc]
  return msgSendsWithoutMsgSvcList

def mergeOptOutsIntoMsgSends(ownMsgSvcSends, ownSenderSends, optOuts):
  for optOut in optOuts:
    if optOut.record_type == "phone number":
      for msgSend in ownSenderSends:
        if msgSend.sender == optOut.sender:
          msgSend.cntOptOuts = optOut.count
          break
    else:
      for msgSend in ownMsgSvcSends:
        if msgSend.messaging_service == optOut.sender:
          msgSend.cntOptOuts = optOut.count
          break

def fetchHighSpendSubAccts(connection, acctSid, dates):
  rows = acctSql.fetchHighSpendSubAccts(connection, acctSid, dates)
  highSpendSubAccts = helpers.transformRowsAndColsToObjects(rows)
  return highSpendSubAccts

def writeAccount(file, acct):
  # write the account DotMap to the file in JSON format
  json.dump(acct.toDict(), file, indent=4)
  return