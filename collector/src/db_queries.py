#!/usr/bin/python26

# See LICENSE file in repository

OBJECT_QUERY_UUID_LOOKUP = "SELECT uuid FROM Object WHERE service_object_id='%s'"
OBJECT_QUERY_UUID_INSERT = "INSERT INTO Object(uuid,service_object_id,object_name,object_desc) VALUES('%s', '%s', '%s', '%s')"
OBJECT_QUERY_UUID_INSERT_PARENT = "INSERT INTO Object(uuid,service_object_id,object_name,object_desc,parent_uuid) VALUES('%s', '%s', '%s', '%s', '%s')"

QUERY_NO_PROXY_DATA = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_PROXY = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_DATA = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
QUERY_ALL = "INSERT INTO Provenance(uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"


QUERY_EVENT_ID = "SELECT event_id FROM Event WHERE event_name='%s'"
QUERY_EVENT_VERSION_ID = "SELECT event_id FROM Event WHERE event_name='%s' and version='%s'"
QUERY_CATEGORY_ID = "SELECT category_id FROM Category WHERE category_name='%s'"
QUERY_SERVICE_ID = "SELECT service_id FROM Service WHERE service_name='%s'"
QUERY_SERVICE_VERSION_ID = "SELECT service_id FROM Service WHERE service_name='%s' and version='%s'"
QUERY_CHECK_UUID = "SELECT * FROM Object WHERE uuid='%s'"

HIST_SELECT_QUERY = "SELECT id FROM history_requests WHERE history_code ='%s'"
HIST_INSERT_QUERY = "INSERT INTO history_requests(history_code,uuid,event_id,category_id,service_id,username,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
HIST_INSERT_QUERY_PARENT = "INSERT INTO history_requests(history_code,uuid,event_id,category_id,service_id,username,created_date,parent) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"


# History Script

PARENT_HIST_SELECT_QUERY = "SELECT * FROM history_requests WHERE parent = '%s' AND processed = '%s'"
PROV_HIST_SELECT_ID = "SELECT provenance_id FROM Provenance WHERE uuid = '%s' AND event_id = '%s' AND category_id = '%s' AND service_id = '%s' AND username = '%s' AND created_date = '%s'"
CHILD_HIST_SELECT_QUERY = "SELECT * FROM history_requests WHERE history_code = '%s' and processed ='%s' AND parent = '%s'"

PROV_HIST_INSERT_ID = "INSERT INTO History(provenance_id,provenance_parent_id) VALUES('%s','%s')"
PROV_HIST_UPDATE_STATUS = "UPDATE history_requests SET processed='%s' WHERE id='%s'"

# Audit Queries

AUDIT_NO_PROXY_DATA = "INSERT INTO Audit(uuid,event_id,category_id,service_id,username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
AUDIT_PROXY = "INSERT INTO Audit(uuid,event_id,category_id,service_id,username,proxy_username,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
AUDIT_DATA = "INSERT INTO Audit(uuid,event_id,category_id,service_id,username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
AUDIT_ALL = "INSERT INTO Audit(uuid,event_id,category_id,service_id,username,proxy_username,event_data,request_ipaddress,created_date) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
AUDIT_SELECT = "SELECT * FROM Audit WHERE processed='%s'"
AUDIT_UPDATE_STATUS = "UPDATE Audit SET processed='%s' WHERE id='%s'"
