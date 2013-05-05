#!/usr/bin/python26

import sys
import MySQLdb
from webob import Request
import logging
import json

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)

from db_queries import (OBJECT_QUERY_UUID_LOOKUP, SERVICE_ID_FROM_KEY_QUERY)
from configs import (PROV_DB_HOST, PROV_DB_USERNAME, PROV_DB_PASSWORD,
                    PROV_DB_NAME, PROV_DB_PORT, OBJECT_LOOKUP_LOGFILE)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a %Y-%m-%d %H:%M:%S',
                    filename=OBJECT_LOOKUP_LOGFILE)


def application(environ, start_response):
    """
    Performs an ``Object`` lookup given a ``service_key`` &
    ``object_id``.

    The ``service_key`` is used to query for the ``service_id``, a
    foreign key into the ``Service`` table.  This provides "scoping" or
    namespacing of the service correlation identifier (that's a fancy
    way to say 'the object identifier that makes sense within the
    _domain_, or `scope`, of the service committing provenance')

    WSGI entry point for API endpoint 'object_lookup'.

    This endpoint will lookup an object stored in the ``Object`` that is
    related to actions/events within the ``Provenance`` table.

    Currently, the query parameters are passed via the query string.

    Expected parameters are:

    ``service_key`` - a short, alpha-numeric "key" that identifies
                      a calling service.
    ``object_id`` - an identifier for an object that exists within the
                    domain of the service.

    An optional parameter +might+ be ``service_id``.  This is unlikely
    as it is an auto-incremented numeric key that a calling service is
    not likely to know.  In the current API, there is no endpoint to
    tell a service what its' ``service_id`` is.
    """
    req = Request(environ)
    srv_key = req.params.get('service_key')
    obj_id = req.params.get('object_id')

    data_string, webstatus = _handle_get(srv_key, obj_id)

    response_headers = [('Content-Type', 'application/json'),
                        ('Content-Length', len(data_string))]
    start_response(webstatus, response_headers)
    return (data_string)


def _handle_get(srv_key, obj_id):
    """
    Handle the object lookup for the request.

    Returns a response string and HTTP status code as a tuple in the
    form: ``(data_string, webstatus)``.
    """
    try:
        conn = MySQLdb.connect(host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                               passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME,
                               port=PROV_DB_PORT)
        cursor = conn.cursor()

        cursor.execute(SERVICE_ID_FROM_KEY_QUERY % (srv_key))
        key_to_id = cursor.fetchone()
        srv_id, = key_to_id

        cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (obj_id, srv_id))
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
                                'with the same `object_id` for the same ' +
                                ' `service_id`. Incident has been reported'},
                                indent=4)
            webstatus = '404 Not Found'
        else:
            err_msg = "Object UUID is null: " + obj_id
            logging.error(err_msg)
            data_string = json.dumps({'Status': 'Failed',
                                'Details': 'Object does not exist'},
                                indent=4)
            webstatus = '404 Not Found'
        cursor.close()
    except Exception, exc:
        err_msg = "MySQL DB Exception: " + " " + str(exc) + " " + obj_id
        logging.debug(err_msg)

        data_string = json.dumps({'Status': 'Failed',
                              'Details': 'MySQL Exception. Incident' +
                              ' has been reported'}, indent=4)
        webstatus = '500 Internal Server Error'

    return (data_string, webstatus)