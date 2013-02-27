#!/usr/bin/python2.6

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
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol
from genpy.Snowflake import Snowflake
from genpy.Snowflake import ttypes
from genpy.Snowflake import constants

CONFIG_PATH = '/scripts/public/v1.0'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *


def application(environ, start_response):

   req = Request(environ)
   objid = req.params.get('service_object_id')
   objname = req.params.get('object_name')
   objdesc = req.params.get('object_desc')

   obj_data = "[" + str(objid) + "," + str(objname) + "," + str(objdesc) + "]" 

   try:

     conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
     cursor = conn.cursor ()
     cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (objid))
     results = cursor.fetchone()
 
     if results == None: 
       uuid = getUUID(obj_data)

       if uuid == None:       
         errMsg = "Objuuid is null: " + obj_data
         LogErrors(errMsg)
         failedInsertsAudit(obj_data)
       else:
         cursor.execute(OBJECT_QUERY_UUID_INSERT % (uuid,objid,objname,objdesc))
         uid = str(uuid)
         infoMsg = "Object created: " + " " + uid
         LogInfo(infoMsg)

     else:
       for value in results:
         uid = str(value)
         infoMsg = "Lookup: Object Exists" + " " + uid
         LogInfo(infoMsg)  

     cursor.close()

     data_string = json.dumps({'UUID' : uid})

     webstatus = '200 OK'
     response_headers = [('Content-type', 'application/json')]
     start_response(webstatus,response_headers)
     return (data_string)


   except Exception, e:

     errMsg = "MySQL DB Exception: " + " " + str(e) +  " " + obj_data
     LogException(errMsg)
     failedInsertsAudit(obj_data)

     data_string = json.dump({'Status' : 'Failed'})

     webstatus = '404 Not Found'
     response_headers = [('Content-type', 'application/json')]
     start_response(webstatus,response_headers)
     return (data_string)

def getUUID(obj_data):

   host = 'localhost'
   port = 7610

   try:

     socket = TSocket.TSocket(host, port)
     transport = TTransport.TFramedTransport(socket)
     protocol = TBinaryProtocol.TBinaryProtocol(transport)
     client = Snowflake.Client(protocol)
     trans_out = transport.open()

     timestmp = client.get_timestamp()
     id = client.get_id("provenanceAPI")

     snflake_data = "[" + str(socket) + "," + str(transport) + "," + str(protocol) + "," + str(client) + "," + str(trans_out) + "," + str(timestmp) + "," + str(id) + "]"
     infoMsg = snflake_data + " " + obj_data
     LogInfo(infoMsg)
 
     return id
     
   except Exception, e:

     errMsg = "Snowflake Server exception: " + str(e) + " " + obj_data
     LogException(errMsg)
     failedInsertsAudit(obj_data)


def failedInsertsAudit(data):

  curr_time = datetime.datetime.now()
  insertfile = open(OBJECT_FAILED_INSERTS_FILE,"a")
  insertfile.write(str(curr_time) + " " + data + "\n")
  insertfile.close()
