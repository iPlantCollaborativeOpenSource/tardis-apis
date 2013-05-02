"""
Handles HTTP POSTs with form-encoded or JSON data bodies...
"""

import json
import MySQLdb
from webob import Request

from db_queries import (AUDIT_ALL, AUDIT_DATA, AUDIT_PROXY, AUDIT_NO_PROXY_DATA,
                        HIST_INSERT_QUERY_PARENT, HIST_INSERT_QUERY,
                        HIST_SELECT_QUERY, QUERY_ALL, QUERY_CATEGORY_ID,
                        QUERY_CHECK_UUID, QUERY_DATA, QUERY_EVENT_ID,
                        QUERY_NO_PROXY_DATA, QUERY_PROXY, QUERY_SERVICE_ID,
                        QUERY_SERVICE_VERSION_ID)
from configs import (PROV_DB_HOST, PROV_DB_USERNAME, PROV_DB_PASSWORD,
                     PROV_DB_NAME, PROV_DB_PORT)
from prov_logging import log_errors, log_exception, log_info
from provenance_agent import validate, ProvTuple
from script_tracking import (failed_inserts_audit, get_history_code,
                             track_history_errors)

FORM_ENCODED_MIME = 'application/x-www-form-urlencoded'
JSON_BODY_MIME = 'application/json'

def application(environ, start_response):
    """
    Endpoint for a 'fire-and-forget' style provenance logging
    interaction.

    This endpoint will expect the union of the information associated
    with a call to `/register` and `/provenance`.  This is, all required
    parameters of both endpoints will need to be included such that if a
    UUID is not included, a "multi-action" operation can be performed.

    This means that the conversational nature of the original design is
    overted and a calling semantic that does not require statefulness
    can be employed by clients calling this API.
    """
    req = Request(environ)
    args, kwargs = environ['wsgiorg.routing_args']
    if (len(args) > 0):
        log_info('Positional arguments include: ' + args)

    if (req.method == 'POST'):
        json_data, webstatus = _handle_post(req, kwargs)
    else:
        webstatus = '405 Method Not Allowed'
        json_data = json.dumps({'result': {'Status': 'Failed',
                                'Details': 'Incorrect HTTP METHOD'}},
                               indent=4)
    info_msg = "Request Processed: " + str(webstatus) + " Details: " + \
        str(json_data)
    log_info(info_msg)

    response_headers = [('Content-type', 'application/json')]
    start_response(webstatus, response_headers)
    return (json_data)


def _handle_post(request, routing_args):
    """
    Private method for processing an HTTP POST to the WSGI endpoint
    encapsulated in this file.
    """
    # let's grab the POST body, if it's there...
    prov, json_data, webstatus = _get_post_body(request)

    if prov.uuid is None:
        # we look for object_* and insert, fetch uuid

        print 'this is a compound insert: both into Object & Prov tables...'
    # then log provenance

    return json_data, webstatus


def _get_post_body(request):
    """
    Retrieve data encoded in the request body.

    This method returns three values, a successful retrieval from the
    body will be result in an instance of ``provenance_agent.ProvTuple``
    and the second & third arguments will be ``None``.

    If this method were to fail, further information about the context
    of the failure in the second & third return values. The second will
    contain data about the failure encoded as JSON and the third will
    contain a web status code.
    """
    prov = None
    webstatus = None
    json_data = None
    # we're only accepting form-encoded or JSON bodies - nothing else.
    if (request.environ['CONTENT_TYPE'] == FORM_ENCODED_MIME):
        prov = _create_tuple(request.POST, request.remote_addr)
    elif (request.environ['CONTENT_TYPE'] == JSON_BODY_MIME):
        prov = _create_tuple(json.loads(request.body), request.remote_addr)
    else: #fail
        json_data, webstatus = _post_body_error(request)

    return prov, json_data, webstatus


def _create_tuple(body, request_ip):
    """
    Pull the values out of the request body and create a tuple
    representation.
    """
    ## service_object_id, object_name, object_desc, parent_uuid
    ## uuid, username, service_name, event_name, category_name, request_ipaddr
    ## proxy_username, event_data, version, track_history, track_history_code
    prov = None

    try:
        # if you have a UUID, we'll grab value & log the provenance
        if body.get('uuid') is not None:
            prov = ProvTuple(body['uuid'], body['service_name'],
                            body['category_name'], body['event_name'],
                            body['username'], request_ip)
        else:
            prov = ProvTuple(None, body['service_name'], body['category_name'],
                            body['event_name'], body['username'], request_ip)
            prov.service_object_id = body['service_object_id']
            prov.object_name = body['object_name']
            prov.object_desc = body['object_desc']
            prov.parent_uuid = body.get('parent_uuid') # optional...
        # optional paremeters - so we're using get()
        prov.proxy_username = body.get('proxy_username')
        prov.event_data = body.get('event_data')
        prov.version = body.get('version')
        prov.track_history = body.get('track_history')
        prov.track_history_code = body.get('track_history_code')
    except KeyError, kerr:
        raise kerr

    return prov


def _post_body_error(request):
    """
    Provide error feedback when getting the POST body has failed.

    Only ``FORM_ENCODED_MIME`` and ``JSON_BODY_MIME`` are accepted.
    """
    if request.body is None or request.body == '':
        webstatus = 'HTTP POST body expected'
        json_data = json.dumps({'result': {'Status': 'Failed',
                            'Details': 'HTTP POST body expected in ' +
                            'form-encoding or JSON'}},
                            indent=4)
    else:
        webstatus = 'HTTP POST body in unexpected content type'
        json_data = json.dumps({'result': {'Status': 'Failed',
                            'Details': 'HTTP POST body expected in ' +
                            'form-encoding or JSON'}},
                            indent=4)
    return json_data, webstatus
