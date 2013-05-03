#!/usr/bin/python26

import datetime
import re
import sys
import time
import MySQLdb
from webob import Request
import json

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)
from db_queries import (AUDIT_ALL, AUDIT_DATA, AUDIT_PROXY, AUDIT_NO_PROXY_DATA,
                        HIST_INSERT_QUERY_PARENT, HIST_INSERT_QUERY,
                        HIST_SELECT_QUERY, QUERY_ALL, QUERY_CATEGORY_ID,
                        QUERY_CHECK_UUID, QUERY_DATA, QUERY_EVENT_ID,
                        QUERY_NO_PROXY_DATA, QUERY_PROXY, QUERY_SERVICE_ID,
                        QUERY_SERVICE_VERSION_ID)
from configs import (PROV_DB_HOST, PROV_DB_USERNAME, PROV_DB_PASSWORD,
                     PROV_DB_NAME, PROV_DB_PORT)
from prov_logging import log_errors, log_exception, log_info
from script_tracking import (failed_inserts_audit, get_history_code,
                             track_history_errors)

UUID_FIELD = re.compile(r'^[0-9]+$')
STR_FIELD = re.compile(r'^[A-Za-z0-9\-_]+$')
VER_FIELD = re.compile(r'^[A-Za-z0-9\.\-_]+$')


class ProvTuple(object):

    """A simple grouping of request data."""
    def __init__(self, uuid_, service_name, category_name, event_name,
                 username, request_ip):
        """
        Require information for logging a provenance object:
        ``uuid``, ``service_name``, ``category_name``, ``event_name``,
        ``username``, ``request_ip`` (request IP address)

        Optional arguments can be set by attribute:
        ``proxy_username``, ``event_data``, ``track_history``,
        ``track_history_code``, ``created_date``, ``version``
        """
        super(ProvTuple, self).__init__()
        self.uuid = uuid_
        self.service_name = service_name
        self.category_name = category_name
        self.event_name = event_name
        self.username = username
        self.request_ipaddress = request_ip
        # Bookkeeping or derived by construction...
        self.created_date = get_date_time()
        # Optional are set for None for now...
        self.proxy_username = None
        self.event_data = None
        self.track_history = None
        self.track_history_code = None
        self.version = None

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.__repr__()

    def get_history_info(self):
        """
        Returns a colon delimited string of attributes associated with
        history tracking information.
        """
        return '{}:{}:{}'.format(self.username, self.uuid, self.created_date)

    def has_required_arguments(self):
        """
        Simple verifier method to incidate if the required attributes
        have been set for this instance.
        """
        return (self.uuid != None and self.service_name != None and
                self.category_name != None and self.event_name != None and
                self.username != None)


def application(environ, start_response):
    """Endpoint for creating provenance records given a service, a
    category, and an event.

    These elements must be added prior to registering an object and
    creating any provenance information.

    Also included for additional tracking and bookkeeping are:
    ``username`` - this may be a system or daemon account
    ``proxy_username`` - the user as system account is acting on behalf of
    ``event_data`` - any additional info associated with the event
    ``request_ipaddress`` - the IP address of the service posting data
    ``track_history`` - boolean-like code indicating to track history
    ``track_history_code`` - the association code for history tracking
    ``created_date`` - time in seconds since Epoch
    ``version`` - string identifier indicating version
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


def _handle_post(req, req_args):
    """Private method for handling an HTTP POST to this endpoint."""
    req_tuple = ProvTuple(req_args['uuid'], req_args['service_name'],
                          req_args['category_name'], req_args['event_name'],
                          req_args['username'], req.remote_addr)
    req_tuple.proxy_username = req.params.get('proxy_username')
    req_tuple.event_data = req.params.get('event_data')
    req_tuple.track_history = req.params.get('track_history')
    req_tuple.track_history_code = req.params.get('track_history_code')
    req_tuple.version = req.params.get('version')

    # if the above was an object, a json.dumps() call would create this
    # same string that is being contenated and it would include key names
    all_data = str(req_tuple)
    info_msg = "Received provenance request: " + all_data
    log_info(info_msg)

    return _add_valid_tuple(req_tuple)


def _add_valid_tuple(req_tuple):
    """
    If we've got a valid request tuple, we add it - like a boss.

    This was factored out of _handle_post() so that a public method,
    ``commit_provenance()`` could reuse it.
    """
    validated, details = validate(req_tuple)

    info_msg = "Validation:" + str(validated) + " Details: " + str(details)
    log_info(info_msg)

    if validated:
        json_data, webstatus = _process_valid_request(req_tuple)
    else:
        json_data = json.dumps({'result': {'Status': 'Failed',
                               'Details': 'Validation Failed',
                               'Report': details}}, indent=4)
        webstatus = '400 Bad Request'
    return (json_data, webstatus)


def commit_provenance(req_tuple):
    """
    Inserts provenance.

    We could say that this method "logs provenance" but that would
    confuse the matter what _provenance_ is not the same as "logging".

    This method is committing some historical information regarding the
    actions or operations processed on an object that has been
    registered in the ``Objects`` table.

    Note: this was extracted as a method so that it could be called
    from another WSGI endpoint application that is performing a
    similar, but not 100 percent identifical operation.
    """
    json_data, webstatus = _add_valid_tuple(req_tuple)
    log_info(webstatus + ' ' + json_data)
    # if we've got an ``OK`` then we can assume that it was inserted
    return webstatus == '200 OK' # again, I hate to do this comparison


def _process_valid_request(req_tuple):

    if req_tuple.version == None:
        req_tuple.version = "Default"

    event_id = get_id(req_tuple.event_name, "EVENT", req_tuple.version)
    category_id = get_id(req_tuple.category_name, "CATEGORY",
                         req_tuple.version)
    service_id = get_id(req_tuple.service_name, "SERVICE", req_tuple.version)

    if event_id != "EMPTY" and category_id != "EMPTY" and service_id != "EMPTY":

        all_data = str(req_tuple)

        try:
            conn = MySQLdb.connect(host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                                   passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME,
                                   port=PROV_DB_PORT)
            cursor = conn.cursor()

            cursor.execute(QUERY_CHECK_UUID % (req_tuple.uuid))
            check_results = cursor.fetchall()
            if len(check_results) == 1:

                if (req_tuple.proxy_username is None and
                        req_tuple.event_data is None):
                    insert_status = cursor.execute(
                        QUERY_NO_PROXY_DATA % (req_tuple.uuid, event_id,
                                               category_id, service_id,
                                               req_tuple.username,
                                               req_tuple.request_ipaddress,
                                               req_tuple.created_date))
                    if str(insert_status) == "1":
                        info_msg = "Success: " + all_data
                        log_info(info_msg)
                    else:
                        err_msg = "QUERY_NO_PROXY_DATA query failed" + all_data
                        log_errors(err_msg)
                        audit_insert = cursor.execute(AUDIT_NO_PROXY_DATA %
                                                   (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                        if audit_insert != 1:
                            failed_inserts_audit(all_data)

                elif req_tuple.proxy_username != None:
                    insert_status = cursor.execute(QUERY_PROXY %
                                                    (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.proxy_username,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                    if str(insert_status) == "1":
                        info_msg = "Success: " + all_data
                        log_info(info_msg)
                    else:
                        err_msg = "QUERY_PROXY query failed" + all_data
                        log_errors(err_msg)
                        audit_insert = cursor.execute(AUDIT_PROXY %
                                                    (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.proxy_username,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                        if audit_insert != 1:
                            failed_inserts_audit(all_data)

                elif req_tuple.event_data != None:

                    insert_status = cursor.execute(QUERY_DATA
                                                % (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.event_data,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                    if str(insert_status) == "1":
                        info_msg = "Success: " + all_data
                        log_info(info_msg)
                    else:
                        err_msg = "QUERY_DATA query failed" + all_data
                        log_errors(err_msg)
                        audit_insert = cursor.execute(AUDIT_DATA
                                                % (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.event_data,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                        if audit_insert != 1:
                            failed_inserts_audit(all_data)

                else:
                    insert_status = cursor.execute(QUERY_ALL
                                                % (req_tuple.uuid, event_id,
                                                  category_id, service_id,
                                                  req_tuple.username,
                                                  req_tuple.proxy_username,
                                                  req_tuple.event_data,
                                                  req_tuple.request_ipaddress,
                                                  req_tuple.created_date))
                    if str(insert_status) == "1":
                        info_msg = "Success: " + all_data
                        log_info(info_msg)
                    else:
                        err_msg = "QUERY_ALL query failed" + all_data
                        log_errors(err_msg)
                        audit_insert = cursor.execute(AUDIT_ALL
                                                    % (req_tuple.uuid, event_id,
                                                    category_id, service_id,
                                                    req_tuple.username,
                                                    req_tuple.proxy_username,
                                                    req_tuple.event_data,
                                                    req_tuple.request_ipaddress,
                                                    req_tuple.created_date))
                        if audit_insert != 1:
                            failed_inserts_audit(all_data)

                if req_tuple.track_history == "1":

                    if req_tuple.track_history_code != None:
                        history_data = str(
                            req_tuple.track_history_code) + " " + all_data

                        cursor.execute(HIST_SELECT_QUERY %
                                      (req_tuple.track_history_code))
                        results = cursor.fetchall()
                        if len(results) != 0:
                            hist_status = cursor.execute(HIST_INSERT_QUERY
                                            % (req_tuple.track_history_code,
                                                req_tuple.uuid, event_id,
                                                category_id, service_id,
                                                req_tuple.username,
                                                req_tuple.created_date))
                            if str(hist_status) == "1":
                                info_msg = ("History request recorded:" + " " +
                                            str(req_tuple.track_history_code) +
                                            " " + all_data)
                                log_info(info_msg)
                            else:
                                err_msg = "HIST_INSERT_QUERY failed" + \
                                    history_data
                                log_errors(err_msg)
                                track_history_errors(history_data)
                        else:
                            parent_query = "Y"
                            hist_status = cursor.execute(
                                HIST_INSERT_QUERY_PARENT % (
                                    req_tuple.track_history_code,
                                    req_tuple.uuid, event_id, category_id,
                                    service_id, req_tuple.username,
                                    req_tuple.created_date, parent_query))
                            if str(hist_status) == "1":
                                info_msg = ("History request recorded:" + " " +
                                            str(req_tuple.track_history_code) +
                                            " " + all_data)
                                log_info(info_msg)
                            else:
                                err_msg = "HIST_INSERT_QUERY_PARENT failed" + \
                                    history_data
                                log_errors(err_msg)
                                track_history_errors(history_data)

                    else:
                        history_data = req_tuple.get_history_data()
                        history_code = get_history_code(history_data)
                        info_msg = "History code generated: " + \
                            str(history_code) + " " + all_data
                        log_info(info_msg)
                else:
                    if req_tuple.track_history_code != None:
                        err_msg = ("Track History flag not set but history " +
                                   "code was sent. Please check history " +
                                   "tracking error logs. " +
                                   str(req_tuple.track_history_code))
                        log_errors(err_msg)
                        history_data = str(req_tuple.track_history_code) + ","\
                                     + str(all_data)
                        track_history_errors(history_data)

                cursor.close()

                webstatus = '200 OK'
                if (req_tuple.track_history == "1" and
                    req_tuple.track_history_code == None):
                    data = json.dumps({'result': {'Status': 'Success',
                                      'Details': 'Provenance recorded',
                                      'History code': history_code}},
                                      indent=4)
                elif (req_tuple.track_history == None and
                      req_tuple.track_history_code != None):
                    data = json.dumps({'result': {'Status': 'Success',
                                      'Details': 'Provenance recorded',
                                      'Warning': 'Track history flag is not' +
                                      'set but history code was sent'}},
                                      indent=4)
                else:
                    data = json.dumps({'result': {'Status': 'Success',
                                      'Details': 'Provenance recorded'}},
                                      indent=4)

                return (data, webstatus)

            else:
                cursor.close()
                webstatus = '500 Internal Server Error'
                data = json.dumps({'result': {'Status': 'Failed', 'Details':
                                  'Provenance not recorded', 'Report':
                                  'More than one record found for given ' +
                                  ' UUID. Support has been notified'}},
                                  indent=4)
                err_msg = "Duplicate UUID enery found: " + all_data
                # notify_support
                log_errors(err_msg)
                failed_inserts_audit(all_data)
                return (data, webstatus)

        except Exception as exc:
            err_msg = "EXCEPTION: " + str(exc) + ": " + all_data
            log_exception(err_msg)
            audit_insert = cursor.execute(
                AUDIT_ALL % (req_tuple.uuid, event_id, category_id, service_id,
                            req_tuple.username, req_tuple.proxy_username,
                            req_tuple.event_data, req_tuple.request_ipaddress,
                            req_tuple.created_date))
            if audit_insert != 1:
                failed_inserts_audit(all_data)

            cursor.close()

            webstatus = '500 Internal Server Error'
            data = json.dumps({'result': {'Status': 'Failed', 'Details':
                              'Provenance was not recorded. Audit data ' +
                              'recorded.'}}, indent=4)
            return (data, webstatus)

    else:
        webstatus = '400 Bad Request'
        data = json.dumps({'result': {'Status': 'Failed', 'Details':
                          'Incorrect Service/Category/Event data.'}}, indent=4)
        return (data, webstatus)


def get_date_time():
    """Retrieves the current time in seconds."""
    currenttime = datetime.datetime.now()
    current_in_sec = time.mktime(currenttime.timetuple())

    return int(current_in_sec)


def get_id(name, key, version):
    """Retrieve the identifier for a Service or Event."""
    conn = MySQLdb.connect(host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                           passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME,
                           port=PROV_DB_PORT)
    cursor = conn.cursor()

    if key == "EVENT":
        cursor.execute(QUERY_EVENT_ID % (name))
        results = cursor.fetchone()
    elif key == "SERVICE" and version == "Default":
        cursor.execute(QUERY_SERVICE_ID % (name))
        results = cursor.fetchone()
    elif key == "SERVICE" and version != "Default":
        cursor.execute(QUERY_SERVICE_VERSION_ID % (name, version))
        results = cursor.fetchone()
    else:
        cursor.execute(QUERY_CATEGORY_ID % (name))
        results = cursor.fetchone()

    if results != None:
        id_ = int(results[0])
        cursor.close()
        return id_
    else:
        cursor.close()
        return "EMPTY"


def validate(req_tuple):
    """Determine the provided information from the request is
    acceptable."""
    if (not req_tuple.has_required_arguments()):
        return (False, "uuid/event_name/category_name/service_name/username " +
            "cannot be empty")

    # We failed fast & we know we have values to validate...
    # NOW ROCK THE VALIDATION \m/
    if re.match(UUID_FIELD, req_tuple.uuid) is None:
        details = "uuid value is not in the correct format"
        return (False, details)
    elif re.match(STR_FIELD, req_tuple.service_name) is None:
        details = "service_name value is not in the correct format"
        return (False, details)
    elif re.match(STR_FIELD, req_tuple.category_name) is None:
        details = "category_name value is not in the correct format"
        return (False, details)
    elif re.match(STR_FIELD, req_tuple.event_name) is None:
        details = "event_name value is not in the correct format"
        return (False, details)
    elif re.match(STR_FIELD, req_tuple.username) is None:
        details = "username value is not in the correct format"
        return (False, details)
    elif (req_tuple.proxy_username != None and
          re.match(STR_FIELD, req_tuple.proxy_username) is None):
        details = "proxy_username value is not in the correct format"
        return (False, details)
    elif (req_tuple.version != None and
          re.match(VER_FIELD, req_tuple.version) is None):
        details = "version value is not in the correct format"
        return (False, details)
    else: # the tuple survived the validation gauntlet, give them free passage!
        details = "Validation Passed"
        return (True, details)
