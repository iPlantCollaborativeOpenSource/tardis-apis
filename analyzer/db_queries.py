#!/usr/bin/python2.6


QUERY_ALL_DATA = "SELECT * FROM Analytics WHERE created_date BETWEEN '%s' AND '%s' LIMIT '%s'"
QUERY_HISTORY_PARENT_DATA = "SELECT provenance_parent_id from History where provenance_id='%s'"
QUERY_ALL_HIST_DATA = "SELECT * FROM Analytics LIMIT '%s'"

SELECT_QUERY = "SELECT * FROM Analytics WHERE username='%s'"
