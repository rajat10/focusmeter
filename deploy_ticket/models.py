# Create your models here.

from datetime import datetime

from django.conf import settings
from django.db import models

from common import models as libs_models


class PushDeployment(libs_models.DatesModel):
    """
    Store upd information from jira, fetch each time from jira for getting latest changes
    """

    UAT_SERVER_LIST = [
        'ms5uat-proxy-001', 'ms5uat-cpanel-001', 'ms5uat-queue-001', 'ms5uat-comm-001', 'ms5uat-celery-001',
        'ms5uat-db-001', 'ms5uat-log-001'
    ]

    PROD_SERVER_LIST = [
        'ms5prod-proxy-001', 'ms5prod-cpanel-001', 'ms5prod-queue-001', 'ms5prod-comm-001', 'ms5prod-celery-001',
        'ms5prod-db-001', 'ms5prod-log-001'
    ]

    PD_TYPE_UPD = 1
    PD_TYPE_PPD = 2

    PD_TYPE_CHOICES = (
        (PD_TYPE_UPD, u'UPD'),
        (PD_TYPE_PPD, u'PPD'),
    )

    PD_STATUS_START = 1
    PD_STATUS_ISSUES_FETCH_START = 2
    PD_STATUS_DB_SCRIPT_FETCH_START = 3
    PD_STATUS_DB_INFRA_CREATION_START = 4
    PD_STATUS_CONFLUENCE_CREATION_START = 5
    PD_STATUS_INFRA_TICKET_CREATION_START = 6
    PD_STATUS_COMPLETED = 7

    PD_STATUS_CHOICES = (
        (PD_STATUS_START, 'Started Push deployment ticket Creation Process'),
        (PD_STATUS_ISSUES_FETCH_START, 'Fetching issues from current Sprint'),
        (PD_STATUS_DB_SCRIPT_FETCH_START, 'Fetching latest migration scripts from db confluence doc'),
        (PD_STATUS_DB_INFRA_CREATION_START, 'Creating INFRA database tickets for migration queries'),
        (PD_STATUS_CONFLUENCE_CREATION_START, 'Creating a new confluence doc with steps for this push deployment'),
        (PD_STATUS_INFRA_TICKET_CREATION_START, 'Creating final infra ticket for this push deployment'),
        (PD_STATUS_COMPLETED, 'Push deployment ticket creation process completed'),
    )

    key = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    type = models.IntegerField(choices=PD_TYPE_CHOICES, default=PD_TYPE_UPD)
    status = models.IntegerField(choices=PD_STATUS_CHOICES, default=PD_STATUS_START)
    version = models.IntegerField(default=1)
    version_description = models.TextField(blank=True, null=True)
    artifact_link = models.TextField(blank=True, null=True)
    installation_file_link = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scheduled_release_date = models.CharField(
        max_length=250, default='08/16/2018 LA, US ;  08/17/2018 New Delhi',
        help_text='Will be displayed on PD Confluence page Ex. 08/16/2018 LA, US ;  08/17/2018 New Delhi'
    )
    scheduled_maintainance_window = models.CharField(
        max_length=250, default='Aug 16th, 2018 (PST)',
        help_text='Will be displayed on PD Confluence page Ex. Aug 16th, 2018 (PST)'
    )
    scheduled_release_time = models.CharField(
        max_length=250, default='8:00 PM PST',
        help_text='Will be displayed on PD Confluence page Ex. 8:00 PM PST'
    )
    releasing_sprint_display_name = models.CharField(
        max_length=250, default='Sprint 14th Aug',
        help_text='Will be displayed on PD Confluence page Ex. Sprint 14th Aug'
    )
    build_no = models.CharField(
        max_length=250, default='....To be filled....',
        help_text='Finalised build no which will be on UPD/PPD infra ticket'
    )

    def get_environment(self):
        """
        :return:
        """
        return 'UAT' if self.type == PushDeployment.PD_TYPE_UPD else 'PROD'

    def get_effected_db_info(self):
        """
        :return:
        """
        return '*ms5uat* DB on UAT' if self.type == PushDeployment.PD_TYPE_UPD else '*ms5prod* DB on PROD'

    def get_server_list(self):
        """
        :return:
        """
        return self.UAT_SERVER_LIST if self.type == PushDeployment.PD_TYPE_UPD else self.PROD_SERVER_LIST



class Project(libs_models.DatesModel):
    """
    Store project information from jira
    """
    project_key = models.CharField(max_length=100, null=True, blank=True)
    project_name = models.CharField(max_length=100, null=True, blank=True)
    project_owner = models.CharField(max_length=100, null=True, blank=True)


class JiraUser(libs_models.DatesModel):
    """
    Store user information from jira
    """
    jira_user_key = models.CharField(max_length=100, null=True, blank=True)
    jira_user_email = models.CharField(max_length=100, null=True, blank=True)
    jira_user_name = models.CharField(max_length=100, null=True, blank=True)
    jira_password = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    can_create_upd = models.BooleanField(default=False)
    can_create_ppd = models.BooleanField(default=False)


class Sprint(libs_models.DatesModel):
    """
    Store sprint information from jira
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sprint_name = models.CharField(max_length=100, null=True, blank=True)
    sprint_start_date = models.DateTimeField(default=datetime.now)
    sprint_end_date = models.DateTimeField(default=datetime.now)
    push_deployment = models.ForeignKey(PushDeployment, on_delete=models.CASCADE)

    def __str__(self):
        """
        :return:
        """
        return self.sprint_name


class Issue(libs_models.DatesModel):
    """
    Store issue information from jira
    """
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    issue_key = models.CharField(max_length=250, null=True, blank=True)
    issue_type = models.CharField(max_length=250, null=True, blank=True)
    issue_jira_created_date = models.CharField(max_length=250, null=True, blank=True)
    issue_priority = models.CharField(max_length=250, null=True, blank=True)
    issue_labels = models.TextField(null=True, blank=True)
    issue_status = models.CharField(max_length=250, null=True, blank=True)
    issue_environment = models.CharField(max_length=250, null=True, blank=True)
    issue_duedate = models.CharField(max_length=250, null=True, blank=True)
    issue_title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    assiginee = models.ForeignKey(JiraUser, related_name='assigned_ticket', null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey(JiraUser, null=True, related_name='created_ticket', on_delete=models.SET_NULL)
    reporter = models.ForeignKey(JiraUser, null=True, related_name='reported_ticket', on_delete=models.SET_NULL)
    sprint_start_date = models.DateTimeField(default=datetime.now)
    sprint_end_date = models.DateTimeField(default=datetime.now)
    push_deployment_main_ticket = models.ForeignKey(PushDeployment, related_name='infra_ticket', on_delete=models.CASCADE, null=True)
    push_deployment_db_ticket = models.ForeignKey(PushDeployment, related_name='db_tickets', on_delete=models.CASCADE, null=True)
    selected_for_push_deployment = models.BooleanField(default=False)

    def __str__(self):
        return '{} : ( {} )'.format(self.issue_key, self.issue_type)


class DbScripts(libs_models.DatesModel):
    """
    Store db script information from db confluence to be used in sprint
    """
    push_deployment = models.ForeignKey(PushDeployment, on_delete=models.CASCADE)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    script = models.TextField(null=True, blank=True)
    execution_sequence = models.IntegerField(default=0)


class ConfluenceWikiPage(libs_models.DatesModel):
    """
    Store Confluence Wiki page information
    """
    space = models.CharField(max_length=100, null=True, blank=True)
    page_id = models.CharField(max_length=100, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    ui_link = models.URLField(null=True, blank=True)
    push_deployment = models.ForeignKey(PushDeployment, on_delete=models.CASCADE)
