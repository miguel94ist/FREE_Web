from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from FREE_quizes.models.questions_models import Experiment_Execution

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


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title',  )
    list_filter = ()
    search_fields = ('description', 'category', )


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category', 'apparatus_type')


# class SubCategoryAdmin(admin.ModelAdmin):
#     # search_fields = ('sub_category', )
#     # list_display = ('sub_category', 'category',)
#     # # list_filter = ('category',)


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'evaluated', 
              'figure',  'explanation', 'priority', 'answer_order')

    search_fields = ('content', 'explanation')
#    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content',  'evaluated', 
              'figure',  'explanation','priority', 'correct',)

    search_fields = ('content', 'explanation')
#    filter_horizontal = ('quiz',)


class EssayQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content',  'evaluated',   'explanation', 'verif_function','priority','rounding')
    search_fields = ('content', 'explanation')
#    filter_horizontal = ('quiz',)


class  Experiment_ExecutionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'sub_category',  'evaluated', 'explanation', 'priority')
    search_fields = ('content', 'explanation')
#    filter_horizontal = ('quiz',)  

class SittingAdmin(admin.ModelAdmin):
    list_display =('user','complete')

class FREE_quizes_AdminSite(admin.AdminSite):
    site_header = "FREE quizes admin"
    site_title = "FREE quizes Portal"

FREE_quizes_admin_site = FREE_quizes_AdminSite(name='FREE_quizes_admin')

FREE_quizes_admin_site.register(Quiz, QuizAdmin)
FREE_quizes_admin_site.register(Category, CategoryAdmin)
# FREE_quizes_admin_site.register(SubCategory, SubCategoryAdmin)
FREE_quizes_admin_site.register(MCQuestion, MCQuestionAdmin)
FREE_quizes_admin_site.register(Progress, ProgressAdmin)
FREE_quizes_admin_site.register(TF_Question, TFQuestionAdmin)
FREE_quizes_admin_site.register(Essay_Question, EssayQuestionAdmin)
FREE_quizes_admin_site.register(Sitting, SittingAdmin)
FREE_quizes_admin_site.register(Experiment_Execution, Experiment_ExecutionAdmin)