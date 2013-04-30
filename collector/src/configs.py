#!/usr/bin/python26

# URL Prefix

ENDPT_PREFIX = "/dev"

# Provenance Database

PROV_DB_HOST = "localhost"
PROV_DB_USERNAME = ""
PROV_DB_PASSWORD = ""
PROV_DB_NAME = "provenance"
PROV_DB_PORT = 3306

# Audit files
OBJECT_FAILED_INSERTS_FILE = "/provenance-logs/audit/object_failed_inserts.txt"
PROV_FAILED_INSERTS_FILE = "/provenance-logs/audit/prov_failed_inserts.txt"
HISTORY_INSERT_FILE = "/provenance-logs/history/history_insert_file.txt"

# Log Files

PROV_LOGFILE = "/provenance-logs/v1.3/provenance.log"
OBJECT_LOOKUP_LOGFILE = "/provenance-logs/v1.3/Object-lookup.log"
HISTORY_TRACKING_LOGFILE = "/provenance-logs/v1.3/history/history_tracking.log"


# Support Mail

MAIL_FROM = ""
MAIL_TO = ""
