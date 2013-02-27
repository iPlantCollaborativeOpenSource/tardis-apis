#!/usr/bin/python26

import logging
from configs import *

logging.basicConfig (level=logging.DEBUG,
                     format='%(asctime)s %(levelname)-8s %(message)s',
                     datefmt='%a %Y-%m-%d %H:%M:%S',
                     filename=PROV_LOGFILE)


def LogException(message):
 
  message = str(message)
  
  logging.debug(message)

def LogErrors(message):
  
  message = str(message)

  logging.error(message)

def LogInfo(message):

  message = str(message)

  logging.info(message)
  
