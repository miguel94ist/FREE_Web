from modeltranslation.translator import translator, TranslationOptions
from free.models import *

class ExperimentTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'scientific_area', 'lab_type',)
translator.register(Experiment, ExperimentTranslationOptions)

class ApparatusTranslationOptions(TranslationOptions):
    fields = ('location','description',)
translator.register(Apparatus, ApparatusTranslationOptions)

class ProtocolTranslationOptions(TranslationOptions):
    fields = ('name','description',)
translator.register(Protocol, ProtocolTranslationOptions)