import re

import requests
import json

from common.config import BASE_URL
from common.credentials import JIRA_USERNAME, JIRA_PASSWORD
from jira.client import JIRA

# BASE_URL = 'https://mpulsemobile.atlassian.net/rest/api/2/issue/'
# ISSUE_PREFIX = 'issue'
#
# url = '{}{}'.format(BASE_URL, 'MSXDEV-8472')
#
# r = requests.get(url, auth=(JIRA_USERNAME, JIRA_PASSWORD))
#
# data = None
# if r.status_code == 200:
#     data = json.loads(r.content.decode('utf-8'))


options = {
    'server': BASE_URL,
}

jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

projects = jira.projects()
issue = jira.issue('MSXDEV-9577')
print(json.dumps(issue.raw))


def get_latest_sprint_issues():
    """
    """
    sprint_tickets = {}
    issues_in_project = jira.search_issues('project=MSXDEV AND SPRINT not in closedSprints() AND sprint not in futureSprints()')

    for value in issues_in_project:
        print(value.key, value.fields.summary , value.fields.assignee , value.fields.reporter ,value.fields.updated ,value.fields.resolutiondate, value.fields.duedate, value.fields.labels)
        for sprint in value.fields.customfield_10440:
            sprint_name_list = re.findall(r"name=[^,]*", str(value.fields.customfield_10440[0]))
            if sprint_name_list:
                sprint_name = sprint_name_list[0].split('name=')[1]
                print(sprint_name)
                if sprint_name not in sprint_tickets:
                    sprint_tickets[sprint_name] = []
                sprint_tickets[sprint_name].append(value)
    return sprint_tickets

print(get_latest_sprint_issues())



# issue_dict = {
# 	'project': {'id': 123},
# 	'summary': 'New issue from jira-python',
# 	'description': 'Look into this one',
# 	'issuetype': {'name': 'Bug'},
# }
# new_issue = jira.create_issue(fields=issue_dict)
