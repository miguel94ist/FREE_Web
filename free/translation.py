from modeltranslation.translator import translator, TranslationOptions
from free.models import *

class ApparatusTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'scientific_area', 'lab_type',)
translator.register(ApparatusType, ApparatusTypeTranslationOptions)

class ApparatusTranslationOptions(TranslationOptions):
    fields = ('location','description',)
translator.register(Apparatus, ApparatusTranslationOptions)

class ProtocolTranslationOptions(TranslationOptions):
    fields = ('name','description',)
translator.register(Protocol, ProtocolTranslationOptions)