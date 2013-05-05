"""
WSGI application that will provide a configuration summary for the
given deployment it is associated with.  The response will be just
indicate that the summary has been logged to the main log file for the
overall application; thus, no "super serial", sensitive information is
leaked into the outside world.

Provided at the request of QA Czar, Jerry Schneider.
"""

import json
import logging
import threepio
from webob import Request
from configs import (ENDPT_PREFIX, PROV_DB_HOST, PROV_DB_USERNAME,
                    PROV_DB_NAME, PROV_DB_PORT, SNOWFLAKE_HOST, SNOWFLAKE_PORT,
                    SNOWFLAKE_AGENT, BASE_LOG_DIR, OBJECT_FAILED_INSERTS_FILE,
                    PROV_FAILED_INSERTS_FILE, HISTORY_INSERT_FILE, PROV_LOGFILE,
                    OBJECT_LOOKUP_LOGFILE, HISTORY_TRACKING_LOGFILE, MAIL_FROM,
                    MAIL_TO)

threepio.initialize(log_filename=PROV_LOGFILE,
                    logger_name="Deploy-Summary::From-Protocol-Droid",
                    app_logging_level=logging.DEBUG,
                    dep_logging_level=logging.INFO)

from threepio import logger as c3po

DICT_RESP = {'result': {'Status': 'Succeeded', 'Details':
                        'Logged summary info to application log file'}}
def application(environ, start_response):
    """
    WSGI endpoint to trigger logging of the values in ``configs.py``.
    """
    req = Request(environ)
    c3po.info(req)
    resp_string = json.dumps(DICT_RESP, indent=4)

    try:
        _log_summary()
        webstatus = '200 OK'
    except Exception as exc:
        c3po.exception(exc)
        webstatus = '500 Internal Server Error'
        resp_string = json.dumps({'result': {'Status': 'Failed', 'Details':
                              'Logging summary failed - may be due to ' +
                              'misconfiguration, check ``configs``.'}},
                              indent=4)

    response_headers = [('Content-Type', 'application/json'),
                        ('Content-Length', len(resp_string))]
    start_response(webstatus, response_headers)
    return (resp_string)


def _log_summary():
    """
    Kicks out all the imported values from ``configs`` to
    ``PROV_LOGFILE`` for inspection.
    """
    config_dict = {}
    config_dict["Endpoint prefix: "] = ENDPT_PREFIX

    # Provenance Database
    config_dict["Database related settings -> "] = {
            "Database Host: ": PROV_DB_HOST,
            "Database username: ": PROV_DB_USERNAME,
            "Database name: ": PROV_DB_NAME,
            "Database port: ": str(PROV_DB_PORT)
    }

    # Snowflake conmponent info
    config_dict["Snowflake related setting -> "] = {
            "Snowflake host: ": SNOWFLAKE_HOST,
            "Snowflake port: ": str(SNOWFLAKE_PORT),
            "Snowflake client agent name: ": SNOWFLAKE_AGENT
    }

    # Logging
    config_dict["Logging & audit file settings -> "] = {
            "Base directory: ": BASE_LOG_DIR,
            "Audit file for failed object inserts: ":
                                OBJECT_FAILED_INSERTS_FILE,
            "Audit file for failed provenance commits: ":
                                PROV_FAILED_INSERTS_FILE,
            "History file for inserts: ": HISTORY_INSERT_FILE,
            "Central log file for provenance: ": PROV_LOGFILE,
            "Object lookup log file: ": OBJECT_LOOKUP_LOGFILE,
            "History tracking log file: ": HISTORY_TRACKING_LOGFILE
    }

    # Support Mail
    config_dict["Mail settings -> "] = {
            "Mail ``from`` is: ": MAIL_FROM,
            "Mail ``to`` is : ": MAIL_TO,
    }

    config_dict["Important Message"] = "Always remember - if you're having " + \
                                       "issues - blame ``lenards``"

    c3po.info(json.dumps(config_dict, indent=4))

