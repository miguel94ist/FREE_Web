from modeltranslation.translator import translator, TranslationOptions
from FREEquizes.models.quiz_models import *
from FREEquizes.models.questions_models import *


class QuizTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'fail_text', 'success_text')
translator.register(Quiz, QuizTranslationOptions)

class QuestionTranslationOptions(TranslationOptions):
    fields = ('title', 'content','explanation',)
translator.register(Question, QuestionTranslationOptions)

class Experiment_ExecutionTranslationOptions(TranslationOptions):
    pass
#    fields = ('content','explanation',)
translator.register(Experiment_Execution, Experiment_ExecutionTranslationOptions)

class Essay_QuestionTranslationOptions(TranslationOptions):
    pass
#    fields = ('content','explanation',)
translator.register(Essay_Question, Essay_QuestionTranslationOptions)

class MCQuestionTranslationOptions(TranslationOptions):
    pass
#    fields = ('content','explanation',)
translator.register(MCQuestion, MCQuestionTranslationOptions)

class TF_QuestionTranslationOptions(TranslationOptions):
    pass
#    fields = ('content','explanation',)
translator.register(TF_Question, TF_QuestionTranslationOptions)
