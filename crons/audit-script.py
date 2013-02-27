#!/usr/bin/python26

import os
import string
import sys
import fileinput
import datetime
import time
import smtplib
import MySQLdb
from email.MIMEText import MIMEText
import site

CONFIG_PATH = '/scripts/public/v1.2'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *
from scriptTracking import *


def insertAudit():

  scriptname = "Audit"

  try:
 
    conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
    cursor = conn.cursor ()
  
  except:
    
    errMsg = "Audit: Connection failed to Provenance database."
    trackAuditExceptions(errMsg)
    notifySupport(errMsg,scriptname)
       
  try:

    cursor.execute(AUDIT_SELECT % ('N'))
    results = cursor.fetchall()

    if len(results) != 0:
      
      for row in results:

        id = int(row[0])
        uuid = int(row[1])
        service_id = int(row[2])
        category_id = int(row[3])
        event_id = int(row[4])
        username = str(row[5])
        proxy_username = str(row[6])
        event_data = str(row[7])
        request_ipaddress = str(row[8])
        created_date = int(row[9])

        all_data = "{Audit row : " + str(id) + "}"

        if proxy_username is None and event_data is None:

         insert_status = cursor.execute(QUERY_NO_PROXY_DATA % (uuid,event_id,category_id,service_id,username,request_ipaddress,created_date))
         if insert_status == 1:
           update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
           if update_status == 1:
             infoMsg = "Audit Success: " + all_data
             LogInfo(infoMsg)
           else:
             errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
             LogErrors(errMsg)
             failedInsertsAudit(all_data)
             notifySupport(errMsg,scriptname)
         else:
           errMsg = "Audit: QUERY_NO_PROXY_DATA query failed" + all_data
           LogErrors(errMsg)
           failedInsertsAudit(all_data)
           notifySupport(errMsg,scriptname)

        elif proxy_username != None:

          insert_status = cursor.execute(QUERY_PROXY % (uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              LogInfo(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              LogErrors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)
          else:
            errMsg = "Audit: QUERY_PROXY query failed" + all_data
            LogErrors(errMsg)
            failedInsertsAudit(all_data)
            notifySupport(errMsg,scriptname)

        elif event_data != None:

          insert_status = cursor.execute(QUERY_DATA % (uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              LogInfo(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              LogErrors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)

          else:
            errMsg = "Audit: QUERY_DATA query failed" + all_data
            LogErrors(errMsg)
            failedInsertsAudit(all_data)
            notifySupport(errMsg,scriptname)
        else:

          insert_status = cursor.execute(QUERY_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              LogInfo(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              LogErrors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)
          else:
            errMsg = "Audit: QUERY_ALL query failed" + all_data
            LogErrors(errMsg)
            failedInsertsAudit(all_data)   
            notifySupport(errMsg,scriptname)

    cursor.close() 

  except Exception, e:

    errMsg = "AUDIT EXCEPTION: " + str(e) + ": " + all_data
    LogException(errMsg)
    failedInsertsAudit(all_data) 
    notifySupport(errMsg,scriptname)
    cursor.close()


if __name__ == "__main__":
	try:
	  insertAudit()
	except Exception, e:
          errMsg = "insertAudit() was not initialized" + " " + str(e)
          notifySupport(errMsg,"Audit")
    
