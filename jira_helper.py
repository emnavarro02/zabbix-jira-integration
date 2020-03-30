import os
from jira import JIRA

url      = os.getenv("jira_url")
user     = os.getenv("jira_user")
password = os.getenv("jira_password")

assignee = "zoicloud"

jira = JIRA(options={'server':url}, basic_auth=(user,password))

def parse_zabbix_message(message):
    """ Creates a dictionary with  multiple reusable values from the original Zabbix message.
        ===============================================
        > Params:
            - message (String) : The original Zabbix message
        > Returns:
            - (Dictionary)

        It splits the message by semicollumn char (":"):
            - The fist part of the line is the Key 
            - The second part of the line is the value
        
        Considering the following message, it's possible to retrieve the "Original event ID"
        by using: dict.get("Original event ID")
        
        ~~~
            Problem: CloudHealth service is not running on i-ac5d6bba

            Problem started at 18:10:49 on 2020.03.30
            Problem name: CloudHealth service is not running on i-ac5d6bba
            Host: i-ac5d6bba
            Severity: Average

            Original problem ID: 2273037
        ~~~
    """
    dict = {}
    lines = message.splitlines()
    for line in lines:
        value = line.split(":")
        if len(value) > 1:
            print(value)
            dict[value[0]]=value[1].lstrip()
    return dict

def mount_jira_ticket_subject(instance_id,subject,zabbix_event_id):
    '''Create the Jira Issue subject following the pattern:
    <instance_id> - <Zabbix alert title> (<zabbix event id>)

    Params:
        - instance_id (String) : The affected instance ID or hostname
        - subject     (String) : The zabbix alert title
        - zabbix_event_id (String) : Zabbix original Event ID
    Returns : (String)'''
    title = subject + " (" + zabbix_event_id.lstrip() + ")"
    # title = instance_id + " - " + subject + " (" + zabbix_event_id.lstrip() + ")"
    return title

def create_new_ticket(subject,description,project_key="CCM"):
    '''Create a new JIRA issue.

        Params:
            - subject (String) : The ticket subject
            - description (String) : ticket body
            - project_key (String) : Jira project identification (default = CCM)
        Returns : (String)'''
    if opened_issues_amount(subject) == 0:
        ticket_dict = mount_ticket(subject,description,project_key)
        new_ticket = jira.create_issue(fields=ticket_dict)
        #TODO: Check if I need to return it.
        return new_ticket
    else:
        print("There is already a ticket for this issue.")
        return opened_issues(subject)

def mount_ticket(subject,description,project_key,issue_type="Incident"):
    '''Create a new ticket structure.
       ==============

        Params:
            - subject (String) : The ticket subject
            - description (String) : The ticket body
            - project_key (String) : Jira project name (e.g.: CCM)
            - issue_type (String) : The issue type (default=Incident)
            - request_type (String) : Jira custom field for the issue subcategory (default=Incident)
        Returns: (dict)    '''
    ticket = {
        'project': {'key': project_key},
        'summary': subject,
        'description': description,
        'issuetype': {'name': issue_type},
        'assignee': {'name': assignee},
        'customfield_14401' : "ccm/504ecb37-a078-4fb0-a85b-90acf231053b" # Service Desk - Request type
    }
    return ticket

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