#!/usr/bin/env python
# coding: utf-8
import sys
import jira_helper
import zabbix_helper

script  = sys.argv[0]
send_to = sys.argv[1]
subject = sys.argv[2]
message = sys.argv[3]

# Retrieve parameters from Zabbix Alert message
params = jira_helper.parse_zabbix_message(message)
print ("Parameters obtained")

instance_id = params.get("Instance ID")
zabbix_event_id = params.get("Original event ID")
print ("Instance ID: " + instance_id)
print ("Zabbix ID: " + zabbix_event_id)

title = jira_helper.mount_jira_ticket_subject(instance_id,subject,zabbix_event_id)
print("Creating a new ticket with the title: " + title)

ticket = jira_helper.create_new_ticket(title,message,"CCM")
print (ticket)
# Update Zabbix alert with ticket information
# if ticket was opened
if ticket:
    print(ticket.key)
    # Search for the alert in Zabbix
    alert = zabbix_helper.search_alert(zabbix_event_id)
    print(alert)
    # If alert exists
    if alert:
        jira_issue = ticket.key
        # ACK the alert in Zabbix
        zabbix_helper.acknowledge_alert(zabbix_event_id,jira_issue)
    else:
        print("Alert not found in Zabbix.")
else: 
    print("Zabbix alert not updated due Ticket not created.")