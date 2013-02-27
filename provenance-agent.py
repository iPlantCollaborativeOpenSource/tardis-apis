#!/usr/bin/python26

import os
import subprocess
from subprocess import PIPE
import string
import httplib
import urllib
from urlparse import urlparse
import fileinput
import sys
import datetime
import time
import smtplib
import MySQLdb
from email.MIMEText import MIMEText
import webob
from webob import Request, Response
import logging
import site
import json

CONFIG_PATH = '/scripts/public/v1.1'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *
from scriptTracking import *

def application(environ, start_response):

   req = Request(environ)

   uuid = req.params.get('uuid')
   service_name = req.params.get('service_name')
   category_name = req.params.get('category_name')
   event_name = req.params.get('event_name')
   username = req.params.get('username')
   proxy_username = req.params.get('proxy_username')
   event_data = req.params.get('event_data')
   request_ipaddress = req.params.get('request_ipaddress') 
   track_history = req.params.get('track_history')
   track_history_code = req.params.get('track_history_code')

   event_id = getID(event_name, "EVENT")
   category_id = getID(category_name, "CATEGORY")
   service_id = getID(service_name, "SERVICE")
   created_date = getDateTime()
   

   all_data = "{" + str(uuid) + "," + str(service_name) + "," + str(category_name) + "," + str(event_name) + "," + str(username) + "," + str(proxy_username) + "," + str(event_data) + "," + str(request_ipaddress) + "," + str(created_date) + "}"

       
   try:

     conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
     cursor = conn.cursor ()

     if proxy_username is None and event_data is None:

       insert_status = cursor.execute(QUERY_NO_PROXY_DATA % (uuid,event_id,category_id,service_id,username,request_ipaddress,created_date))
       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_NO_PROXY_DATA query failed" + all_data
         LogErrors(errMsg)
         audit_insert = cursor.execute(AUDIT_NO_PROXY_DATA % (uuid,event_id,category_id,service_id,username,request_ipaddress,created_date))
         if audit_insert != 1:
           failedInsertsAudit(all_data)
          

     elif proxy_username != None:

       insert_status = cursor.execute(QUERY_PROXY % (uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_PROXY query failed" + all_data
         LogErrors(errMsg)
         audit_insert = cursor.execute(AUDIT_PROXY % (uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date))
         if audit_insert != 1:
           failedInsertsAudit(all_data)

     elif event_data != None:

       insert_status = cursor.execute(QUERY_DATA % (uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_DATA query failed" + all_data
         LogErrors(errMsg)
         audit_insert = cursor.execute(AUDIT_DATA % (uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date))
         if audit_insert != 1:
           failedInsertsAudit(all_data)

     else:

       insert_status = cursor.execute(QUERY_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_ALL query failed" + all_data
         LogErrors(errMsg)
         audit_insert = cursor.execute(AUDIT_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))
         if audit_insert != 1:
           failedInsertsAudit(all_data)         

     
     if track_history == "1":
       if track_history_code != None:
 
         history_data = str(track_history_code) + " " + str(all_data)
         
         hist_check = cursor.execute(HIST_SELECT_QUERY % (track_history_code))
         results = cursor.fetchall()
         if len(results) != 0:         
           hist_status = cursor.execute(HIST_INSERT_QUERY % (track_history_code,uuid,event_id,category_id,service_id,username,created_date))
           if str(hist_status) == "1":
             infoMsg = "History request recorded:" + " " + str(track_history_code) + " " + all_data
             LogInfo(infoMsg)
           else:
             errMsg = "HIST_INSERT_QUERY failed" + history_data
             LogErrors(errMsg)
             trackHistoryErrors(history_data)
         else:
           parent_query = "Y"
           hist_status = cursor.execute(HIST_INSERT_QUERY_PARENT % (track_history_code,uuid,event_id,category_id,service_id,username,created_date,parent_query))
           if str(hist_status) == "1":
             infoMsg = "History request recorded:" + " " + str(track_history_code) + " " + all_data
             LogInfo(infoMsg)
           else:
             errMsg = "HIST_INSERT_QUERY_PARENT failed" + history_data
             LogErrors(errMsg)
             trackHistoryErrors(history_data)
         
       else:
         history_data = str(username) + ":" + str(uuid) + ":" + str(created_date)
         history_code = getHistoryCode(history_data)
         infoMsg = "History code generated: " + str(history_code) + " " + all_data
         LogInfo(infoMsg)
     else:
       if track_history_code != None:
         errMsg = "Track History flag not set but history code was sent. Please check history tracking error logs." + " " + str(track_history_code)
         LogErrors(errMsg)
         history_data = str(track_history_code) + "," + str(all_data)
         trackHistoryErrors(history_data)

     cursor.close()

     webstatus = '200 OK'
     response_headers = [('Content-type', 'application/json')]
     if track_history == "1" and track_history_code == None:
       data = json.dumps({'result':{'Status':'Success','Details':'Provenance recorded','History code':history_code}}, indent=4)   
     else:
       data = json.dumps({'result':{'Status':'Success','Details':'Provenance recorded'}}, indent=4)

     start_response(webstatus,response_headers)
     return (data)

   except Exception, e:

     errMsg = "EXCEPTION: " + str(e) + ": " + all_data
     LogException(errMsg)
     audit_insert = cursor.execute(AUDIT_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))
     if audit_insert != 1:
       failedInsertsAudit(all_data) 
 
     cursor.close()

     webstatus = '400 Bad Request'
     response_headers = [('Content-type', 'application/json')]
     data = json.dumps({'result':{'Status':'Failed','Details':'Provenance was not recorded. Audit data recorded.'}}, indent=4) 
     start_response(webstatus,response_headers)
     return (data)

def getDateTime():

   currenttime = datetime.datetime.now()
   current_in_sec = time.mktime(currenttime.timetuple())

   return int(current_in_sec)


def getID(name, key):

   conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
   cursor = conn.cursor ()

   if key == "EVENT":

     cursor.execute(QUERY_EVENT_ID % (name))
     results = cursor.fetchone()
     id = int(results[0])
 
   elif key == "SERVICE":     

     cursor.execute(QUERY_SERVICE_ID % (name))
     results = cursor.fetchone()
 
     id = int(results[0])
   
   else:

     cursor.execute(QUERY_CATEGORY_ID % (name))
     results = cursor.fetchone()
 
     id = int(results[0])
   
   cursor.close()
   
   return id

