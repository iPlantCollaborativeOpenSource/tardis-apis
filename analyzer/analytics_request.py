#!/usr/bin/python26

import re
import sys
import MySQLdb
from webob import Request
import json

CONFIG_PATH = '/path/to/scripts'

sys.path.append(CONFIG_PATH)
from db_queries import QUERY_HISTORY_PARENT_DATA, QUERY_ALL_HIST_DATA
from configs import (AYLT_DB_HOST, AYLT_DB_USERNAME, AYLT_DB_PASSWORD,
                     AYLT_DB_NAME)
from aylt_logging import log_errors, log_info, log_exception
from query_builder import build_query


def application(environ, start_response):
    """
    WSGI Endpoint for make queries about provenance.
    """
    req = Request(environ)

    if (req.method == 'GET'):
        uuid = req.params.get('uuid')
        service_name = req.params.get('service_name')
        category_name = req.params.get('category_name')
        event_name = req.params.get('event_name')
        username = req.params.get('username')
        proxy_username = req.params.get('proxy_username')
        start_date = req.params.get('start_date')
        end_date = req.params.get('end_date')
        days = req.params.get('days')

        show_history = req.params.get('show_history')
        if show_history == None:
            show_history = 0

        record_limit = req.params.get('record_limit')
        if record_limit == None:
            record_limit = 100

        request_data = "UUID: " + str(uuid) + '\n' + "service_name: " + \
                    str(service_name) + '\n' + "category_name: " + \
                    str(category_name) + '\n' + "event_name: " + \
                    str(event_name) + '\n' + "username: " + str(username) \
                    + '\n' + "proxy_username: " + str(proxy_username) + '\n' \
                    + "start_date: " + str(start_date) + '\n' + "end_date: " \
                     + str(end_date) + '\n' + "days: " + str(days) + '\n' + \
                     "record_limit: " + str(record_limit) + '\n' + \
                     "show_history: " + str(show_history)

        log_info("Request filters: " + '\n', request_data)

        validated, details = checkValidation(uuid, service_name, category_name,
                                        event_name, username, proxy_username,
                                        start_date, end_date)
        if validated == 1:  # SIGH...
            json_data, webstatus = processRequest(uuid, service_name,
                                        category_name, event_name, username,
                                        proxy_username, start_date, end_date,
                                        days, record_limit, show_history)
        elif validated == "EMPTY":
            json_data = json.dumps({'result': {'Status': 'Validation failed',
                                    'Report':details}}, indent=4)
            webstatus = '405 Method Not Allowed'
        else:
            json_data = json.dumps({'result': {'Status': 'Validation failed',
                                    'Report':details}}, indent=4)
            webstatus = '404 Not Found'

    else:
        webstatus = '405 Method Not Allowed'
        json_data = json.dumps({'result': {'Status': 'Failed',
                                'Details':'Incorrect HTTP METHOD'}}, indent=4)

    response_headers = [('Content-type', 'application/json')]
    start_response(webstatus, response_headers)
    return (json_data)


def processRequest(uuid, service_name, category_name, event_name, username,
                   proxy_username, start_date, end_date, days, record_limit,
                   show_history):

    (query_statement, query_values) = build_query(uuid, service_name,
                                        category_name, event_name, username,
                                        proxy_username, start_date, end_date,
                                        days, record_limit)

    log_info("SQL Query: ", str(query_statement))
    log_info("SQL Query Values: ", str(query_values))

    try:

        conn = MySQLdb.connect(host=AYLT_DB_HOST, user=AYLT_DB_USERNAME,
                               passwd=AYLT_DB_PASSWORD, db=AYLT_DB_NAME)
        cursor = conn.cursor()

        cursor.execute(query_statement, tuple(query_values))

        if record_limit == "all":
            results = cursor.fetchall()
        else:
            results = cursor.fetchmany(size=int(record_limit))

        if (len(results) > 0):
            alldata = "{'result':{'status':'Success','records':["
            for row in results:
                id_ = int(row[0])
                uuid = int(row[1])
                username = str(row[2])
                proxy_username = str(row[3])
                event_data = str(row[4])
                request_ipaddress = str(row[5])
                created_date = str(row[6])
                event_name = str(row[7])
                service_name = str(row[8])
                service_link = str(row[9])
                service_ipaddress = str(row[10])
                service_group = str(row[11])
                service_type = str(row[12])
                service_version = str(row[13])
                version_status = str(row[14])
                if version_status == "A":
                    version_status = "Active"
                else:
                    version_status = "Inactive"

                category_name = str(row[15])
                service_object_id = str(row[16])
                object_name = str(row[17])
                object_desc = str(row[18])
                parent_uuid = str(row[19])

                alldata += "{'UUID':'"+ str(uuid)+ "','Username':'" + username \
                           + "','Proxy username':'" + proxy_username + \
                           "','Event data':'" + event_data + \
                           "','Request IP address':'" + request_ipaddress + \
                           "','Event name':'" + event_name + \
                           "','Service name':'" + service_name + \
                           "','Service link':'" + service_link + \
                           "','Service IP address':'" + service_ipaddress + \
                           "','Service Group':'" + service_group + \
                           "','Category name':'" + category_name + \
                           "','Service Object ID':'" + service_object_id + \
                           "','Object Name':'" + object_name + \
                           "','Object Description':'" + object_desc + \
                           "','Parent UUID':'" + parent_uuid + \
                           "','Created Date':'" + created_date + \
                           "','Service Type':'" + service_type + \
                           "','Service Version':'" + service_version + \
                           "','Version Status':'" + version_status + "'},"

                if show_history == 1:
                    cursor.execute(QUERY_HISTORY_PARENT_DATA % (id_))
                    histresults = cursor.fetchall()

                    ph_data = "{'History':{'status':'Success','records':["

                    if (len(histresults) > 0):

                        for hrow in histresults:
                            provenance_parent_id = hrow[0]

                            cursor.execute(QUERY_ALL_HIST_DATA %
                                            (provenance_parent_id))
                            phresults = cursor.fetchall()

                            if (len(phresults) > 0):

                                for pphrow in phresults:

                                    ph_uuid = pphrow[1]
                                    ph_username = pphrow[2]
                                    ph_proxy_username = pphrow[3]
                                    ph_event_data = pphrow[4]
                                    ph_request_ipaddress = pphrow[5]
# UNUSED =>                         ph_created_date = pphrow[6]
                                    ph_event_name = pphrow[7]
                                    ph_service_name = pphrow[8]
                                    ph_service_link = pphrow[9]
                                    ph_service_ipaddress = pphrow[10]
                                    ph_service_group = pphrow[11]
                                    ph_category_name = pphrow[12]
                                    ph_service_object_id = pphrow[13]
                                    ph_object_name = pphrow[14]
                                    ph_object_desc = pphrow[15]
                                    ph_parent_uuid = pphrow[16]
# TODO - make this a string template or something
                                    ph_data += ("{'UUID':'" + ph_uuid+
                                        "','Username':'"+ ph_username +
                                        "','Proxy username':'" +
                                        ph_proxy_username +
                                        "','Event data':'"+ ph_event_data
                                        + "','Request IP address':'"+
                                        ph_request_ipaddress +
                                        "','Event name':'" + ph_event_name +
                                        "','Service name':'"+ ph_service_name +
                                        "','Service link':'" + ph_service_link +
                                        "','Service IP address':'" +
                                        ph_service_ipaddress +
                                        "','Service Group':'" +
                                        ph_service_group +
                                        "','Category name':'" +
                                        ph_category_name +
                                        "','Service Object ID':'" +
                                        ph_service_object_id +
                                        "','Object Name':'" +
                                        ph_object_name +
                                        "','Object Description':'" +
                                        ph_object_desc +
                                        "','Parent UUID':'" +
                                        ph_parent_uuid +
                                        "','Service Type':'" +
                                        service_type +  "','Service Version':'"
                                        + service_version +
                                        "','Version Status':'" +
                                        version_status+"'},")
# This is heinous and should really bother people---^

                                ph_data = ph_data.strip(",")
                                ph_data += "]}}"

                            else:
                                err_msg = "History Recorded but Provenance " + \
                                    "row doesn't exist" + " " + "[" + id + "]"
                                log_errors(err_msg)
                                ph_data = "{'Null'},"
                                # notify Support

                        ph_data = ph_data.strip(",")
                        ph_data += "]}}"

                    else:
                        ph_data = "{'No Records in History Table'}"
                        ph_data += "]}}"

                    alldata = alldata.strip(",")
                    alldata += ph_data
                    alldata += "]}}"
                    json_data = json.dumps(eval(alldata), indent=4)
                    info_msg = "Analytics + History: Success!"
                    log_info(info_msg, json_data)
                    cursor.close()
                    webstatus = '200 OK'
                    return (json_data, webstatus)

            alldata = alldata.strip(",")
            alldata += "]}}"
            json_data = json.dumps(eval(alldata), indent=4)
            info_msg = "Analytics: Success "
            log_info(info_msg, json_data)
            cursor.close()
            webstatus = '200 OK'
            return (json_data, webstatus)

        else:
            json_data = json.dumps({'result': {'Status': 'Success',
                                    'Details':'No records found'}}, indent=4)
            info_msg = "Analytics: Success! "
            log_info(info_msg, json_data)
            cursor.close()
            webstatus = '200 OK'
            return (json_data, webstatus)

    except Exception as exc:
        err_msg = "EXCEPTION: " + str(exc)
        log_exception(err_msg)

        webstatus = '400 Bad Request'
        json_data = json.dumps({'result': {'Status': 'Failed', 'Details':
                                'Analytics call failed'}}, indent=4)
        return (json_data, webstatus)


def checkValidation(uuid, service_name, category_name, event_name, username,
                    proxy_username, start_date, end_date):

    try:
        queryvals = {}
        queryvals['uuid'] = uuid
        queryvals['service_name'] = service_name
        queryvals['event_name'] = event_name
        queryvals['category_name'] = category_name
        queryvals['username'] = username
        queryvals['proxy_username'] = proxy_username
        queryvals['start_date'] = start_date
        queryvals['end_date'] = end_date

        details = "{"

        for name, values in queryvals.iteritems():
            if values != None:
                if name == "uuid":
                    if re.match(r'^[0-9]+$', values) != None:
                        continue
                    else:
                        details += "'" + str(name) + "':'Failed',"
                elif name == "start_date" or name == "end_date":
                    if re.match(r'(\d{4})[-](\d{2})[-](\d{2})$',
                                values) != None:
                        continue
                    else:
                        details += "'" + str(name) + "':'Failed',"
                elif name == "username" or name == "proxy_username":

                    if re.match(r'^[A-Za-z0-9\-_]+$', values) != None:
                        continue
                    else:
                        details += "'" + str(name) + "':'Failed',"
                else:
                    if re.match(r'^[A-Za-z0-9\-_]+$', values) != None:
                        continue
                    else:
                        details += "'" + str(name) + "':'Failed',"
            else:  # /boggle - if we're at the end of the loop, what
                  # does this do?
                continue

        details = details.strip(",")
        details += "}"

        if "Failed" in details:
            returnval = 0
        else:
            returnval = 1

        info_msg = "Validation: Completed"
        val_det = "Status: " + str(returnval) + " Details:  " + str(details)
        log_info(info_msg, val_det)

        json_det = json.dumps(details)
        json_det = json_det.replace('\"', '')
        return (returnval, json_det)

    except Exception, e:
        returnval = "EMPTY"
        info_msg = "Validation: Failed"
        val_det = "Details: No filter was specified. " + str(e)
        log_info(info_msg, val_det)
        json_det = json.dumps({'result': {'Status': 'Validation Failed',
                               'Details':val_det}}, indent=4)
        return (returnval, json_det)