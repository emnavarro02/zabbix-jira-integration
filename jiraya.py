#!/usr/bin/env python
# coding: utf-8
import sys
import jira_helper
import zabbix_helper
import logging
logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT, file='jiraya.log')
logger.setLevel(logging.DEBUG)

script  = sys.argv[0]
send_to = sys.argv[1]
subject = sys.argv[2]
message = sys.argv[3]

# Retrieve parameters from Zabbix Alert message
params = jira_helper.parse_zabbix_message(message)
logger.info("Parameters obtained")

instance_id = params.get("Host")
zabbix_event_id = params.get("Original problem ID")
logger.info("Instance ID: " + instance_id)
logger.info("Event ID: " + zabbix_event_id)

title = jira_helper.mount_jira_ticket_subject(instance_id,subject,zabbix_event_id)
logger.info("Creating a new ticket with the title: " + title)

ticket = jira_helper.create_new_ticket(title,message,"CCM")
# Update Zabbix alert with ticket information. If ticket was opened
if ticket:
    logger.info("Created jira issue: " + ticket.key)
    logger.info("Updating Zabbix alert with the new alert")
    # Search for the alert in Zabbix
    alert = zabbix_helper.search_alert(zabbix_event_id)
    logger.info("Finding Zabbix alert to acknowledge: " + alert[0].get("eventid"))
    # If alert exists
    if alert:
        jira_issue = ticket.key
        # ACK the alert in Zabbix
        zabbix_helper.acknowledge_alert(zabbix_event_id,jira_issue)
    else:
        logger.info("Alert not found in Zabbix.")
else: 
    logger.info("Zabbix alert not updated due Ticket not created.")