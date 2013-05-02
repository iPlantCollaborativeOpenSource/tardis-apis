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
    """Logs exceptions to the configured log file for provenance
    activities"""
    message = str(message)
    logging.debug(message)


def log_errors(message):
    """Logs errors encountered when provenance activities fail.
    The log file used is the provenance log file defined in
    `configs.py`."""
    message = str(message)
    logging.error(message)


def log_info(message, data):
    """Logs informative messages regarding provenance actitivies to the
    log file defined in `configs.py`."""
    message = str(message)
    data = str(data)

    logging.info(message)
    logging.info(data)