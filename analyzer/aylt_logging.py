#!/usr/bin/python26

"""
A logging utility - nearly identical to the logging utility in Collector.
"""

import logging
from configs import ANALYTICS_LOGFILE

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a %Y-%m-%d %H:%M:%S',
                    filename=ANALYTICS_LOGFILE)


def log_exception(message):
    message = str(message)

    logging.debug(message)


def log_errors(message):
    message = str(message)

    logging.error(message)


def log_info(message, data):
    message = str(message)
    data = str(data)

    logging.info(message)
    logging.info(data)