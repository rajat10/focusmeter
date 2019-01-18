import json

from django.shortcuts import render, redirect

# Create your views here.
from datetime import datetime

from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic as generic_views, View

from deploy_ticket.forms import PDCreationForm, IssueSelectionForm
from deploy_ticket.models import PushDeployment, Issue, Sprint, ConfluenceWikiPage
from deploy_ticket.utils.helper import start_push_deployment_ticket_creation_process


class IndexView(generic_views.TemplateView):
    template_name = u'deploy_ticket/home.html'

    def get_context_data(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        push_deployment = PushDeployment.objects.get(id=2)
        start_push_deployment_ticket_creation_process(push_deployment=push_deployment)
        return super(IndexView, self).get_context_data(**kwargs)


class PushDeploymentProgressCheckView(View):
    """
    """
    def get(self, request, push_deployment_id):
        pd = PushDeployment.objects.get(id=push_deployment_id)
        return HttpResponse(
            content=json.dumps({'pd_status': pd.status, 'pd_status_display': pd.get_status_display()}),
            content_type='application/json'
        )


class PushDeploymentListView(generic_views.ListView):
    template_name = u'deploy_ticket/admin/pd_list_view.html'

    def get_queryset(self):
        """
        queryset
        :return:
        """

        return PushDeployment.objects.prefetch_related('infra_ticket').filter(
            status=PushDeployment.PD_STATUS_COMPLETED
        ).order_by('-created_at')


class PushDeploymentCreationView(generic_views.CreateView):
    """
    """
    form_class = PDCreationForm
    template_name = u'deploy_ticket/admin/create_push_deployment.html'

    def get_initial(self):
        """
        :return:
        """
        initials = super(PushDeploymentCreationView, self).get_initial()
        initials.update({u'user': self.request.user})
        return initials

    def get_context_data(self, **kwargs):
        return super(PushDeploymentCreationView, self).get_context_data(**kwargs)

    def get_success_url(self):
        """
        :return:
        """
        return reverse(u'deploy_ticket:issue_selection', kwargs={'push_deployment_id': self.object.id})


class PushDeploymentIssueSelectionView(generic_views.View):
    """
    """
    form_class = IssueSelectionForm
    template_name = u'deploy_ticket/admin/issue_selection.html'
    success_url = reverse_lazy(u'deploy_ticket:pd_create_progress')

    def get(self, request, push_deployment_id, *args, **kwargs):
        sprint = Sprint.objects.get(push_deployment_id=push_deployment_id)
        form = self.form_class(PushDeployment.objects.get(id=push_deployment_id))
        return render(request, self.template_name, {'form': form, 'sprint': sprint})

    def post(self, request, push_deployment_id, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        selected_issues = request.POST.getlist('issues_selection')
        count = Issue.objects.filter(sprint__push_deployment_id=push_deployment_id, id__in=selected_issues).update(
            selected_for_push_deployment=True
        )
        if count:
            start_push_deployment_ticket_creation_process(PushDeployment.objects.get(id=push_deployment_id))
        return redirect(u'deploy_ticket:pd_list')

    # def get_initial(self):
    #     """Return the initial data to use for forms on this view."""
    #     self.initial['procedural_questions']
    #     return self.initial.copy()

    # def get_queryset(self):
    #     """
    #     queryset
    #     :return:
    #     """
    #
    #     return Issue.objects.filter(
    #         sprint__push_deployment=self.kwargs.get('push_deployment_id'),
    #         push_deployment_main_ticket=None,
    #         push_deployment_db_ticket=None
    #     ).order_by('assiginee')


class PDDetailView(generic_views.DetailView):
    """
    """
    template_name = u'deploy_ticket/admin/view_push_deployment.html'
    pk_url_kwarg = u'push_deployment_id'

    def get_queryset(self):
        """
        queryset
        :return:
        """
        return PushDeployment.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PDDetailView, self).get_context_data(**kwargs)
        context['form'] = PDCreationForm(self.request.POST or None, instance=self.get_object())
        return context
