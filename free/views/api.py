from django.utils import timezone
from rest_framework import generics, serializers, views
from rest_framework.response import Response
from free.models import *

# Experiment
class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = ['name', 'description', 'config', 'scientific_area', 'lab_type']

class ExperimentListAPI(generics.ListAPIView):
    """
    Returns a list of **all** experiments.
    """
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


# Execution API

class ExecutionConfigSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.HiddenField(default='C')

    class Meta:
        model = Execution
        fields = ['id','apparatus', 'protocol', 'config', 'status', 'user']

# TODO: Schema validation!
# Maybe convert to APIView for more verbosity
class ExecutionConfigure(generics.CreateAPIView):
    """
    Configures an execution of experiment for a given apparatus and protocol.
    """
    serializer_class = ExecutionConfigSerializer
    queryset = Execution.objects.all()


class ExecutionStart(views.APIView):
    """
    Starts a configured execution
    """
    def put(self, *args, **kwargs):
        try:
            execution = Execution.objects.get(pk=kwargs['id'])
        except Execution.DoesNotExist:
            return Response(status = 404)

        if execution.status != 'C':
            return Response({'error': 'This execution has already been started'}, status = 400)

        execution.status = 'R'
        execution.start = timezone.now()
        execution.save()

        return Response(status = 200)

# Maybe this should return all execution info?
class ExecutionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = ['status']

class ExecutionStatus(generics.RetrieveAPIView):
    """
    Returns the current status of an execution with a given id.
    """
    serializer_class = ExecutionStatusSerializer
    queryset = Execution.objects.all()
    lookup_field='id'