#!/usr/bin/python

"""
Designed to run periodically, via a scheduler like crontab, this script
creates and inserts history records for provenance objects that have
request ``history tracking``.
"""

import sys
import MySQLdb

CONFIG_PATH = '/scripts'

sys.path.append(CONFIG_PATH)

from db_queries import (PROV_HIST_SELECT_ID, PROV_HIST_INSERT_ID,
                        CHILD_HIST_SELECT_QUERY, PARENT_HIST_SELECT_QUERY,
                        PROV_HIST_UPDATE_STATUS)
from configs import (PROV_DB_HOST, PROV_DB_NAME, PROV_DB_USERNAME,
                     PROV_DB_PASSWORD, PROV_DB_PORT)
from script_tracking import (notify_support, track_history_errors,
                            track_history_exceptions, track_history_info)

# might as well define this as a global
SCRIPTNAME = "History"

def _process_single_parent_results(cursor, parent_id, parent_history_code,
                                    parent_id_results):
    """Private method for processing child results for parent records
    that only have a single result. """
    p_id = parent_id
    p_history_code = parent_history_code
    p_id_results = parent_id_results
    p_provenance_id = int(p_id_results[0][0])
    child_hist = cursor.execute(CHILD_HIST_SELECT_QUERY %
                                (p_history_code, 'N', 'N'))
    c_results = cursor.fetchall()

    for child in c_results:
        c_id = int(child[0])
        c_uuid = int(child[2])
        c_service_id = int(child[3])
        c_category_id = int(child[4])
        c_event_id = int(child[5])
        c_username = str(child[6])
        c_createdate = int(child[7])

        c_histid_status = cursor.execute(PROV_HIST_SELECT_ID %
                                        (c_uuid, c_event_id,
                                        c_category_id,
                                        c_service_id, c_username,
                                        c_createdate))
        c_id_results = cursor.fetchall()

        if len(c_id_results) == 1:
            c_provenance_id = int(c_id_results[0][0])
            c_histid_status = cursor.execute(PROV_HIST_INSERT_ID %
                                            (c_provenance_id,
                                            p_provenance_id))
            if c_histid_status == 1:
                c_process_status = cursor.execute(
                                        PROV_HIST_UPDATE_STATUS
                                        % ('Y', c_id))
                if c_process_status == 1:
                    info_msg = ("Child row updated: [" +
                                "parent_provenance_id, " +
                                "child_provenance_id]:" +
                                "[" + str(p_id) + "," + str(c_id) +
                                "]")
                    track_history_info(info_msg)
                else:
                    err_msg = ("Failed to update child row " +
                                "status: [parent_provenance_id, " +
                                "child_provenance_id]:" + "[" +
                                str(p_id) + "," + str(c_id) + "]")
                    track_history_errors(err_msg)
                    notify_support(err_msg, SCRIPTNAME)
            else:
                err_msg = ("Failed History Recording, at child row"
                         + " [parent_provenance_id, " +
                         "child_provenance_id]:" + "[" + str(p_id)
                         + "," + str(c_id) + "]")
                track_history_errors(err_msg)
                notify_support(err_msg, SCRIPTNAME)
        else:
            err_msg = ("Error in retrieving child row from " +
                        "provenance table, multiple entries or " +
                        "no entry found. [parent_provenance_id, " +
                        "child_provenance_id]: [" + str(p_id) +
                        "," + str(c_id) + "]")
            track_history_errors(err_msg)
            notify_support(err_msg, SCRIPTNAME)

        p_process_status = cursor.execute(PROV_HIST_UPDATE_STATUS %
                                            ('Y', p_id))
        if p_process_status == 1:
            info_msg = ("History Recorded: [parent_provenance_id]:"
                        + "[" + str(p_id) + "]")
            track_history_info(info_msg)
        else:
            err_msg = ("Failed updating parent row status:" +
                        "[parent_provenance_id, " +
                        "child_provenance_id]:" + "[" + str(p_id) +
                        "," + str(c_id) + "]")
            track_history_errors(err_msg)
            notify_support(err_msg, SCRIPTNAME)


def insert_history():
    """Handles inserting history records for provenance objects."""
    try:
        conn = MySQLdb.connect(host=PROV_DB_HOST, user=PROV_DB_USERNAME,
                               passwd=PROV_DB_PASSWORD, db=PROV_DB_NAME,
                               port=PROV_DB_PORT)
        cursor = conn.cursor()
    except:
        err_msg = "Connection failed to Provenance database."
        track_history_exceptions(err_msg)
        notify_support(err_msg, SCRIPTNAME)

    try:

        cursor.execute(PARENT_HIST_SELECT_QUERY % ('Y', 'N'))
        p_results = cursor.fetchall()

        if len(p_results) != 0:

            for parent in p_results:

                p_id = int(parent[0])
                p_history_code = str(parent[1])
                p_uuid = int(parent[2])
                p_service_id = int(parent[3])
                p_category_id = int(parent[4])
                p_event_id = int(parent[5])
                p_username = str(parent[6])
                p_createdate = int(parent[7])

                proc_return = cursor.execute(PROV_HIST_SELECT_ID % (p_uuid,
                                            p_event_id, p_category_id,
                                            p_service_id, p_username,
                                            p_createdate))
                p_id_results = cursor.fetchall()

                # parent ID results contain only 1 result record
                if len(p_id_results) == 1:
                    _process_single_parent_results(cursor, p_id,
                                                    p_history_code,
                                                    p_id_results)

                # parent ID results greater than 1 result record
                elif len(p_id_results) > 1:
                    err_msg = ("Multiple entries found for parent row. " +
                                "[parent_provenance_id]:" + "[" + str(p_id) +
                                "]")
                    track_history_exceptions(err_msg)
                    notify_support(err_msg, SCRIPTNAME)

                else:
                    err_msg = ("No entry found for parent row, but history " +
                                "tracking flag enabled. [parent_provenance_id,"
                                + "]:" + "[" + str(p_id) + "]")
                    track_history_exceptions(err_msg)
                    notify_support(err_msg, SCRIPTNAME)
        # finish up and close our cursor
        cursor.close()

    except Exception, exc:
        err_msg = ("Exception occured after establishing DB connection: " +
                    str(exc))
        track_history_exceptions(err_msg)
        notify_support(err_msg, SCRIPTNAME)
        cursor.close()


def main():
    """Script entry point."""
    try:
        insert_history()
    except:
        err_msg = "insert_history() was not initialized"
        notify_support(err_msg, "History")


if __name__ == "__main__":
    main()

