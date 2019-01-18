import re

import requests
import json

from django.template.loader import render_to_string

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
from deploy_ticket.models import PushDeployment, Issue, JiraUser, DbScripts, ConfluenceWikiPage

options = {
    'server': BASE_URL,
}

jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

projects = jira.projects()
# issue = jira.issue('MSXDEV-9577')
issue = jira.issue('INFRA-7692')
print(json.dumps(issue.raw))


def get_latest_sprint_issues():
    """
    """
    sprint_tickets = {}
    issues_in_project = jira.search_issues(
        'project=MSXDEV AND SPRINT not in closedSprints() AND sprint not in futureSprints()')

    for value in issues_in_project:
        print(value.key, value.fields.summary, value.fields.assignee, value.fields.reporter, value.fields.updated,
              value.fields.resolutiondate, value.fields.duedate, value.fields.labels)
        for sprint in value.fields.customfield_10440:
            sprint_name_list = re.findall(r"name=[^,]*", str(value.fields.customfield_10440[0]))
            if sprint_name_list:
                sprint_name = sprint_name_list[0].split('name=')[1]
                print(sprint_name)
                if sprint_name not in sprint_tickets:
                    sprint_tickets[sprint_name] = []
                sprint_tickets[sprint_name].append(value)
    return sprint_tickets


def create_db_queries_and_tickets(push_deployment, sprint, db_queries_for_infra_tickets={}):
    """
    :param push_deployment:
    :param sprint:
    :param db_queries_for_infra_tickets:
    :return:
    """
    sequence = 1
    for issue_key, db_queries in db_queries_for_infra_tickets.items():
        issue_description = render_to_string(
            template_name='../templates/ticket_format/upd/db_ticket.html',
            context={
                'db_queries': [(db_query['notes'], db_query['db_script'].split(';')) for db_query in db_queries],
                'sprint_key': issue_key,
                'db': push_deployment.get_effected_db_info()
            }
        )
        issue_description = issue_description.replace('&#39;', "'").replace('&quot;', '')
        issue_dict = {
            'project': {'key': 'INFRA'},
            'summary': '{0} - DB Migration on {0} server for {1}'.format(
                push_deployment.get_environment(), push_deployment.releasing_sprint_display_name
            ),
            'description': issue_description,
            'issuetype': {'name': 'Task'},
            'environment': push_deployment.get_environment(),
            'labels': ['UPCOMING-{}'.format(push_deployment.get_type_display())],
            'assignee': None
        }
        print(issue_dict)
        # new_issue = jira.create_issue(fields=issue_dict)
        new_issue = jira.issue(id='INFRA-7894')
        new_issue.update(issue_dict)

        assignee = None
        reporter = None
        creator = None

        if new_issue.fields.assignee:
            assignee, new_assignee = JiraUser.objects.get_or_create(
                jira_user_key=new_issue.fields.assignee.key,
                jira_user_email=new_issue.fields.assignee.emailAddress,
                defaults={
                    'jira_user_name': new_issue.fields.assignee.name,
                    'full_name': new_issue.fields.assignee.displayName
                }
            )
        if new_issue.fields.creator:
            creator, new_creator = JiraUser.objects.get_or_create(
                jira_user_key=new_issue.fields.creator.key,
                jira_user_email=new_issue.fields.creator.emailAddress,
                defaults={
                    'jira_user_name': new_issue.fields.creator.name,
                    'full_name': new_issue.fields.creator.displayName
                }
            )
        if new_issue.fields.reporter:
            reporter, new_reporter = JiraUser.objects.get_or_create(
                jira_user_key=new_issue.fields.reporter.key,
                jira_user_email=new_issue.fields.reporter.emailAddress,
                defaults={
                    'jira_user_name': new_issue.fields.reporter.name,
                    'full_name': new_issue.fields.reporter.displayName
                }
            )

        new_issue, created = Issue.objects.get_or_create(
            sprint=sprint,
            issue_key=new_issue.key,
            defaults={
                'issue_type': new_issue.fields.issuetype.name,
                'issue_jira_created_date': new_issue.fields.created,
                'issue_priority': new_issue.fields.priority.name,
                'issue_labels': ','.join(new_issue.fields.labels),
                'issue_status': new_issue.fields.status.name,
                'issue_environment': new_issue.fields.environment,
                'issue_duedate': new_issue.fields.duedate,
                'issue_title': new_issue.fields.summary,
                'description': new_issue.fields.description,
                'assiginee': assignee,
                'creator': creator,
                'reporter': reporter,
                # 'push_deployment_main_ticket': None,
                'push_deployment_db_ticket': push_deployment
            }
        )

        # creating db script entry
        db_script, created = DbScripts.objects.get_or_create(
            push_deployment=push_deployment,
            sprint=sprint,
            issue=new_issue,
            defaults={
                'script': db_queries,
                'execution_sequence': sequence,
            }
        )
        sequence += 1


def create_final_infra_ticket(push_deployment, sprint):
    """
    :param push_deployment:
    :param sprint:
    :return:
    """
    wiki_page = ConfluenceWikiPage.objects.filter(push_deployment=push_deployment).first()
    db_script_tickets = DbScripts.objects.select_related('issue').filter(
        push_deployment=push_deployment
    ).order_by('execution_sequence')
    issue_description = render_to_string(
        template_name='../templates/ticket_format/upd/upd_infra.html',
        context={
            'wiki_link': wiki_page.ui_link,
            'build_no': push_deployment.build_no,
            'environment': push_deployment.get_environment(),
            'deployment_type': push_deployment.get_type_display,
            'db_script_tickets': db_script_tickets,
            'end_counter': 3 + len(db_script_tickets)
        }
    )
    issue_description = issue_description.replace('&#39;', "'").replace('&quot;', '')
    issue_dict = {
        'project': {'key': 'INFRA'},
        'summary': '{0} - Deployment - {1}'.format(
            push_deployment.get_type_display(), push_deployment.releasing_sprint_display_name
        ),
        'description': issue_description,
        'issuetype': {'name': 'Task'},
        'environment': push_deployment.get_environment(),
        'labels': ['UPCOMING-{}'.format(push_deployment.get_type_display())],
        'assignee': None
    }
    print(issue_dict)
    # new_issue = jira.create_issue(fields=issue_dict)
    new_issue = jira.issue(id='INFRA-7905')
    new_issue.update(issue_dict)

    assignee = None
    reporter = None
    creator = None

    if new_issue.fields.assignee:
        assignee, new_assignee = JiraUser.objects.get_or_create(
            jira_user_key=new_issue.fields.assignee.key,
            jira_user_email=new_issue.fields.assignee.emailAddress,
            defaults={
                'jira_user_name': new_issue.fields.assignee.name,
                'full_name': new_issue.fields.assignee.displayName
            }
        )
    if new_issue.fields.creator:
        creator, new_creator = JiraUser.objects.get_or_create(
            jira_user_key=new_issue.fields.creator.key,
            jira_user_email=new_issue.fields.creator.emailAddress,
            defaults={
                'jira_user_name': new_issue.fields.creator.name,
                'full_name': new_issue.fields.creator.displayName
            }
        )
    if new_issue.fields.reporter:
        reporter, new_reporter = JiraUser.objects.get_or_create(
            jira_user_key=new_issue.fields.reporter.key,
            jira_user_email=new_issue.fields.reporter.emailAddress,
            defaults={
                'jira_user_name': new_issue.fields.reporter.name,
                'full_name': new_issue.fields.reporter.displayName
            }
        )

    new_issue, created = Issue.objects.get_or_create(
        sprint=sprint,
        issue_key=new_issue.key,
        defaults={
            'issue_type': new_issue.fields.issuetype.name,
            'issue_jira_created_date': new_issue.fields.created,
            'issue_priority': new_issue.fields.priority.name,
            'issue_labels': ','.join(new_issue.fields.labels),
            'issue_status': new_issue.fields.status.name,
            'issue_environment': new_issue.fields.environment,
            'issue_duedate': new_issue.fields.duedate,
            'issue_title': new_issue.fields.summary,
            'description': new_issue.fields.description,
            'assiginee': assignee,
            'creator': creator,
            'reporter': reporter,
            'push_deployment_main_ticket': push_deployment,
            'push_deployment_db_ticket': None
        }
    )
    push_deployment.status = PushDeployment.PD_STATUS_COMPLETED
    push_deployment.save()

# sprint(new_issue)
# issues_in_project = jira.search_issues('project=MSXDEV AND SPRINT not in closedSprints() AND sprint not in futureSprints()')

# issue_dict = {
# 	'project': {'id': 123},
# 	'summary': 'New issue from jira-python',
# 	'description': 'Look into this one',
# 	'issuetype': {'name': 'Bug'},
# }
# new_issue = jira.create_issue(fields=issue_dict)
