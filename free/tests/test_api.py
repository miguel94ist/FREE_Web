from django.test import TestCase
from django.test import Client
from free.models import *
import json

def setup_fixtures(self):
    self.user = User.objects.create_user('user', 'em@a.il', 'password')
    self.user.save()

    self.experiment = Experiment(
        name = 'TestExperiment',
        description = 'X',
        scientific_area = 'X',
        lab_type = 'X'
    )
    self.experiment.save()

    self.apparatus = Apparatus(
        experiment = self.experiment,
        location = 'Prague',
        secret = 'secret_code',
        owner = 'Somebody'
    )
    self.apparatus.save()

    self.basic_protocol = Protocol(
        experiment = self.experiment,
        name = 'Basic protocol',
        config = {"type": "object"}
    )
    self.basic_protocol.save()

    self.protocol_with_schema = Protocol(
        experiment = self.experiment,
        name = 'Test',
        config = {"type": "object", "properties": {"displacement": {"type": "number", "description": "user name", "minimum": 5, "maximum": 20}, "enumerator": {"type": "string", "enum": ["A", "B"]}}, "required": ["displacement", "enumerator"]}
    )
    self.protocol_with_schema.save()

    self.apparatus.protocols.add(self.protocol_with_schema)
    self.apparatus.protocols.add(self.basic_protocol)
    self.apparatus.save()

    self.client = Client()
    login_result = self.client.login(username='user', password='password')
    self.assertEqual(login_result, True)


class ExecutionAPI(TestCase):
    def setUp(self):
        setup_fixtures(self)

    def test_configure_execution_success(self):
        response = self.client.post('/api/v1/execution', {
            'apparatus': self.apparatus.pk, 
            'protocol': self.basic_protocol.pk, 
            'config': {}}
        )
        self.assertEqual(response.status_code, 201)
        response = json.loads(response.content)

        execution = Execution.objects.get(pk=response["id"])
        self.assertEqual(execution.status, 'C')
        self.assertEqual(execution.user, self.user)
        self.assertEqual(execution.apparatus, self.apparatus)

    def test_configure_execution_foreign_key_fail(self):
        """Ensures that the FKs are validated"""
        response = self.client.post('/api/v1/execution', {
            'apparatus': 999, 
            'protocol': self.basic_protocol.pk, 
            'config': {}}
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/v1/execution', {
            'apparatus': self.apparatus, 
            'protocol': 999, 
            'config': {}}
        )
        self.assertEqual(response.status_code, 400) 

    def test_execution_flow(self):
        # Configure an execution
        response = self.client.post('/api/v1/execution', {
            'apparatus': self.apparatus.pk, 
            'protocol': self.basic_protocol.pk, 
            'config': {}}
        )
        self.assertEqual(response.status_code, 201)
        response = json.loads(response.content)
        execution_id = response["id"]

        # Check if status = C
        response = self.client.get('/api/v1/execution/' + str(execution_id) + '/status')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response["status"], 'C')
        self.assertEqual(len(response),1)

        # Run execution
        response = self.client.put('/api/v1/execution/' + str(execution_id))
        self.assertEqual(response.status_code, 200)

        # Check if status is R in database
        execution = Execution.objects.get(pk=execution_id)
        self.assertEqual(execution.status, 'R')

        # Check that it cannot be run again
        response = self.client.put('/api/v1/execution/' + str(execution_id))
        self.assertEqual(response.status_code, 400)

        # Check that we fail on non-existing execution id
        response = self.client.put('/api/v1/execution/999')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/v1/execution/' + str(execution_id) + '/status')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response["status"], 'R')
        self.assertEqual(len(response),1)

        response = self.client.get('/api/v1/execution/999/status')
        self.assertEqual(response.status_code, 404)


