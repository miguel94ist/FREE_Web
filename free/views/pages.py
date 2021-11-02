import json
from django.views.generic import TemplateView, DetailView
from free.views.api import ExecutionSerializer
from free.models import *
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
        context['execution'] = ExecutionSerializer(Execution.objects.get(pk=self.kwargs['execution'])).data
        return context