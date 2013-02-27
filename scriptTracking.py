#!/usr/bin/python2.6

import os
import subprocess
from subprocess import PIPE
import string
import fileinput
import sys
import datetime
import time
import logging
import site
import base64
from email.MIMEText import MIMEText
import smtplib

CONFIG_PATH = '/scripts/public/v1.3'

sys.path.append(CONFIG_PATH)
from configs import *


logging.basicConfig (level=logging.DEBUG,
                     format='%(asctime)s %(levelname)-8s %(message)s',
                     datefmt='%a %Y-%m-%d %H:%M:%S',
                     filename=HISTORY_TRACKING_LOGFILE)


def getHistoryCode(query_string):

  encoded = base64.b64encode(query_string)
  return (encoded)


def trackHistoryInfo(infodata):

  infoMsg = "History Recorded: " + " " + str(infodata)
  logging.info(infoMsg)

def trackHistoryErrors(error_data):

  errMsg = "History Error: " + str(error_data)
  logging.error(errMsg)

def trackHistoryExceptions(error_data):

  errMsg = "History Exception: " + str(error_data)
  logging.debug(errMsg)

def failedInsertsAudit(data):

  curr_time = datetime.datetime.now()
  insf = open(PROV_FAILED_INSERTS_FILE,"a")
  insf.write(str(curr_time) + " " + data + "\n")
  insf.close()

def notifySupport(msg,script):

  if script == "Audit":
    message = "Audit Script: " + str(msg)
  else:
    message = "History Script: " + str(msg)

  mime_msg = MIMEText (message, 'html')
  mime_msg['Subject'] = '[iPlant Provenance] Exception in ' + str(script) + ' script'
  mime_msg['From'] = MAIL_FROM
  mime_msg['To'] = MAIL_TO

  s = smtplib.SMTP('localhost')
  s.sendmail (MAIL_FROM, MAIL_TO, mime_msg.as_string())
  s.close()

