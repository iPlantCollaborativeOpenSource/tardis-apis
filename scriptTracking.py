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

CONFIG_PATH = '/scripts'

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

