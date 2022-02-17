from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from free.views.api import ExecutionSerializer, ResultSerializer
from free.models import *
from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView

class IndexView(TemplateView):
    template_name='free/index.html'

# EXPERIMENT CONTROL & EXECUTIONS

class ExecutionView(DetailView):
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
        if not self.request.user.is_authenticated:
            return ['free/login.html']
        return ['free/experiments/' + self.object.apparatus.experiment.slug + '.html']

class CreateExecutionView(ExecutionView):    
    model = Execution

    def get_object(self):
        if not self.request.user.is_authenticated:
            return ['free/login.html']
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

class ExecutionsListView(SingleTableView):
    template_name = 'free/executions.html'
    table_class = ExecutionsTable

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ['free/login.html']
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
        fields = ['experiment', 'location', 'experiment__scientific_area', 'experiment__lab_type', 'current_status', 'protocols']    
        
class ApparatusesView(SingleTableView):
    template_name = 'free/apparatuses.html'
    table_class = ApparatusTable
    queryset = Apparatus.objects.all()