import json
from django.views.generic import TemplateView
from django.core import serializers
from free.models import *
class IndexView(TemplateView):
    template_name='free/index.html'



# Add by Rossa  need to be changed:
class ExperimentView(TemplateView):
    template_name='free/experiment.html'    

    def get_context_data(self, **kwargs):
        context = super(ExperimentView, self).get_context_data(**kwargs)
        data = serializers.serialize('json', Experiment.objects.all())
        # print(data)

        context['free_experiment'] = json.loads(data)

        return context


class CavityView(TemplateView):
    template_name='free/cavity.html'          


class PendulumView(TemplateView):
    template_name='free/pendulum.html'     

    def get_context_data(self, **kwargs):
        context = super(PendulumView, self).get_context_data(**kwargs)
        
        id = self.request.GET.get('id', None)
        location = self.request.GET.get('location', None)

        data = None
        if id != None:
            data = serializers.serialize('json', Experiment.objects.filter(id=id))
        
        context['config'] = {}
        delta = {
        "min": 0,
        "max": 50
        }

        context['min'] = 0
        context['max'] = 40
        context['deltaX'] = delta

        print('Result data', data)
        try:
            if data != None:
                data = json.loads(data)
            # print('Result data', data[0]['fields']['config'])

            if data and len(data) > 0 and data[0]['fields']['config']:
                context['config'] = data[0]['fields']['config']
        except:
            pass

        return context