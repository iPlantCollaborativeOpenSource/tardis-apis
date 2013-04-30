#!/usr/bin/python26

import base64
import datetime
from email.mime.text import MIMEText
import logging
import smtplib
import sys

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)
from configs import (HISTORY_TRACKING_LOGFILE, PROV_FAILED_INSERTS_FILE,
                    MAIL_FROM, MAIL_TO)

logging.basicConfig(level=logging.DEBUG, datefmt='%a %Y-%m-%d %H:%M:%S',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    filename=HISTORY_TRACKING_LOGFILE)


def get_history_code(query_string):
    return base64.b64encode(query_string)


# why aren't the functions from prov_logging used?
def track_history_info(infodata):
    info_msg = "History Recorded: " + " " + str(infodata)
    logging.info(info_msg)


def track_history_errors(error_data):
    err_msg = "History Error: " + str(error_data)
    logging.error(err_msg)


def track_history_exceptions(error_data):
    errMsg = "History Exception: " + str(error_data)
    logging.debug(errMsg)


def failed_inserts_audit(data):
    curr_time = datetime.datetime.now()
    insf = open(PROV_FAILED_INSERTS_FILE,"a")
    insf.write(str(curr_time) + " " + data + "\n")
    insf.close()


def notify_support(msg, script):

    if script == "Audit":
        message = "Audit Script: " + str(msg)
    else:
        message = "History Script: " + str(msg)

    mime_msg = MIMEText(message, 'html')
    mime_msg['Subject'] = ('[iPlant Provenance] Exception in ' +
                            str(script) + ' script')
    mime_msg['From'] = MAIL_FROM
    mime_msg['To'] = MAIL_TO
    # Apparently, we're assuming that the deployed server has SMTP
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail (MAIL_FROM, MAIL_TO, mime_msg.as_string())
    smtp.close()

