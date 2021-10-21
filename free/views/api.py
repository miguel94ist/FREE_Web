from rest_framework import generics, serializers, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from free.models import *
from jsonschema import validate, ValidationError as JSONValidationError

from free.views.permissions import ApparatusOnlyAccess

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

    def validate(self, data):
        try:
            validate(instance = data['config'] if 'config' in data else {}, schema = data['protocol'].config)
        except JSONValidationError as e:
            raise serializers.ValidationError(e.message)
        return data

    class Meta:
        model = Execution
        fields = ['id','apparatus', 'protocol', 'config', 'status', 'user']

class ExecutionUpdateRetrieveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate(self, data):
        try:
            validate(instance = data['config'] if 'config' in data else {}, schema = data['protocol'].config)
        except JSONValidationError as e:
            raise serializers.ValidationError(e.message)

        if self.instance: # if updating
            if self.instance.status != 'C':
                raise serializers.ValidationError("Can only update configuration of not enqueued/runned executions.")
        return data       

    class Meta:
        model = Execution
        fields = ['id','apparatus', 'protocol', 'config', 'status']


class ExecutionConfigure(generics.CreateAPIView):
    """
    Configures an execution of experiment for a given apparatus and protocol.
    """
    serializer_class = ExecutionConfigSerializer
    queryset = Execution.objects.all()

class ExecutionUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves or updates a given execution
    """
    serializer_class = ExecutionUpdateRetrieveSerializer
    queryset = Execution.objects.all()
    lookup_field = 'id'


class ExecutionStart(views.APIView):
    """
    Starts a configured execution (status is changed to Q- "Queued")
    """
    def put(self, *args, **kwargs):
        try:
            execution = Execution.objects.get(pk=kwargs['id'])
        except Execution.DoesNotExist:
            return Response({'error': 'Execution with given ID does not exist!'}, status = 404)

        if execution.status != 'C':
            return Response({'error': 'This execution has already been started'}, status = 400)

        execution.status = 'Q'
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

class ApparatusSerializer(serializers.ModelSerializer):
    read_only = True
    protocols = ProtocolSerializer(many=True)
    experiment = ExperimentSerializer()
    class Meta:
        model = Apparatus
        fields = ['experiment', 'protocols', 'location', 'owner']

class AppratusView(generics.RetrieveAPIView):
    serializer_class = ApparatusSerializer
    queryset = Apparatus.objects.all()
    lookup_field = 'id'

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
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_object(self):
        obj = Execution.objects.filter(status='Q', apparatus_id=self.kwargs['apparatus_id']).order_by('start').first()
        if obj:
            self.check_object_permissions(self.request, obj)
            obj.status = 'R'
            obj.save()
        return obj
        

class QueuedExecutions(generics.ListAPIView):
    """
    Returns all queued executions
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_queryset(self):
        return Execution.objects.filter()

class ResultSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['execution'].status != 'R':
            raise ValidationError('Can only add resuls to a running execution!')
        if data['result_type'] == 'f':
            if Result.objects.filter(execution=data['execution'], result_type='f').count()!=0:
                raise ValidationError('Cannot add more than one final result!')
            data['execution'].status = 'F'
            data['execution'].save()
        return data

    class Meta:
        model = Result
        fields = ['id', 'execution', 'value', 'result_type']

class AddResult(generics.CreateAPIView):
    """
    Add a measurement result to a given execution
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ResultSerializer
    queryset = Result.objects.all()

    def create(self, request, *args, **kwargs):
        execution = Execution.objects.get(pk=request.data['execution'])
        self.check_object_permissions(request, execution)  
        return super().create(request, *args, **kwargs)


class ResultList(generics.ListAPIView):
    """
    Returns a list of all results for a given execution_id, with id greater or equal to last_id
    """
    serializer_class = ResultSerializer

    def get_queryset(self):
        if 'last_id' in self.kwargs:
            return Result.objects.filter(execution_id=self.kwargs['execution_id'], pk__gte=self.kwargs['last_id'])
        else:
            return Result.objects.filter(execution_id=self.kwargs['execution_id'])

class ExecutionStatusSerializer(serializers.ModelSerializer):
    permission_classes = [ApparatusOnlyAccess]
    def validate(self, data):
        valid_transitions = {
            'R': ['F', 'E']
        }

        if self.instance: # if updating
            if self.instance.status in valid_transitions:
                if data['status'] not in valid_transitions[self.instance.status]:
                    raise ValidationError('Execution in state ' + self.instance.status + ' can only change state to ' + ','.join(valid_transitions[self.instance.status]))
            else:
                raise ValidationError('Cannot change an execution with status ' + self.instance.status)

        return data
                
    class Meta:
        model = Execution
        fields = ['status']

class ChangeExecutionStatus(generics.RetrieveUpdateAPIView):
    """
    Changes or retrieves the status of a given execution
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionStatusSerializer
    queryset = Execution.objects.all()
    lookup_field='id'

class ExecutionQueue(generics.ListAPIView):
    """
    Retrieves a current execution queue for the apparatus
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_queryset(self):
        return Execution.objects.filter(state='Q', apparatus_id=self.kwargs['apparatus_id'])