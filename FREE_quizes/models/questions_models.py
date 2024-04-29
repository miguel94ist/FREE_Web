from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import (
    MaxValueValidator, validate_comma_separated_integer_list,
)

from django.utils.translation import gettext_lazy as _
from six import python_2_unicode_compatible
from django.conf import settings

from FREE_quizes.quizes_code import *
from model_utils.managers import InheritanceManager

#from .quiz_models import Question
from free.models import Result, Execution
from free.views.api import ResultSerializer

import importlib


@python_2_unicode_compatible
class Question(models.Model):
    """
    Base class for all question types.
    Shared properties placed here.
    """

#    quiz = models.ManyToManyField(Quiz,
##                                  verbose_name=_("Quiz"),
#                                  blank=True)

#    category = models.ForeignKey(Category,
#                                 verbose_name=_("Category"),
#                                 related_name='%(app_label)s_%(class)s_category',
#                                 blank=True,
#                                 null=True,
#                                 on_delete=models.CASCADE)

    evaluated = models.BooleanField(default=True, blank=True,
                                   verbose_name=_("To be evaluated"))
    evaluationWeight = models.PositiveIntegerField(default=1, blank=True,
                                   verbose_name=_("Evaluation Weigth"))

    figure = models.ImageField(upload_to='uploads/%Y/%m/%d',
                               blank=True,
                               null=True,
                               verbose_name=_("Figure"))

    title = models.CharField(max_length=30,
                               blank=True,
                               help_text=_("Enter a small description of the question"),
                               verbose_name=_('Question Title'))

    internal_title = models.CharField(max_length=30,
                               blank=True,
                               help_text=_("Title to identify questin in admin"),
                               verbose_name=_('internal Title'))


    content = models.CharField(max_length=5000,
                               blank=False,
                               help_text=_("Enter the question text that "
                                           "you want displayed"),
                               verbose_name=_('Question Content'))
    #verif_function -> correctness_verification_function
    correctness_verification_function = models.CharField(max_length=100,
                               blank=True,
                               help_text=_("Enter the name of the function"
                                           "that will evaluate the question"),
                               verbose_name=_('Correctness Verification Name'))


    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text=_("Explanation to be shown "
                                               "after the question has "
                                               "been answered."),
                                   verbose_name=_('Explanation'))

    
#    priority = models.PositiveIntegerField(
#        blank=True, null=True, verbose_name=_("Priority"),
#        help_text=_("Question priority to show in quiz, smaller means bigger priority"))

    objects = InheritanceManager()

    def get_answers(self):
        return False

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
#        ordering = [F('priority').asc(nulls_last=True)]

    def __str__(self):
        return self.internal_title
    def question_type(self):
        
        pass



ANSWER_ORDER_OPTIONS = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)

@python_2_unicode_compatible
class Experiment_Execution(Question):
    class RetrieveMethod(models.TextChoices):
        CREATE = "Create", _("Create")
        FETCH = "Fetch", _("Fetch")

    sub_category = models.CharField(
        max_length=6,
        choices=RetrieveMethod.choices,
    )
    class Meta:
        verbose_name = _("Experiment Execution")
        verbose_name_plural = _("Experiment Executions")

    config_function = models.CharField(max_length=100,
                               blank=True,
                               help_text=_("Enter the name of the function"
                                           "that will update the default expertiment configuration"),
                               verbose_name=_('Experiment default configuration function'))
    
    def update_experiment_input(self, config, current_quiz):
        try:
            module = importlib.import_module('FREE_quizes.quizes_code')
            m = getattr(module, current_quiz.url)
            f = getattr(m, self.config_function)
            config = f(config)
        except :
            pass

        return config


    assessement_parameters_function = models.CharField(max_length=100,
                               blank=True,
                               help_text=_("Enter the name of the function"
                                           "that will generate different parameters for the assessemnsts"),
                               verbose_name=_('Experiment parameters function'))

    def get_student_experiment_parameters(self, current_quiz, current_question, user_answers):
        try:
            module = importlib.import_module('FREE_quizes.quizes_code')
            m = getattr(module, current_quiz.url)
            f = getattr(m, current_question.assessement_parameters_function)
            parameters = f(user_answers)
            return parameters
        except :
            return None
        
    def check_if_correct(self, current_execution, student_parameters):
        if student_parameters:  
            for param in student_parameters:
                param_name = param['name']
                student_value = current_execution.config[param['name']]
                print(param['value'],  student_value)
                if param['value'] !=  student_value:
                    print("wrong")
                    return False
        return True
            




@python_2_unicode_compatible
class Essay_Question(Question):

    decimal_precision = models.PositiveIntegerField(default=2,
                                            verbose_name=_("Decimal Precision"))

    multiple_answer_fields = models.JSONField("Student answeres names", 
                                          blank = True, null=True, 
                                          default=None)

    outer_locals = locals()

    def question_type(self):
        return "ESSAY"


    def check_if_correct(self, user_answer,  current_quiz, last_execution, executions, decimal_places):

        if user_answer is None:
            return False
        try:
            if self.correctness_verification_function != '':
                module = importlib.import_module('FREE_quizes.quizes_code')
                m = getattr(module, current_quiz.url)
                f = getattr(m, self.correctness_verification_function)
                if_correct = f(self , user_answer, decimal_places, current_quiz, last_execution, executions)
            else:
                if_correct = True                                                  
        except KeyError:
            if_correct = False
            print("Wrong correctness_verification_function name in question model")

        return if_correct


    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)




    class Meta:
        verbose_name = _("Open ended question")
        verbose_name_plural = _("Open ended questions")

class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Tick this if the question "
                                              "is true. Leave it blank for"
                                              " false."),
                                  verbose_name=_("Correct"))

    def question_type(self):
        return "TF"

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'True'},
                {'correct': self.check_if_correct("False"),
                 'content': 'False'}]

    def get_answers_list(self):
        return [(True, True), (False, False)]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = _("True/False Question")
        verbose_name_plural = _("True/False Questions")
        #ordering = ['category']

class MCQuestion(Question):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which multichoice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))

    def question_type(self):
        return "MC"

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


@python_2_unicode_compatible
class Answer(models.Model):
    question = models.ForeignKey(MCQuestion, 
                                 verbose_name=_("Question"), 
                                 related_name='%(app_label)s_%(class)s_question',
                                 on_delete=models.CASCADE)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Enter the answer text that "
                                           "you want displayed"),
                               verbose_name=_("Content"))

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Is this a correct answer?"),
                                  verbose_name=_("Correct"))

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
