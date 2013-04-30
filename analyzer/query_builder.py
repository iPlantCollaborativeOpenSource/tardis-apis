#!/usr/bin/python26

"""
Uses to build up queries...

This should be replaced by your favorite framework... SQL Alchemy, Flask,
Django ORM, Pyramids.
"""

import datetime
import time
from datetime import date

def build_query(uuid, service_name, category_name, event_name, username,
               proxy_username, start_date, end_date, days, record_limit):
    """Builds a query with string concatenation."""
    userdict = {}
    datedict = {}
    parameters = []

    if username != None:
        userdict["username"] = username

    if proxy_username != None:
        userdict["proxy_username"] = proxy_username

    if event_name != None:
        userdict["event_name"] = event_name

    if category_name != None:
        userdict["category_name"] = category_name

    if service_name != None:
        userdict["service_name"] = service_name

    if uuid != None:
        userdict["uuid"] = uuid

    if start_date != None and end_date != None:
        st_date = time.strptime(start_date, "%Y-%m-%d")
        ed_date = time.strptime(end_date, "%Y-%m-%d")

        if st_date < ed_date:
            sdate = int(time.mktime(st_date))
            edate = int(time.mktime(ed_date))
        else:
            sdate = int(time.mktime(ed_date))
            edate = int(time.mktime(st_date))

        datedict["start_date"] = sdate
        datedict["end_date"] = edate

    elif start_date == None and end_date == None and days != None:
        date_range = get_date_range(days)
        sdate = int(date_range[0])
        edate = int(date_range[1])

        datedict["start_date"] = sdate
        datedict["end_date"] = edate

    else:
        days = 8
        date_range = get_date_range(days)
        sdate = int(date_range[0])
        edate = int(date_range[1])

        datedict["start_date"] = sdate
        datedict["end_date"] = edate

    select_stmt = "SELECT * FROM Analytics WHERE "

    for filter_, value in userdict.iteritems():
        select_stmt += filter_ + "=" + "%s" + " AND "
        parameters.append(str(value))

    select_stmt += "created_date BETWEEN %s AND %s"
    for _, cre_vals in datedict.iteritems():
        parameters.append(str(cre_vals))

    select_stmt += "]"
    select_stmt = select_stmt.strip("AND ]")

    return (select_stmt, parameters)


def get_date_range(days_value):
    """Provides a date range tuple."""
    # TODO look for a module that does this - there has to be one...
    days_value = int(days_value)

    today_date = date.today() + datetime.timedelta(days=1)
    date_delta = datetime.timedelta(days=days_value)

    print date_delta

    start_date = today_date - date_delta

    end_date_in_sec = int(time.mktime(today_date.timetuple()))
    start_date_in_sec = int(time.mktime(start_date.timetuple()))

    return(start_date_in_sec, end_date_in_sec)
