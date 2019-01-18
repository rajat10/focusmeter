import hashlib
import hmac
import uuid
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import (
    pagination as rest_pagination
)

from deploy_ticket.models import PushDeployment, Project, Sprint, Issue, JiraUser
from deploy_ticket.utils.confluence import get_db_queries_for_infra_tickets, create_deployment_wiki_tickets
from deploy_ticket.utils.jira_util import get_latest_sprint_issues, create_db_queries_and_tickets, \
    create_final_infra_ticket


def random_string(digits=12):
    return uuid.uuid4().hex.upper()[:digits]


def generate_hash(data):
    """
    Util to one way hash the data based on a secret key
    """
    return hmac.new(msg=data.encode(), key=settings.HASHING_KEY.encode(), digestmod=hashlib.sha512).hexdigest()


class StandardResultsSetPagination(rest_pagination.PageNumberPagination):
    """
    Custom Pagination class
    """
    page_size = 100
    page_size_query_param = u'page_size'
    max_page_size = 1000


def send_email(subject, to_email, message=None, is_html=True, template_name=None, email_body_context=None):
    if is_html and template_name:
        message = render_to_string(template_name=template_name, context=email_body_context)
    sender = EMAIL_INVITATION_SENDER_EMAIL_ID = 'sri.rajat10@gmail.com'
    EMAIL_INVITATION_TEST_MODE=''
    EMAIL_INVITATION_TEST_EMAIL_ID=''
    if EMAIL_INVITATION_TEST_MODE == 'True':
        to_list = [EMAIL_INVITATION_TEST_EMAIL_ID]
    else:
        to_list = [to_email]
    msg = EmailMessage(subject, message, sender, to_list)
    msg.content_subtype = u'html' if is_html else u'text' # Main content is now text/html
    msg.send(fail_silently=True)


def fetch_sprint_and_issues(push_deployment):
    """
    :param push_deployment:
    :return:
    """
    project = None
    sprint = None
    # push_deployment = PushDeployment.objects.get(id=2)
    latest_sprint_issues = get_latest_sprint_issues()
    for sprint_name, issues in latest_sprint_issues.items():
        for issue in issues:
            if not project:
                project = issue.raw['fields']['project']
                project, created = Project.objects.get_or_create(
                    project_key=project['key'],
                    defaults={'project_name':project['name'], 'project_owner':'Josh'}
                )
            if not sprint:
                sprint, created = Sprint.objects.get_or_create(
                    project=project,
                    sprint_name=sprint_name,
                    push_deployment=push_deployment,
                    defaults={}
                )
            if issue.fields.assignee:
                assignee, new_assignee = JiraUser.objects.get_or_create(
                    jira_user_key=issue.fields.assignee.key,
                    jira_user_email=issue.fields.assignee.emailAddress,
                    defaults={
                        'jira_user_name':issue.fields.assignee.name,
                        'full_name':issue.fields.assignee.displayName
                    }
                )
                creator, new_creator = JiraUser.objects.get_or_create(
                    jira_user_key=issue.fields.creator.key,
                    jira_user_email=issue.fields.creator.emailAddress,
                    defaults={
                        'jira_user_name':issue.fields.creator.name,
                        'full_name':issue.fields.creator.displayName
                    }
                )
                reporter, new_reporter = JiraUser.objects.get_or_create(
                    jira_user_key=issue.fields.reporter.key,
                    jira_user_email=issue.fields.reporter.emailAddress,
                    defaults={
                        'jira_user_name':issue.fields.reporter.name,
                        'full_name':issue.fields.reporter.displayName
                    }
                )
                saved_issue, created = Issue.objects.get_or_create(
                    sprint=sprint,
                    issue_key=issue.key,
                    defaults={
                        'issue_type': issue.fields.issuetype.name,
                        'issue_jira_created_date': issue.fields.created,
                        'issue_priority': issue.fields.priority.name,
                        'issue_labels': ','.join(issue.fields.labels),
                        'issue_status': issue.fields.status.name,
                        'issue_environment': issue.fields.environment,
                        'issue_duedate': issue.fields.duedate,
                        'issue_title': issue.fields.summary,
                        'description': issue.fields.description,
                        'assiginee': assignee,
                        'creator': creator,
                        'reporter': reporter,
                        'sprint_start_date': datetime.now,
                        'sprint_end_date': datetime.now,
                        # 'push_deployment_main_ticket': None,
                        # 'push_deployment_db_ticket': None
                    }
                )
    return sprint


def start_push_deployment_ticket_creation_process(push_deployment):
    """
    :param self:
    :return:
    """
    sprint = fetch_sprint_and_issues(push_deployment=push_deployment)

    db_queries_for_infra_tickets = get_db_queries_for_infra_tickets()
    # db_queries_for_infra_tickets = {
    #     'MSXDEV-9316': [
    #         "ALTER TYPE activitytype ADD VALUE 'MEMBER_RECORD_CREATE';ALTER TYPE activitytype ADD VALUE 'MEMBER_RECORD_UPDATE';ALTER TYPE activitytype ADD VALUE 'MEMBER_RECORD_DELETE';switch to postgres user to run this:DELETE FROM pg_enum WHERE enumlabel in ('MEMBER_CREATE', 'MEMBER_DELETE', 'MEMBER_UPDATE');"
    #     ]
    # }

    create_db_queries_and_tickets(
        push_deployment=push_deployment, sprint=sprint,
        db_queries_for_infra_tickets=db_queries_for_infra_tickets
    )

    create_deployment_wiki_tickets(
        push_deployment=push_deployment
    )

    create_final_infra_ticket(push_deployment, sprint)

    print(db_queries_for_infra_tickets)


def start_push_deployment_ticket_creation_process1(push_deployment):
    """
    :param push_deployment:
    :return:
    """
    push_deployment = PushDeployment.objects.get(id=2)
    sprint = fetch_sprint_and_issues(push_deployment=push_deployment)

    db_queries_for_infra_tickets = get_db_queries_for_infra_tickets()

    create_db_queries_and_tickets(
        push_deployment=push_deployment, sprint=sprint,
        db_queries_for_infra_tickets=db_queries_for_infra_tickets
    )
    print(db_queries_for_infra_tickets)


    # create_deployment_wiki_tickets(push_deployment=push_deployment)
    # create_final_infra_ticket(
    #     push_deployment=push_deployment, sprint=push_deployment.sprint_set.first()
    # )


# Issue.objects.all().delete()
# JiraUser.objects.all().delete()
# Sprint.objects.all().delete()
# Project.objects.all().delete()
#
