from rest_framework import permissions
from free.models import Execution, Result, Apparatus

class ApparatusOnlyAccess(permissions.BasePermission):
    message = 'Please provide a valid secret in the Authentication HTTP header.'

    def has_object_permission(self, request, view, obj):
        if 'Authentication' in request.headers:
            if isinstance(obj, Execution):
                return request.headers['Authentication'] == obj.apparatus.secret
            if isinstance(obj, Result):
                return request.headers['Authentication'] == obj.execution.apparatus.secret
            if isinstance(obj, Apparatus):
                return request.headers['Authentication'] == obj.secret
        return False
        