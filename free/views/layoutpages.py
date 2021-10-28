import json
from django.views.generic import TemplateView
from django.core import serializers
from free.models import *
from django.db import connection

class ProtocolsView(TemplateView):
    template_name='free/protocols.html'

    def get_context_data(self, **kwargs):
        context = super(ProtocolsView, self).get_context_data(**kwargs)
        data = serializers.serialize('json', Experiment.objects.all())
        
        cursor = connection.cursor()
        cursor.execute('select fe.id as id, fe.name as name, fa.location as location, fe.scientific_area as scientific_area, \
            fe.lab_type as education_levels from free_apparatus fa, free_experiment fe where fa.experiment_id = fe.id ;')
        results = cursor.fetchall()
        experiments_list = []
        for item in results:
            experiment_data = {
                "id": item[0],
                "name": item[1],
                "location": item[2],
                "scientific_area": item[3],
                "education_levels": item[4],
            }
            experiments_list.append(experiment_data)
            print('Results experiment_data : ', experiment_data)

        print('Resultsdata : ', data)
        print('Resultsdata : ', experiments_list)
        context['free_experiments'] = json.loads(data)
        context['free_experimentsjj'] = experiments_list

        return context


class ExecutionsView(TemplateView):
    template_name='free/executions.html'    