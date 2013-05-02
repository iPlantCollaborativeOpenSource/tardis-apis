#!/usr/bin/python26

"""
Provided pre-configured logging for provenance activities.
"""

import logging
from configs import PROV_LOGFILE

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a %Y-%m-%d %H:%M:%S',
                    filename=PROV_LOGFILE)


def log_exception(message):
    """Logs exceptions to the configured log file for provenance
    activities"""
    message = str(message)
    logging.debug(message)
    logging.exception(message)

def log_errors(message):
    """Logs errors encountered when provenance activities fail.
    The log file used is the provenance log file defined in
    `configs.py`."""
    message = str(message)
    logging.error(message)

def log_info(message):
    """Logs informative messages regarding provenance actitivies to the
    log file defined in `configs.py`."""
    message = str(message)
    logging.info(message)

