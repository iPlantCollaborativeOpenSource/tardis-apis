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

CONFIG_PATH = '/scripts/public/v1.0'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *

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
 
   event_id = getID(event_name, "EVENT")
   category_id = getID(category_name, "CATEGORY")
   service_id = getID(service_name, "SERVICE")
   created_date = getDateTime()

   all_data = "{" + str(uuid) + "," + str(service_name) + "," + str(category_name) + "," + str(event_name) + "," + str(username) + "," + str(proxy_username) + "," + str(event_data) + "," + str(request_ipaddress) + "," + str(created_date) + "}"
   LogInfo(all_data)
       
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
         failedInsertsAudit(all_data)


     elif proxy_username != None:

       insert_status = cursor.execute(QUERY_PROXY % (uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_PROXY query failed" + all_data
         LogErrors(errMsg)
         failedInsertsAudit(all_data)

     elif event_data != None:

       insert_status = cursor.execute(QUERY_DATA % (uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_DATA query failed" + all_data
         LogErrors(errMsg)
         failedInsertsAudit(all_data)

     else:

       insert_status = cursor.execute(QUERY_ALL % (uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date))

       if str(insert_status) == "1":
         infoMsg = "Success: " + all_data
         LogInfo(infoMsg)
       else:
         errMsg = "QUERY_ALL query failed" + all_data
         LogErrors(errMsg)
         failedInsertsAudit(all_data)

     cursor.close()

     webstatus = '200 OK'
     response_headers = [('Content-type', 'application/json')]
     data = json.dumps({'result':{'Status':'Success','Details':'Provenance recorded'}}, indent=4)   
     start_response(webstatus,response_headers)
     return (data)

   except Exception, e:

     errMsg = "EXCEPTION: " + str(e) + ": " + all_data
     LogException(errMsg)
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

def failedInsertsAudit(data):

  curr_time = datetime.datetime.now()
  insf = open(PROV_FAILED_INSERTS_FILE,"a")
  insf.write(str(curr_time) + " " + data + "\n")
  insf.close()
  
