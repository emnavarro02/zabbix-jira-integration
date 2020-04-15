#!/usr/bin/env python
# coding: utf-8
import os
from pyzabbix import ZabbixAPI

url = os.getenv("zabbix_url")
user = os.getenv("zabbix_user")
password = os.getenv("zabbix_password")

try:
    zapi = ZabbixAPI(url)
    zapi.login(user, password)
except:
    print("Error while logging in Zabbix. Check credentials")


def search_alert(eventid):
    '''Search for a Zabbix alert based on the original Event ID

    Params:
        - eventid (String) : The Zabbix Original Event ID
    Returns : (list)'''
    # search alert
    return zapi.event.get(output="extended", eventids=eventid)


def acknowledge_alert(eventid, jira_issue):
    '''Acknowledges a Zabbix alert based on the Original Event ID

    Params:
        - eventid (String) : The Zabbix Original Event ID
        - jira_issue (String) : The Jira issue number
    '''
    message = "The ticket " + jira_issue + \
        " have been automatically created in Taskbox."
    zapi.event.acknowledge(eventids=eventid, message=message)
