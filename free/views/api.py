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
    Returns a list of all experiments.

    Returns a list of all experiments.
    """
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


# Execution API

class ExecutionConfigSerializer(serializers.ModelSerializer):

    def validate(self, data):
        try:
            validate(instance = data['config'] if 'config' in data else {}, schema = data['protocol'].config)
        except JSONValidationError as e:
            raise serializers.ValidationError(e.message)

        return data

    class Meta:
        model = Execution
        fields = ['id','apparatus', 'protocol', 'config']

class ProtocolSerializer(serializers.ModelSerializer):
    read_only = True
    class Meta:
        model = Protocol
        fields = ['id', 'name', 'config']

class ApparatusSerializer(serializers.ModelSerializer):
    read_only = True
    protocols = ProtocolSerializer(many=True)
    experiment = ExperimentSerializer()
    class Meta:
        model = Apparatus
        fields = ['experiment', 'protocols', 'location', 'owner', 'video_config']

class ExecutionSerializer(serializers.ModelSerializer):
    protocol = ProtocolSerializer()

    def validate(self, data):
        data = super().validate(data)

        if self.instance: # if updating or destroying
            if self.instance.status != 'C':
                raise serializers.ValidationError("Can only update configuration of not enqueued executions.")
            try:
                validate(instance = data['config'] if 'config' in data else {}, schema = self.instance.protocol.config)
            except JSONValidationError as e:
                raise serializers.ValidationError(e.message)
            
        return data  

    class Meta:
        model = Execution
        fields = ['id','apparatus', 'protocol', 'config', 'status', 'queue_time', 'start', 'end']
        read_only_fields = ('id', 'apparatus', 'protocol', 'status', 'queue_time', 'start', 'end')


class ExecutionConfigure(generics.CreateAPIView):
    """
    Configures an execution of experiment. 
    
    You must supply valid apparatus and protocol ids. The config is validated against JSON schema of the protocol.
    """
    serializer_class = ExecutionConfigSerializer
    queryset = Execution.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status = 'C')

class ExecutionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates or deletes a given execution. 
    
    The config is validated against JSON schema of the protocol.
    Update and delete are only possible for executions, that have not been enqueued (are in configured state - C).
    It is only possble to update config of the execution.
    """
    serializer_class = ExecutionSerializer
    queryset = Execution.objects.all()
    lookup_field = 'id'

class ExecutionStart(views.APIView):
    """
    Starts a configured execution. 
    
    Status is changed to Q - "Queued".
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

class AppratusView(generics.RetrieveAPIView):
    """
    Retrieves an information about a given apparatus.

    Retrieves an information about a given apparatus.
    """
    serializer_class = ApparatusSerializer
    queryset = Apparatus.objects.all()
    lookup_field = 'id'

class NextExecution(generics.RetrieveAPIView):
    """
    Returns the earliest started execution.

    This is supposed to be the next execution that the apparatus should perform.

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_object(self):
        obj = Execution.objects.filter(status='Q', apparatus_id=self.kwargs['id']).order_by('start').first()
        if obj:
            self.check_object_permissions(self.request, obj)
            obj.status = 'R' #TODO!
            obj.save()
        return obj   

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
    Adds a measurement result to a given execution.

    Adding a measurement with result_type "f" will automatically stop the execution.

    **APPARATUS AUTHENTICATION REQUIRED**
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
    Returns a list of all results for a given execution_id.

    Unpaginated, may be long.
    """
    serializer_class = ResultSerializer
    
    def get_queryset(self):
        return Result.objects.filter(execution_id=self.kwargs['id'], result_type='f')

class ResultListFiltered(generics.ListAPIView):
    """
    Returns a list of all results for a given execution, with id greater or equal to last_id.

    This allows you to limit the size of the result list to only view most recent results.
    """
    serializer_class = ResultSerializer
    
    def get_queryset(self):
        return Result.objects.filter(execution_id=self.kwargs['id'], pk__gte=self.kwargs['last_id'])


class ExecutionStatusSerializer(serializers.ModelSerializer):
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
    Changes or retrieves the status of a given execution.

    It is only possible to change state of running execution (R) to either finished (F) or error (E).

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionStatusSerializer
    queryset = Execution.objects.all()
    lookup_field='id'

class ExecutionQueue(generics.ListAPIView):
    """
    Retrieves a current execution queue for the apparatus.

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_queryset(self):
        return Execution.objects.filter(state='Q', apparatus_id=self.kwargs['apparatus_id']).order_by('queue_time')