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

CONFIG_PATH = '/scripts/public/v1.1'

sys.path.append(CONFIG_PATH)
from db_queries import *
from configs import *
from prov_logging import *
from scriptTracking import *




 
conn = MySQLdb.connect (host = PROV_DB_HOST,user = PROV_DB_USERNAME,passwd = PROV_DB_PASSWORD,db = PROV_DB_NAME)
cursor = conn.cursor ()
  
       

cursor.execute(AUDIT_SELECT % ('N'))
results = cursor.fetchall()

print results

if len(results) != 0:
      
  for row in results:

    r_id = int(row[0])
    uuid = int(row[1])
    service_id = int(row[2])
    category_id = int(row[3])
    event_id = int(row[4])
    username = str(row[5])
    proxy_username = str(row[6])
    event_data = str(row[7])
    request_ipaddress = str(row[8])
    created_date = int(row[9])

    print r_id, uuid, service_id, event_id, username, created_date
       
    update_status = cursor.execute("UPDATE Audit SET processed='%s' WHERE id='%s'" % ('Y',r_id))

    print update_status

cursor.close()
