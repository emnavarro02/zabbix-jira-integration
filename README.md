# Jira Zabbix Integration

The Jira Zabbix integration will create new Taskbox tickets based on Zabbix alerts.

The integration is done via a python script, triggered via an _Action_ configured in Zabbix. 
When a new alert is created in Zabbix the script will search in Taskbox for a previously opened ticket for the same problem and create a new *Incident*.

The alert priority will be calculated automatically based on the alert severity in Zabbix. 

Once the Ticket is created in Taskbox, the script will also acknowledge the alert in Zabbix with the Ticket number.

------------------------------------------------------------------------------------------------

## Libraries Dependencies

- os
- jira
- pyzabbix
- logger

------------------------------------------------------------------------------------------------

## Zabbix alert severity and Taskbox ticket priority correlation

The correlation between the Zabbix alert and the Taskbox ticket is presented below:

|Zabbix              | Taskbox                        | 
|--------------------| -------------------------------|
|Disaster            | Production system down (Prio 2)|
|High                | System impaired (Prio 3)       |
|Average             | System impaired (Prio 3)       |
|Warning (or bellow) | General guidance (Prio 4)      |


------------------------------------------------------------------------------------------------

## Implementation

Scripts must be deployed into: 

```
"<%zabbixpath%>/alertscripts/jira-issues/*"
```

Besides the script deployment it's necessary to configure 3 resources in Zabbix:

- User
- Media Type
- Action


### User configuration

The script runs behalf the Zabbix user `ssvc-jira-integration`.

The user must have `Read` and `Write` access to resources in Zabbix. Currently it's configured via an user group called `Taskbox Integration`.

In the user's media configuration you can control who the Taskbox ticket will be assigned to by setting a valid taskbox user in the "Send to" parameter.


### Media Type Configuration

The script configuration is done within a new Media Type called `Taskbox Issue`.

The configuration parameters are shown in the table below. 

> It's important to keep the script parameters order as presented in the table.


|Field               |  Value                |
|--------------------|-----------------------|
|Name                | Taskbox Issue         |
|Type                | Script                |
|Script name         | jira-issues/jiraya.py |
|Script Parameters 1 | {ALERT.SENDTO}        |
|Script Parameters 2 | {ALERT.SUBJECT}       |
|Script Parameters 3 | {ALERT.MESSAGE}       |
|Enabled             | True                  |


### Actions

The script is triggered via an Action called `Forward to Jira (Taskbox)`.

The Action's Operations is set to send message to the user `ssvc-jira-integration`.

The default message is presented bellow and must not be changed. It's used by the script to process the alert and create the ticket.


```xml
resource={HOST.NAME1}
event={ITEM.KEY1}
environment=Production
severity={TRIGGER.SEVERITY}
status={TRIGGER.STATUS}
ack={EVENT.ACK.STATUS}
service={TRIGGER.HOSTGROUP.NAME}
group=Zabbix
value={ITEM.VALUE1}
text={TRIGGER.STATUS}: {TRIGGER.NAME}
tags={EVENT.TAGS}
attributes.ip={HOST.IP1}
attributes.thresholdInfo={TRIGGER.TEMPLATE.NAME}: {TRIGGER.EXPRESSION}
type=zabbixAlert
eventid={EVENT.ID}
dateTime={EVENT.DATE}T{EVENT.TIME}Z
```