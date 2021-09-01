from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin, TranslationAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from free.models import *

admin.site.site_title = _('FREE Administration')
admin.site.site_header = _('FREE Administration')
admin.site.index_title = _('FREE Administration')

class ExperimentAdmin(TabbedTranslationAdmin):
    pass
admin.site.register(Experiment, ExperimentAdmin)

class ApparatusAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['protocols'].queryset = Protocol.objects.filter(experiment=kwargs['instance'].experiment)
        else:
            self.fields['protocols'].widget = self.fields['protocols'].hidden_widget()

class ApparatusAdmin(TabbedTranslationAdmin):
    form = ApparatusAdminForm
    list_filter = ['experiment']
admin.site.register(Apparatus, ApparatusAdmin)

class StatusAdmin(admin.ModelAdmin):
    list_display = ['apparatus', 'status', 'time']
    list_filter = ['apparatus', 'status', 'time']
admin.site.register(Status, StatusAdmin)

class ProtocolAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'experiment']
admin.site.register(Protocol, ProtocolAdmin)

class ExecutionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'apparatus', 'start', 'end']
    list_filter = ['apparatus', 'apparatus__experiment']
admin.site.register(Execution, ExecutionAdmin)

class ResultAdmin(admin.ModelAdmin):
    list_display = ['value','result_type', 'time']
    list_filter = ['execution__apparatus', 'time']
admin.site.register(Result, ResultAdmin)

class UserProfileInline(admin.StackedInline):
    model=UserProfile
    can_delete=False

class UserAdmin(BaseUserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.inlines = (UserProfileInline,)
        return super().get_form(request, obj, **kwargs)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


