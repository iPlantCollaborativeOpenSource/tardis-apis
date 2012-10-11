tardis-collector
================

Tracking and Retreiving Data Interface Service, iPlant's provenance collector API


Collector API version 1.2

This section describes the installation steps for the Collector API. 

Pre-requisites

Python 2.6
Python modules: Webob, MySQLdb
python26-mod_wsgi 3.3
MySQL 5.0.95
Snowflake and its dependencies

Installation Steps

1. Download the Collector API code from github.

Make sure the following files exist in the repo:

provenance-agent.py: This script performs the validation and logs the provenance (end point for /provenance call)
object_lookup.py: This script does the looks up the uuid of an object based on the service_object_id input (end point for /lookup call)
object_reg_lookup,py: This script registers the object and generates a unique uuid for an object (end point for /register call)
db_queries.py: This script has the SQL queries
config.py: This is the configuration file
prov_logging.py: This script handles the logging
scriptTracking.py: This script handles additional functions for history tracking and notifications
audit-script.py: This script processes provenance requests that failed the first time
create_database.sql: This file can be used to create the collector API database

NOTE: The default installation path is "/collector-scripts. Please modify config.py and CONFIG_PATH (specified in the python scripts), if you are using a different location.

2. Update CONFIG_PATH value with your /path/to/scripts in the following script files:

object_lookup.py
scriptTracking.py
object_reg_lookup.py
provenance-agent.py
audit-script.py


3. Execute create_database.sql to setup the Collector API database ("provenance") 

This script comes with a "CREATE DATABASE" command. The default database name used is provenance.

$ mysql -u root -p<root-password> < create_database.sql

4. Create database user and give all privileges to that user on the above database.

mysql> CREATE USER '<username>' identified by '<password>';
mysql> GRANT ALL PRIVILEGES ON <database_name>.* TO '<username>'@'%' identified by '<password>';

5. Modify the config.py

# Provenance Database
 
PROV_DB_HOST = "localhost"
PROV_DB_USERNAME = "username"
PROV_DB_PASSWORD = "password"
PROV_DB_NAME = "database"
 
# Audit files
 
OBJECT_FAILED_INSERTS_FILE = "/path/to/audit/failed/objects/inserts/file"
PROV_FAILED_INSERTS_FILE = "/path/to/provenance/audit/failed/inserts/file"
HISTORY_INSERT_FILE ="/path/to/provenance/history/insert/file"
 
# Log Files
 
PROV_LOGFILE = "/path/to/provenance/log/file"
OBJECT_LOOKUP_LOGFILE = "/path/to/object/lookup/log/file"
HISTORY_TRACKING_LOGFILE = "/path/to/history/tracking/log/file"
 
 
# Support Mail
 
MAIL_FROM = "Specify an email address"
MAIL_TO = "Specify an email addresss"

6. Edit the wsgi.conf under /etc/httpd/conf.d/

<VirtualHost *:80>
 
ServerName server-name
 
WSGIDaemonProcess wsgi processes=3 threads=4 display-name="wsgi-process" python-eggs="/tmp/trac-eggs"
WSGIProcessGroup wsgi
 
RewriteEngine on
RewriteRule ^/provenance/<version-number>/([\w]+)/([a-zA-Z]+)/([\w]+)$ /provenance/<version-number>?uuid=$1&username=$2&service_name=$3&event_name=$4&category_name=$5 [P,L]
RewriteRule ^/register/<version-number>/([\w]+)/([a-zA-Z]+)/([\w]+)$ /register/<version-number>?service_object_id=$1&object_name=$2 [P,L]
RewriteLog "/path/to/provenance/log"
RewriteLogLevel 5
 
WSGIScriptAlias /register/<version-number> /path/to/scripts/object_reg_lookup.py
 
<Directory /path/to/scripts>
  Order allow,deny
  Allow from <ip-address>
</Directory>
 
<Directory /etc/httpd/logs>
  Order allow,deny
  Allow from all
</Directory>
 
WSGIScriptAlias /provenance/<version-number> /path/to/scripts/provenance-agent.py
 
<Directory /path/to/scripts>
  Order allow,deny
  Allow from <ip-address>
</Directory>
 
<Directory /etc/httpd/logs>
  Order allow,deny
  Allow from all
</Directory>
 
WSGIScriptAlias /lookup/<version-number> /path/to/scripts/object_lookup.py
 
<Directory /path/to/scripts>
  Order allow,deny
  Allow from <ip-address>
</Directory>
 
<Directory /etc/httpd/logs>
  Order allow,deny
  Allow from all
</Directory>
 
 
</VirtualHost>

7. Restart httpd and open port 80 in iptables
