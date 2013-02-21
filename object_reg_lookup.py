#!/usr/bin/python2.6

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

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *


def application(environ, start_response):

   req = Request(environ)
   if (req.method == 'POST'):

     objid = req.params.get('service_object_id')
     objname = req.params.get('object_name')
     objdesc = req.params.get('object_desc')

     obj_data = "[" + str(objid) + "," + str(objname) + "," + str(objdesc) + "]"

     if objid != None:
       try:
         conn = MySQLdb.connect (host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                                 passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME)
         cursor = conn.cursor ()
         cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (objid))
         results = cursor.fetchone()
 
         if results == None: 
           uuid = get_uuid(obj_data)

           if uuid == None:       
             errMsg = "Objuuid is null: " + obj_data
             log_errors(errMsg)
             failedInsertsAudit(obj_data)
             data_string = json.dumps({'Status' : 'Failed', 'Details' : 'Error retrieving UUID'},indent=4)
             webstatus = '503 Service Unavailable'
           else:
             cursor.execute(OBJECT_QUERY_UUID_INSERT % (uuid, objid, objname,
                                                        objdesc))
             uid = str(uuid)
             infoMsg = "Object created: " + " " + uid
             log_info(infoMsg)
             data_string = json.dumps({'UUID' : uid}, indent=4)
             webstatus = '200 OK'

         else:
           for value in results:
             uid = str(value)
             infoMsg = "Lookup: Object Exists" + " " + uid
             log_info(infoMsg)  
             data_string = json.dumps({'UUID' : uid})
             webstatus = '200 OK'

         cursor.close()

       except Exception, e:

         errMsg = "MySQL DB Exception: " + " " + str(e) +  " " + obj_data
         log_exception(errMsg)
         failedInsertsAudit(obj_data)

         data_string = json.dumps({'Status' : 'Failed',
                                   'Details' : 'MySQL Exception. Failed to retrieve data'}, indent=4)
         webstatus = '500 Internal Server Error'
   
     else:
       errMsg = "Null Exception: service_object_id cannot be null " + obj_data
       log_exception(errMsg)

       data_string = json.dumps({'Status' : 'Failed','Details':'Null Exception. service_object_id cannot be null'}, indent=4)
       webstatus = '500 Internal Server Error'
  
   else:
     data_string = json.dumps({'Status' : 'Failed', 'Details' : 'Incorrect HTTP METHOD'}, indent=4)
     webstatus = '405 Method Not Allowed'


   response_headers = [('Content-type', 'application/json')]
   start_response(webstatus, response_headers)
   return (data_string)

def get_uuid(obj_data):

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
     log_info(infoMsg)
 
     return id
   except Exception, e:
     errMsg = "Snowflake Server exception: " + str(e) + " " + obj_data
     log_exception(errMsg)
     failedInsertsAudit(obj_data)


def failedInsertsAudit(data):
  curr_time = datetime.datetime.now()
  insertfile = open(OBJECT_FAILED_INSERTS_FILE,"a")
  insertfile.write(str(curr_time) + " " + data + "\n")
  insertfile.close()
