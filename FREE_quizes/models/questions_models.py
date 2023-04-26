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

from .quiz_models import Question
from free.models import Result
from free.views.api import ResultSerializer
import importlib



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


def verify_mc():
    return True
@python_2_unicode_compatible
class Essay_Question(Question):

    rounding = models.BooleanField(
        blank=False, default=False,
        verbose_name=_("Rounding"),
        help_text=_("Will this question be rounded to a decimal case"))


    verif_function = models.CharField(max_length=100,
                               blank=True,
                               help_text=_("Enter the name of the function"
                                           "that will correct the question"),
                               verbose_name=_('Function name'))

    outer_locals = locals()


    def check_if_correct(self, user_answer,  current_quiz, execution, decimal_places):

        if user_answer is None:
            return False
        try:
            if self.verif_function != '':
                module = importlib.import_module('FREE_quizes.quizes_code')
                m = getattr(module, current_quiz.url)
                f = getattr(m, self.verif_function)
    #            if_correct = self.outer_locals[self.verif_function](self,guess,  execution,decimal)
                if_correct = f(self , user_answer, decimal_places, current_quiz, execution)
            else:
                if_correct = True                                                  
        except KeyError:
            if_correct = False
            print("Wrong verif_function name in question model")

        return if_correct


    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)

    def __str__(self):
        return self.content



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
        ordering = ['category']

class MCQuestion(Question):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which multichoice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))

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
