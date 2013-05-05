"""
Configuration settings for the overall application.
"""

# URL Prefix
ENDPT_PREFIX = "/dev"

# Provenance Database
PROV_DB_HOST = "localhost"
PROV_DB_USERNAME = ""
PROV_DB_PASSWORD = ""
PROV_DB_NAME = "provenance"
PROV_DB_PORT = 3306

# Snowflake Settings
SNOWFLAKE_HOST = "vm142-89.iplantc.org"
SNOWFLAKE_PORT = 31376
# Identifies the system calling out to Snowflake - see client for details...
SNOWFLAKE_AGENT = "tardis-collector-api"

# Basedirectory for audit & log files
BASE_LOG_DIR = "/provenance-logs" + ENDPT_PREFIX

# Audit files
OBJECT_FAILED_INSERTS_FILE = BASE_LOG_DIR + "/audit/object_failed_inserts.txt"
PROV_FAILED_INSERTS_FILE = BASE_LOG_DIR + "/audit/prov_failed_inserts.txt"
HISTORY_INSERT_FILE = BASE_LOG_DIR + "/history/history_insert_file.txt"

# Log Files
PROV_LOGFILE = BASE_LOG_DIR + "/provenance.log"
OBJECT_LOOKUP_LOGFILE = BASE_LOG_DIR + "/Object-lookup.log"
HISTORY_TRACKING_LOGFILE = BASE_LOG_DIR + "/history/history_tracking.log"

# Support Mail
MAIL_FROM = ""
MAIL_TO = ""