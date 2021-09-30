from typing_extensions import Final
from django.db.models import query
from django.utils import timezone
from rest_framework import generics, serializers, views
from rest_framework.exceptions import ValidationError
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
            return Response({'error': 'Execution with given ID does not exist!'}, status = 404)

        if execution.status != 'C':
            return Response({'error': 'This execution has already been started'}, status = 400)

        execution.status = 'R'
        execution.start = timezone.now()
        execution.save()

        return Response(status = 200)

# Maybe this should return all execution info. YES
class ExecutionSerializer(serializers.ModelSerializer):
    read_only = True
    class Meta:
        model = Execution
        fields = '__all__'

class ExecutionView(generics.RetrieveAPIView):
    """
    Returns the current status of an execution with a given id.
    """
    serializer_class = ExecutionSerializer
    queryset = Execution.objects.all()
    lookup_field='id'


class ProtocolSerializer(serializers.ModelSerializer):
    read_only = True
    class Meta:
        model = Protocol
        fields = ['name', 'config']

class ProtocolList(generics.ListAPIView):
    """
    Returns all protocols configured for a given apparatus id.
    """
    serializer_class = ProtocolSerializer
    def list(self, request, *args, **kwargs):
        try:
            self.apparatus = Apparatus.objects.get(pk=self.kwargs['apparatus_id'])
        except Apparatus.DoesNotExist:
            return Response({'error': 'Apparatus with given ID does not exist!'}, status=404)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Protocol.objects.filter(apparatus=self.apparatus)

class NextExecution(generics.RetrieveAPIView):
    """
    Returns the earliest started execution
    """
    serializer_class = ExecutionSerializer
    def get_object(self):
        return Execution.objects.filter(status='R').order_by('start').first()


class PartialResultSerializer(serializers.ModelSerializer):
    result_type = serializers.HiddenField(default='p')
    class Meta:
        model = Result
        fields = ['id', 'execution', 'value', 'result_type']

class AddPartialResult(generics.CreateAPIView):
    """
    Adds a partial measurement result to a given execution
    """
    serializer_class = PartialResultSerializer
    queryset = Result.objects.all()

class FinalResultSerializer(serializers.ModelSerializer):
    result_type = serializers.HiddenField(default='f')
    class Meta:
        model = Result
        fields = ['id', 'execution', 'value', 'result_type']

class AddFinalResult(generics.CreateAPIView):
    """
    Add a final measurement result to a given execution
    """
    serializer_class = FinalResultSerializer
    queryset = Result.objects.all()

class ExecutionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = ['status']

class ChangeExecutionStatus(generics.RetrieveUpdateAPIView):
    """
    Changes or retrieves the status of a given execution
    """
    serializer_class = ExecutionStatusSerializer
    queryset = Execution.objects.all()
    lookup_field='id'