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
severity = params.get("severity")
zabbix_event_id = params.get("eventid")

# Check if ticket is already opened
logger.info("New alert received. Checking if there is a ticket in Taskbox")
opened_tickets = jira_helper.opened_issues_amount(subject)

# if not, open a new ticket
if (opened_tickets <= 0): 
    logger.info("No ticket was found. Creating a new ticket in Taskbox.")
    ticket_priority = jira_helper.priority_calculation(severity)
    logger.info("Mapped alert  severity {zabbix_severity} to the Jira priority {jira_priority}".format(zabbix_severity=severity, jira_priority=ticket_priority))
    new_ticket = jira_helper.create_new_ticket(subject,message,ticket_priority,send_to)
    
    # if ticket opened, acknowledge alert in Zabbix. 
    if (new_ticket > 0):
        logger.info("Ticket {ticket} have been created. Acknowledging Zabbix alert {zabbix_event_id}".format(ticket=new_ticket.key, zabbix_event_id=zabbix_event_id))
        zabbix_helper.acknowledge_alert(zabbix_event_id,new_ticket.key)
    else: 
        logger.info("Zabbix alert was not updated because the ticket was not created.")
else:
    logger.info("An existing ticket has been found for this alert. Skipping.")

# https://github.com/alerta/zabbix-alerta