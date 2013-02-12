#!/usr/bin/python26

#  Copyright (c) 2011, The Arizona Board of Regents on behalf of
#  The University of Arizona
#
#  All rights reserved.
#
#  Developed by: iPlant Collaborative as a collaboration between
#  participants at BIO5 at The University of Arizona (the primary hosting
#  institution), Cold Spring Harbor Laboratory, The University of Texas at
#  Austin, and individual contributors. Find out more at
#  http://www.iplantcollaborative.org/.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the iPlant Collaborative, BIO5, The University
#   of Arizona, Cold Spring Harbor Laboratory, The University of Texas at
#   Austin, nor the names of other contributors may be used to endorse or
#   promote products derived from this software without specific prior
#   written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# Author: Sangeeta Kuchimanchi (sangeeta@iplantcollaborative.org)
# Date: 10/11/2012 
#

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

CONFIG_PATH = '/scripts'

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
             log_info(infoMsg)
           else:
             errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
             log_errors(errMsg)
             failedInsertsAudit(all_data)
             notifySupport(errMsg,scriptname)
         else:
           errMsg = "Audit: QUERY_NO_PROXY_DATA query failed" + all_data
           log_errors(errMsg)
           failedInsertsAudit(all_data)
           notifySupport(errMsg,scriptname)

        elif proxy_username != None:

          insert_status = cursor.execute(QUERY_PROXY % (uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              log_info(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              log_errors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)
          else:
            errMsg = "Audit: QUERY_PROXY query failed" + all_data
            log_errors(errMsg)
            failedInsertsAudit(all_data)
            notifySupport(errMsg,scriptname)

        elif event_data != None:

          insert_status = cursor.execute(QUERY_DATA % (uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              log_info(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              log_errors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)

          else:
            errMsg = "Audit: QUERY_DATA query failed" + all_data
            log_errors(errMsg)
            failedInsertsAudit(all_data)
            notifySupport(errMsg,scriptname)
        else:

          insert_status = cursor.execute(QUERY_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))

          if insert_status == 1:
            update_status = cursor.execute(AUDIT_UPDATE_STATUS % ('Y',id))
            if update_status == 1:
              infoMsg = "Audit Success: " + all_data
              log_info(infoMsg)
            else:
              errMsg = "Audit Update: AUDIT_UPDATE_STATUS query failed" + all_data
              log_errors(errMsg)
              failedInsertsAudit(all_data)
              notifySupport(errMsg,scriptname)
          else:
            errMsg = "Audit: QUERY_ALL query failed" + all_data
            log_errors(errMsg)
            failedInsertsAudit(all_data)   
            notifySupport(errMsg,scriptname)

    cursor.close() 

  except Exception, e:

    errMsg = "AUDIT EXCEPTION: " + str(e) + ": " + all_data
    log_exception(errMsg)
    failedInsertsAudit(all_data) 
    notifySupport(errMsg,scriptname)
    cursor.close()


if __name__ == "__main__":
	try:
	  insertAudit()
	except Exception, e:
          errMsg = "insertAudit() was not initialized" + " " + str(e)
          notifySupport(errMsg,"Audit")
    
