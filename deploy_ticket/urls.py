from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from deploy_ticket.forms import AdminLoginForm, LoginForm
from . import views
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view()), name=u'index'),
    url(
        r'^login/$',
        auth_views.login,
        {
            u'template_name': u'invitation/login.html', u'authentication_form': LoginForm,
            u'extra_context': {'next': '/deploy/'}
        },
        name='login'
    ),
    url(r'^pd-create/$', login_required(views.PushDeploymentCreationView.as_view()), name=u'pd_create'),
    url(r'^(?P<push_deployment_id>\d+)/issue-selection/$', login_required(views.PushDeploymentIssueSelectionView.as_view()), name=u'issue_selection'),
    url(
        r'^pd-create-progress/$',
        login_required(TemplateView.as_view(template_name=u'deploy_ticket/admin/pd_creation_progress.html')),
        name=u'pd_create_progress'
    ),
    url(
        r'^pd-create-progress-check/(?P<push_deployment_id>\d+)/$',
        login_required(views.PushDeploymentProgressCheckView.as_view()),
        name=u'pd_list_progress_check'
    ),
    url(r'^pd-list/$', login_required(views.PushDeploymentListView.as_view()), name=u'pd_list'),
    url(r'^pd/(?P<push_deployment_id>\d+)/$', login_required(views.PDDetailView.as_view()), name=u'view_pd'),
    url(r'^logout/$', auth_views.logout, {u'template_name': u'invitation/logout.html'}, name=u'logout'),
]
