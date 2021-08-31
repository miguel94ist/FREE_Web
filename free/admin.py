from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin, TranslationAdmin

from free.models import *

admin.site.site_title = _('FREE Administration')
admin.site.site_header = _('FREE Administration')
admin.site.index_title = _('FREE Administration')

class ExperimentAdmin(TabbedTranslationAdmin):
    pass
admin.site.register(Experiment, ExperimentAdmin)

class ApparatusAdmin(TabbedTranslationAdmin):
    pass
admin.site.register(Apparatus, ApparatusAdmin)

class StatusAdmin(admin.ModelAdmin):
    pass
admin.site.register(Status, StatusAdmin)

class ProtocolAdmin(admin.ModelAdmin):
    pass
admin.site.register(Protocol, ProtocolAdmin)

class ExecutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Execution, ExecutionAdmin)

class ResultAdmin(admin.ModelAdmin):
    pass
admin.site.register(Result, ResultAdmin)


