#!/usr/bin/python2.6

#  Copyright (c) 2011, The Arizona Board of Regents on behalf of
#  The University of Arizona
#
#  All rights reserved.
#
#  Developed by: iPlant Collaborative as a collaboration between
#  participants at BIO5 at The University of Arizona (the primary hosting
#  institution), Cold Spring Harbor Laboratory, The University of Texas at
#  Austin, and individual contributors. Find out more at
#  http://www.iplantcollaborative.org/.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the iPlant Collaborative, BIO5, The University
#   of Arizona, Cold Spring Harbor Laboratory, The University of Texas at
#   Austin, nor the names of other contributors may be used to endorse or
#   promote products derived from this software without specific prior
#   written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# Author: Sangeeta Kuchimanchi (sangeeta@iplantcollaborative.org)
# Date: 10/11/2012
#


import sys
import datetime
import MySQLdb
from webob import Request
import json
import uuid
# from thrift.transport import TTransport
# from thrift.transport import TSocket
# from thrift.transport import THttpClient
# from thrift.protocol import TBinaryProtocol
# from genpy.Snowflake import Snowflake
# from genpy.Snowflake import ttypes
# from genpy.Snowflake import constants

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)
from db_queries import (OBJECT_QUERY_UUID_INSERT, OBJECT_QUERY_UUID_LOOKUP)
from configs import (OBJECT_FAILED_INSERTS_FILE, PROV_DB_HOST, PROV_DB_NAME,
                    PROV_DB_USERNAME, PROV_DB_PASSWORD)
from prov_logging import log_errors, log_exception, log_info

# File under: things I'm thinking about on Saturday Night...
# the registration should be scoped to the service-id, right?
# consider this:
#  - Atmosphere registers an object with ``service_object_id`` of 16
#  - The DE tries to register an object with the same id, 16, and gets
#    back the UUID associated with the Atmosphere object
#
# is this "interning" of objects expected?
#
# I don't think this can be correct because the associated object_name
# and object_desc will be that of the Atmosphere request/call and not
# that of the DE call which means that when the object is looked up &
# displayed in the DE history, it'll be wrong.
def application(environ, start_response):
    """Endpoint for easy registration of provenance objects.

    It will perform the lookup, if the object does not exists, it will
    register the object return the UUID value.

    Call returns UUID if the object is found else, returns 404 NOT FOUND
    is the status code for the response.

    Query String parameters:
    ``service_object_id`` - object identifier (used as primary key)
    ``object_name`` - name of the object
    ``object_desc`` - description of the object

    Note: if the object exists, the parameters ``object_name`` and
    ``object_desc`` are ignored and the existing UUID is returned.
    """
    req = Request(environ)
    if (req.method == 'POST'):
        data_string, webstatus = _handle_post(req)

    else:
        data_string = json.dumps({'Status': 'Failed', 'Details':
                                 'Incorrect HTTP METHOD'}, indent=4)
        webstatus = '405 Method Not Allowed'

    response_headers = [('Content-type', 'application/json')]
    start_response(webstatus, response_headers)
    return (data_string)


def _handle_post(req):
    """Helper method that handles HTTP POST calls to the endpoint."""
    objid = req.params.get('service_object_id')
    objname = req.params.get('object_name')
    objdesc = req.params.get('object_desc')

    obj_data = "[" + str(objid) + "," + str(objname) + "," + \
        str(objdesc) + "]"

    if objid != None:
        data_string, webstatus = _register_obj(objid, objname, objdesc,
                                                obj_data)

    else:
        err_msg = "Null Exception: service_object_id cannot be null " + \
            obj_data
        log_exception(err_msg)

        data_string = json.dumps(
            {'Status': 'Failed', 'Details': 'Null Exception. ' +
             'service_object_id cannot be null'}, indent=4)
        webstatus = '500 Internal Server Error'

    return data_string, webstatus


def _register_obj(objid, objname, objdesc, obj_data):
    """Handles registration of the given object information."""
    try:
        conn = MySQLdb.connect(
            host=PROV_DB_HOST, user=PROV_DB_USERNAME,
            passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME)
        cursor = conn.cursor()
        log_info(OBJECT_QUERY_UUID_LOOKUP % (objid))
        cursor.execute(OBJECT_QUERY_UUID_LOOKUP % (objid))
        results = cursor.fetchone()
        log_info(results)

        if results is None:
            uuid_ = get_uuid(obj_data)
            log_info(uuid_)

            if uuid_ == None:
                log_errors("Objuuid is null: " + obj_data)
                failed_inserts_audit(obj_data)
                data_string = json.dumps({'Status': 'Failed',
                                         'Details':
                                         'Error retrieving UUID'},
                                         indent=4)
                webstatus = '503 Service Unavailable'
            else:
                log_info(OBJECT_QUERY_UUID_INSERT % (uuid_, objid,
                                                     objname,
                                                     objdesc))
                cursor.execute(
                    OBJECT_QUERY_UUID_INSERT % (uuid_, objid, objname,
                                                objdesc))
                uid = str(uuid_)
                info_msg = "Object created: " + " " + uid
                log_info(info_msg)
                data_string = json.dumps({'UUID': uid}, indent=4)
                webstatus = '200 OK'

        else:
            for value in results:
                info_msg = "Lookup: Object Exists" + " " + str(value)
                log_info(info_msg)
                data_string = json.dumps({'UUID': str(value)})
                webstatus = '200 OK'
        cursor.close()

    except Exception, e:
        err_msg = "MySQL DB Exception: " + " " + \
            str(e) + " " + obj_data
        log_exception(err_msg)
        failed_inserts_audit(obj_data)

        data_string = json.dumps({'Status': 'Failed',
                                  'Details': 'MySQL Exception. Failed' +
                                  'to retrieve data'}, indent=4)
        webstatus = '500 Internal Server Error'

    return data_string, webstatus


def get_uuid(obj_data):
    """Generate and return a universal unique identifier (UUID).

    In development mode, this UUID may be generated w/ Python's ``uuid``
    module.

    In production mode, the UUID should be generated by ``Snowflake``, a
    component created by Twitter for creating robust identifiers quickly.
    """
    # generate a 128 bit integer and shift it 66 places to create an
    # 18 digit  UUID
    return int(uuid.uuid1()) >> 66

    # host = 'localhost'
    # port = 7610

    # try:
    #   socket = TSocket.TSocket(host, port)
    #   transport = TTransport.TFramedTransport(socket)
    #   protocol = TBinaryProtocol.TBinaryProtocol(transport)
    #   client = Snowflake.Client(protocol)
    #   trans_out = transport.open()

    #   timestmp = client.get_timestamp()
    #   id = client.get_id("provenanceAPI")

    #   snflake_data = "[" + str(socket) + "," + str(transport) + "," +
    #                   str(protocol) + "," + str(client) + "," + str(trans_out)
    #                   + "," + str(timestmp) + "," + str(id) + "]"
    #   info_msg = snflake_data + " " + obj_data
    #   log_info(info_msg)

    #   return id
    # except Exception, e:
    #   err_msg = "Snowflake Server exception: " + str(e) + " " + obj_data
    #   log_exception(err_msg)
    #   failedInsertsAudit(obj_data)


def failedInsertsAudit(data):
    curr_time = datetime.datetime.now()
    insertfile = open(OBJECT_FAILED_INSERTS_FILE, "a")
    insertfile.write(str(curr_time) + " " + data + "\n")
    insertfile.close()
