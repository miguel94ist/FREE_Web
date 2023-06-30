from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from FREE_quizes.models.questions_models import Experiment_Execution
from FREE_quizes.models.quiz_models import Quiz
from django.conf import settings

from .models import *

class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    """
    below is from
    http://stackoverflow.com/questions/11657682/
    django-admin-interface-using-horizontal-filter-with-
    inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial =\
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    form = QuizAdminForm

    list_display = ('title',  )
    list_filter = ()
    search_fields = ('description', 'category', )
    summernote_fields = ('description')

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category', 'apparatus_type')



class MCQuestionAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'content', 'category', )
    list_filter = ('category',)
    fields = ('title', 'content', 'evaluated', 'evaluationWeight',
              'figure',  'explanation', 'priority', 'answer_order')

    search_fields = ('content', 'explanation')

    inlines = [AnswerInline]
    summernote_fields = ('content', 'explanation')


class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )


class TFQuestionAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'content', 'category', )
    list_filter = ('category',)
    fields = ('title', 'content',  'evaluated',  'evaluationWeight',
              'figure',  'explanation','priority', 'correct',)

    search_fields = ('content', 'explanation')
    summernote_fields = ('content')

class EssayQuestionAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'content', 'category', )
    list_filter = ('category',)
    fields = ('title', 'content',  'evaluated',  'evaluationWeight',  'explanation', 'verif_function','priority','decimal_precision')
    search_fields = ('content', 'explanation')
    summernote_fields = ('content',   'explanation')

class  Experiment_ExecutionAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    list_display = ('title', 'content', 'category')
    list_filter = ('category',)
    fields = ('title', 'content','assessement_parameters_function', 'category', 'sub_category', 'config_function', 'evaluated',  'evaluationWeight', 'explanation', 'priority')
    search_fields = ('content', 'explanation')
    summernote_fields = ('content',   'explanation')

class SittingAdmin(admin.ModelAdmin):
    list_display =('user','complete')

class FREE_quizes_AdminSite(admin.AdminSite):
    site_header = "FREE quizes admin"
    site_title = "FREE quizes Portal"

FREE_quizes_admin_site = FREE_quizes_AdminSite(name='FREE_quizes_admin')

FREE_quizes_admin_site.register(Quiz, QuizAdmin)
FREE_quizes_admin_site.register(Category, CategoryAdmin)
FREE_quizes_admin_site.register(MCQuestion, MCQuestionAdmin)
FREE_quizes_admin_site.register(Progress, ProgressAdmin)
FREE_quizes_admin_site.register(TF_Question, TFQuestionAdmin)
FREE_quizes_admin_site.register(Essay_Question, EssayQuestionAdmin)
FREE_quizes_admin_site.register(Sitting, SittingAdmin)
FREE_quizes_admin_site.register(Experiment_Execution, Experiment_ExecutionAdmin)