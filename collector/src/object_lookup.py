#!/usr/bin/python26

import sys
import MySQLdb
from webob import Request
import logging
import json

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)

from db_queries import OBJECT_QUERY_UUID_LOOKUP
from configs import (PROV_DB_HOST, PROV_DB_USERNAME, PROV_DB_PASSWORD,
                    PROV_DB_NAME, OBJECT_LOOKUP_LOGFILE)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a %Y-%m-%d %H:%M:%S',
                    filename=OBJECT_LOOKUP_LOGFILE)


def application(environ, start_response):
    """
    WSGI entry point for API endpoint 'object_lookup'
    This endpoint will lookup an object stored in provenance for a given
    service (each service must be assigned a `service_object_id`)
    """
    req = Request(environ)
    objid = req.params.get('service_object_id')

    try:
        conn = MySQLdb.connect(host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                              passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME)
        cursor = conn.cursor()
        cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (objid))
        results = cursor.fetchall()

        if len(results) == 1:
            uid = str(results[0][0])
            info_msg = "Lookup Object Exists:" + " " + uid
            logging.info(info_msg)
            data_string = json.dumps({'UUID': uid}, indent=4)
            webstatus = '200 OK'
        elif len(results) > 1 :
            errmsg = ("More than one object was found: " + str(results))
            logging.error(errmsg)
            data_string = json.dumps({'Status': 'Exception',
                                'Details': 'Multiple objects found ' +
                                'with the same service_object_id. ' +
                                'Incident has been reported'}, indent=4)
            webstatus = '404 Not Found'
        else:
            err_msg = "Objuuid is null: " + objid
            logging.error(err_msg)
            data_string = json.dumps({'Status': 'Failed',
                                'Details': 'Object does not exist'},
                                indent=4)
            webstatus = '404 Not Found'

        cursor.close()
    except Exception, exc:
        err_msg = "MySQL DB Exception: " + " " + str(exc) + " " + objid
        logging.debug(err_msg)

        data_string = json.dumps({'Status': 'Failed',
                              'Details': 'MySQL Exception. Incident' +
                              ' has been reported'}, indent=4)
        webstatus = '500 Internal Server Error'

    response_headers = [('Content-type', 'application/json')]
    start_response(webstatus, response_headers)
    return (data_string)

