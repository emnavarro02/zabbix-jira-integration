import os
from jira import JIRA

url      = os.getenv("jira_url")
user     = os.getenv("jira_user")
password = os.getenv("jira_password")
# assignee = "zoicloud"

jira = JIRA(options={'server':url}, basic_auth=(user,password))

def parse_zabbix_message(message):
    """ Creates a dictionary with  multiple reusable values from the original Zabbix message.
        ===============================================

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
    """
    dict = {}
    lines = message.splitlines()
    for line in lines:
        value = line.split("=")
        if len(value) > 1:
            print(value)
            dict[value[0]]=value[1].lstrip()
    return dict

def mount_jira_ticket_subject(instance_id,subject,zabbix_event_id,severity):
    '''Create the Jira Issue subject following the pattern:
    <instance_id> - <Zabbix alert title> (<zabbix event id>)

    Params:
        - instance_id (String) : The affected instance ID or hostname
        - subject     (String) : The zabbix alert title
        - zabbix_event_id (String) : Zabbix original Event ID
    Returns : (String)'''
    title = subject + " " + severity + " (" + zabbix_event_id.lstrip() + ")"
    return title

def create_new_ticket(title,message,priority,assignee,reporter="zoirobot",project_key="CCM"):
    '''Create a new JIRA issue.

        Params:
            - title (String) : The ticket title
            - message (String) : ticket body
            - priority (String) : The Jira ticket priority 
            - assignee (String) : ticket Asignee
            - project_key (String) : Jira project identification (default = CCM)
        Returns : (String)
    '''
    ticket_dict = mount_ticket(title,message,project_key,assignee,priority)
    return jira.create_issue(fields=ticket_dict)

def mount_ticket(subject,description,project_key,assignee,priority,issue_type="Incident"):
    '''Create a new ticket structure.
       ==============

        Params:
            - subject (String) : The ticket subject
            - description (String) : The ticket body
            - project_key (String) : Jira project name (e.g.: CCM)
            - issue_type (String) : The issue type (default=Incident)
            - priority (String) : The ticket severity
            - request_type (String) : Jira custom field for the issue subcategory (default=Incident)
        Returns: (dict)    '''
    ticket = {
        'project': {'key': project_key},
        'summary': subject,
        'description': description,
        'issuetype': {'name': issue_type},
        'assignee': {'name': assignee},
        'priority' : {'name' : priority},
        'customfield_14401' : "ccm/504ecb37-a078-4fb0-a85b-90acf231053b" # Service Desk - Request type
    }
    return ticket

def priority_calculation(severity):
    '''Maps the Zabbix alert severity to the Jira issue priority.

        Params:
            - severity (String) : The zabbix alert severity

        Returns : (String)
        ~~~
        'Disaster' = "Production system down (Prio 2)"
        'High' = "System impaired (Prio 3)"
        'Average' = "System impaired (Prio 3)"
        'Warning (or bellow)' = "General guidance (Prio 4)"
        ~~~
    '''
    if severity == "Disaster" : 
        return "Production system down (Prio 2)"
    # elif severity == "High": 
        # return "Production system down (Prio 2)"
    elif severity == "Average" or severity == "High": 
        return "System impaired (Prio 3)"
    else:
        return "General guidance (Prio 4)"

def opened_issues_amount(subject):
    '''Search for opened JIRA issues with the same subject.
       ============================
        Params:
            - subject (String) : the ticket subject 
        Returns: (int)'''
    query = "Summary ~ '" + subject + "' and Status != Done"
    opened_issues = jira.search_issues(query)
    return len(opened_issues)

def opened_issues(subject):
    '''Search for opened JIRA issues with the same subject.
       ============================
        Params:
            - subject (String) : the ticket subject 
        Returns: (int)'''
    query = "Summary ~ '" + subject + "' and Status != Done"
    opened_issues = jira.search_issues(query)
    return opened_issues[0]