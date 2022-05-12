from rest_framework import permissions
from free.models import Execution, Result, Apparatus
from django.utils import timezone

class ApparatusOnlyAccess(permissions.BasePermission):
    message = 'Please provide a valid secret in the Authentication HTTP header.'

    def has_object_permission(self, request, view, obj):
        if 'Authentication' in request.headers:
            if isinstance(obj, Execution):
                if request.headers['Authentication'] == obj.apparatus.secret:
                    obj.apparatus.last_online = timezone.now()
                    obj.apparatus.save()
                    return True
            if isinstance(obj, Result):
                if request.headers['Authentication'] == obj.execution.apparatus.secret:
                    obj.execution.apparatus.last_online = timezone.now()
                    obj.execution.apparatus.save()
                    return True
            if isinstance(obj, Apparatus):
                if request.headers['Authentication'] == obj.secret:
                    obj.last_online = timezone.now()
                    obj.save()
                    return True
                    
        return False
        