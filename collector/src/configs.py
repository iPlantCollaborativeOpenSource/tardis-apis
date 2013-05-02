#!/usr/bin/python26

# URL Prefix
ENDPT_PREFIX = "/dev"

# Provenance Database
PROV_DB_HOST = "localhost"
PROV_DB_USERNAME = "root"
PROV_DB_PASSWORD = "WHOdoctorR4hrMD"
PROV_DB_NAME = "provenance"
PROV_DB_PORT = 3306

# Snowflake Settings
SNOWFLAKE_HOST = "vm142-89.iplantc.org"
SNOWFLAKE_PORT = 31376
# Identifies the system calling out to Snowflake - see client for details...
SNOWFLAKE_AGENT = "tardis-collector-api"

# Audit files
OBJECT_FAILED_INSERTS_FILE = "/provenance-logs/audit/object_failed_inserts.txt"
PROV_FAILED_INSERTS_FILE = "/provenance-logs/audit/prov_failed_inserts.txt"
HISTORY_INSERT_FILE = "/provenance-logs/history/history_insert_file.txt"

# Log Files
PROV_LOGFILE = "/provenance-logs/" + ENDPT_PREFIX + "/provenance.log"
OBJECT_LOOKUP_LOGFILE = "/provenance-logs/" + ENDPT_PREFIX + \
                        "/Object-lookup.log"
HISTORY_TRACKING_LOGFILE = "/provenance-logs/"+ ENDPT_PREFIX + \
                           "/history/history_tracking.log"

# Support Mail
MAIL_FROM = ""
MAIL_TO = ""