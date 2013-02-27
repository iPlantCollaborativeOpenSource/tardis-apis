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

CONFIG_PATH = '/scripts/public/v1.2'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *


logging.basicConfig (level=logging.DEBUG,
                     format='%(asctime)s %(levelname)-8s %(message)s',
                     datefmt='%a %Y-%m-%d %H:%M:%S',
                     filename=OBJECT_LOOKUP_LOGFILE)


def application(environ, start_response):

   req = Request(environ)
   objid = req.params.get('service_object_id')


   try:
     conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
     cursor = conn.cursor ()
     cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (objid))
     results = cursor.fetchall()
 
     if len(results) == 1: 
       uid = str(results[0][0])
       infoMsg = "Lookup Object Exists:" + " " + uid
       logging.info(infoMsg)  
       data_string = json.dumps({'UUID': uid}, indent=4)
       webstatus = '200 OK'
     elif len(results) > 1 : 
       errMsg = "More than one object was found:" +  " " + str(results)
       logging.error(errMsg)
       data_string = json.dumps({'Status' : 'Exception', 'Details':'Multiple objects found with the same service_object_id. Incident has been reported'}, indent=4)
       webstatus = '404 Not Found'
     else:
       errMsg = "Objuuid is null: " + objid
       logging.error(errMsg)
       data_string = json.dumps({'Status' : 'Failed', 'Details':'Object does not exist'}, indent=4)
       webstatus = '404 Not Found'

     cursor.close()

   except Exception, e:

     errMsg = "MySQL DB Exception: " + " " + str(e) + " " + objid
     logging.debug(errMsg)

     data_string = json.dumps({'Status' : 'Failed', 'Details':'MySQL Exception. Incident has been reported'}, indent=4)
     webstatus = '500 Internal Server Error'
   
   response_headers = [('Content-type', 'application/json')]
   start_response(webstatus,response_headers)
   return (data_string)

