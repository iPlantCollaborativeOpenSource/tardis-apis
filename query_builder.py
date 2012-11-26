#!/usr/bin/python26

import os
import string
import fileinput
import sys
import datetime
import time
from datetime import date
import smtplib
import MySQLdb
from email.MIMEText import MIMEText
import logging
import site
from db_queries import *
from config import *
from aylt_logging import *


def buildQuery(uuid,service_name,category_name,event_name,username,proxy_username,start_date,end_date,days,record_limit):

  userdict = {}
  datedict = {}
  parameters = []
  
  if username != None:

    userdict["username"] = username 

  if proxy_username != None:

    userdict["proxy_username"] = proxy_username 

  if event_name != None:

    userdict["event_name"] = event_name

  if category_name != None:

    userdict["category_name"] = category_name

  if service_name != None:

    userdict["service_name"] = service_name

  if uuid != None:

    userdict["uuid"] = uuid

  if start_date != None and end_date != None:

     st_date = time.strptime(start_date,"%Y-%m-%d")
     ed_date = time.strptime(end_date,"%Y-%m-%d")

     if st_date < ed_date:
       sdate = int(time.mktime(st_date))
       edate = int(time.mktime(ed_date))
     else:
       sdate = int(time.mktime(ed_date))
       edate = int(time.mktime(st_date))   

     datedict["start_date"] = sdate
     datedict["end_date"] = edate

  elif start_date == None and end_date == None and days != None:

     date_range = getDateRange(days)
     sdate = int(date_range[0])
     edate = int(date_range[1])

     datedict["start_date"] = sdate
     datedict["end_date"] = edate

  else:
     days = 8
     date_range = getDateRange(days)
     sdate = int(date_range[0])
     edate = int(date_range[1])

     datedict["start_date"] = sdate
     datedict["end_date"] = edate

  QUERY_SELECT = "SELECT * FROM Analytics WHERE "

  for filter, value in userdict.iteritems():
    QUERY_SELECT += filter + "=" + "%s" + " AND "
    parameters.append(str(value))

  QUERY_SELECT += "created_date BETWEEN %s AND %s"
  for cre_date, cre_vals in datedict.iteritems():
    parameters.append(str(cre_vals))


  QUERY_SELECT += "]"
  QUERY_SELECT = QUERY_SELECT.strip("AND ]")

  return (QUERY_SELECT,parameters)

def getDateRange(days_value):
   
   days_value = int(days_value)

   today_date = date.today() + datetime.timedelta(days=1)
   date_delta = datetime.timedelta(days=days_value)

   print date_delta
 
   start_date = today_date - date_delta
  
   end_date_in_sec = int(time.mktime(today_date.timetuple()))
   start_date_in_sec = int(time.mktime(start_date.timetuple()))

   return(start_date_in_sec,end_date_in_sec)
