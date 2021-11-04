from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, DetailView
from free.views.api import ExecutionSerializer
from free.models import *
from django_tables2 import Table, Column
from django_tables2.views import SingleTableView

class IndexView(TemplateView):
    template_name='free/index.html'

class ExperimentView(DetailView):
    template_name='free/experiments/pendulum.html'    
    model = Experiment

    def get_template_names(self):
        return ['free/experiments/' + self.object.slug + '.html']
        
class ExperimentExecutionView(ExperimentView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Add filter for user and experiment
        context['execution'] = Execution.objects.get(pk=self.kwargs['execution'])
        context['execution_json'] = ExecutionSerializer(context['execution']).data

        return context

# PROTOCOLS LIST

class ApparatusTable(Table):
    class Meta:
        model = Apparatus
        fields = ['experiment', 'location', 'experiment__scientific_area', 'experiment__lab_type', 'protocols']
    
class ApparatusesView(SingleTableView):
    template_name = 'free/protocols.html'
    table_class = ApparatusTable
    queryset = Apparatus.objects.all()