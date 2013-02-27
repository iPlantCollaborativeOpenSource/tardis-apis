#!/usr/bin/python

OBJECT_QUERY_UUID_LOOKUP = "SELECT uuid FROM Object WHERE service_object_id='%s'"
OBJECT_QUERY_UUID_INSERT = "INSERT INTO Object(uuid,service_object_id,object_name,object_desc) VALUES('%s', '%s', '%s', '%s')"


QUERY_NO_PROXY_DATA = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_PROXY = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_DATA = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_ALL = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"


QUERY_EVENT_ID = "SELECT event_id FROM Event WHERE event_name='%s'"
QUERY_CATEGORY_ID = "SELECT category_id FROM Category WHERE category_name='%s'"
QUERY_SERVICE_ID = "SELECT service_id FROM Service WHERE service_name='%s'" 

