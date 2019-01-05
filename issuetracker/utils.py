import requests
import json
from common.credentials import JIRA_USERNAME, JIRA_PASSWORD
from jira.client import JIRA

BASE_URL = 'https://mpulsemobile.atlassian.net/rest/api/2/issue/'
ISSUE_PREFIX = 'issue'

url = '{}{}'.format(BASE_URL, 'MSXDEV-8472')

r = requests.get(url, auth=(JIRA_USERNAME, JIRA_PASSWORD))

data = None
if r.status_code == 200:
	data = json.loads(r.content.decode('utf-8'))


options = {
	'server': 'https://mpulsemobile.atlassian.net',
}

jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

projects = jira.projects()
issue = jira.issue('MSXDEV-9577')
print(json.dumps(issue.raw))




# issue_dict = {
# 	'project': {'id': 123},
# 	'summary': 'New issue from jira-python',
# 	'description': 'Look into this one',
# 	'issuetype': {'name': 'Bug'},
# }
# new_issue = jira.create_issue(fields=issue_dict)



