from rest_framework import generics
from free.models import *
from rest_framework.serializers import ModelSerializer

# Experiment
class ExperimentSerializer(ModelSerializer):
    class Meta:
        model = Experiment
        fields = ['name', 'description', 'config', 'scientific_area', 'lab_type']

class ExperimentListAPI(generics.ListAPIView):
    """
    Returns a list of **all** experiments.
    """
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer