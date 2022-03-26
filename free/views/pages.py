from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from free.views.api import ExecutionSerializer, ResultSerializer
from free.models import *
from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView

from django.contrib.auth.mixins import LoginRequiredMixin
class IndexView(TemplateView):
    template_name='free/index.html'

# EXPERIMENT CONTROL & EXECUTIONS

class ExecutionView(LoginRequiredMixin,DetailView):
    model = Execution
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['execution_json'] = ExecutionSerializer(self.object).data
        context['video_config'] = Apparatus.objects.get(id=self.object.apparatus.id).video_config
        try:
            context['final_result'] = ResultSerializer(Result.objects.get(result_type='f', execution=self.object)).data
        except:
            context['final_result'] = {}
        return context

    def get_template_names(self):
        return ['free/experiments/' + self.object.apparatus.apparatus_type.slug + '.html']

class CreateExecutionView(ExecutionView):    
    model = Execution

    def get_object(self):
        return Execution.objects.get_or_create(
            user = self.request.user,
            apparatus_id = self.kwargs['apparatus_id'],
            protocol_id = self.kwargs['protocol_id'],
            config = '',
            status = 'N'
        )[0]

class ExecutionsTable(Table):
    action = TemplateColumn(template_name='free/execution_link.html')

    class Meta:
        model = Execution
        fields = ['apparatus', 'name', 'protocol', 'status', 'start', 'end']

class ExecutionsListView(LoginRequiredMixin,SingleTableView):
    template_name = 'free/executions.html'
    table_class = ExecutionsTable

    def get_queryset(self):
        return Execution.objects.filter(user=self.request.user, status=self.status_filter)

class ExecutionsConfiguredListView(ExecutionsListView):
    status_filter = 'C'

class ExecutionsFinishedListView(ExecutionsListView):
    status_filter = 'F'
        
# PROTOCOLS LIST

class ApparatusTable(Table):

    protocols = TemplateColumn(template_name='free/protocols.html')
    current_status = Column(verbose_name=_('Current status'))

    class Meta:
        model = Apparatus
        fields = ['apparatus_type', 'location', 'apparatus_type__scientific_area', 'apparatus_type__lab_type', 'current_status', 'protocols']    
        
class ApparatusesView(LoginRequiredMixin,SingleTableView):
    template_name = 'free/apparatuses.html'
    table_class = ApparatusTable
    queryset = Apparatus.objects.all()