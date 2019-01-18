import django
from django.contrib.admin.forms import AdminAuthenticationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

from django.contrib.auth import get_user_model
from material import Layout, Row, Fieldset

from deploy_ticket.models import PushDeployment, Issue, Sprint
from deploy_ticket.utils.helper import generate_hash, fetch_sprint_and_issues

User = get_user_model()


class LoginFormMixin:
    """
    """
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))

    def clean_password(self):
        """
        :return:
        """
        password = self.cleaned_data['password']
        return password
        # return generate_hash(password)
        # return password


class AdminLoginForm(LoginFormMixin, AdminAuthenticationForm):
    """
    """
    pass


class LoginForm(LoginFormMixin, AuthenticationForm):
    """
    """
    pass


class PDCreationForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=PushDeployment.PD_TYPE_CHOICES,
        label='Deployment Ticket type',
        widget=forms.RadioSelect
    )
    # type = forms.ChoiceField(choices=PushDeployment.PD_TYPE_CHOICES, widget=forms.RadioSelect)
    scheduled_release_date = forms.CharField(
        label='Scheduled Release Date', max_length=100,
        help_text='Will be displayed on PD Confluence page Ex. 08/16/2018 LA, US ;  08/17/2018 New Delhi'
    )
    scheduled_maintainance_window = forms.CharField(
        label='Scheduled Maintainance Window', max_length=100,
        help_text='Will be displayed on PD Confluence page Ex. Aug 16th, 2018 (PST)'
    )
    scheduled_release_time = forms.CharField(
        label='Scheduled release time', max_length=100,
        help_text='Will be displayed on PD Confluence page Ex. 8:00 PM PST'
    )
    releasing_sprint_display_name = forms.CharField(
        label='Releasing sprint name', max_length=100,
        help_text='Will be displayed on PD Confluence page Ex. Sprint 14th Aug'
    )
    build_no = forms.CharField(
        label='Build no', max_length=100,
        help_text='Finalised build no which will be on UPD/PPD infra ticket'
    )
    artifact_link = forms.CharField(
        label='Artifact link from jenkins',
        help_text='https://ms5-jenkins.mpulse.io/job/Package/lastSuccessfulBuild/artifact/mobilestorm/msx-1.0.4728-20190114.tgz'
    )
    installation_file_link = forms.CharField(
        label='Installation file link from jenkins',
        help_text='https://ms5-jenkins.mpulse.io/job/Package/lastSuccessfulBuild/artifact/mobilestorm/install-1.0.4728.sh'
    )

    # doc = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = PushDeployment
        fields = [
            u'type', u'scheduled_release_date', u'scheduled_maintainance_window', u'scheduled_release_time',
            u'releasing_sprint_display_name', 'build_no', 'artifact_link', 'installation_file_link'
        ]

    def save(self, commit=True):
        self.instance.created_by = self.initial[u'user']
        push_deployment = super(PDCreationForm, self).save(commit=commit)
        sprint = fetch_sprint_and_issues(push_deployment=push_deployment)
        return push_deployment


class IssueSelectionForm(forms.Form):
    issues_selection = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False, choices=[]
    )

    layout = Layout(Row(Fieldset('Issues List', 'issues_selection')))

    def __init__(self, push_deployment, *args, **kwargs):
        super(IssueSelectionForm, self).__init__(*args, **kwargs)
        sprint = Sprint.objects.filter(push_deployment=push_deployment).first()
        self.layout.elements[0].elements[0].label = 'Issues of Sprint : {}'.format(sprint.sprint_name)
        self.fields['issues_selection'].choices =[(issue.id, issue) for issue in Issue.objects.filter(
            sprint__push_deployment=push_deployment, push_deployment_main_ticket=None, push_deployment_db_ticket=None
        )
        ]
