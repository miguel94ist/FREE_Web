from binascii import Incomplete
import random
from unicodedata import category
from urllib import request

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView

from .forms import QuestionForm, EssayForm, Experiment_ExectionForm
from .models import Quiz, Category, Progress, Sitting, Question, Essay_Question
from FREE_quizes.models.questions_models import Experiment_Execution

from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView

from model_utils.managers import InheritanceManager

from free.models import *
from jsf import JSF
import json

class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


class QuizListTable(Table):
    action = TemplateColumn(template_name='FREE_quizes/quiz_link.html')

    class Meta:
        model = Quiz
        fields = ['title', 'category', 'exam_paper', 'single_attempt']    

class QuizListView(SingleTableView):
    template_name = 'FREE_quizes/quiz_list.html'
    table_class = QuizListTable
    queryset = Quiz.objects.all().filter(draft=False)

class SittingListTable(Table):
    quiz_title = Column(accessor='quiz.title',verbose_name='Quiz Title')
    max_score = Column(accessor='get_max_score',verbose_name='Max Score')
    percent = Column(accessor='get_percent_correct',verbose_name='Percent')
    attempt = Column(accessor='id',verbose_name='Attempt #')

    class Meta:
        model = Sitting
        fields = (
            ['attempt','quiz_title', 'current_score', 'max_score', 'percent'])    

class SittingListView(SingleTableView):
    template_name = 'FREE_quizes/progress_list.html'
    table_class = SittingListTable
    def get_queryset(self):
        return Sitting.objects.filter(user=self.request.user,complete=True)

    def get_context_data(self, **kwargs):
        context = super(SittingListView,self).get_context_data(**kwargs)
        context['table_incomplete'] = (
            QuizIncompletePListTable(Sitting.objects.filter
            (user=self.request.user,complete=False),prefix="1-"))
        return context

#######################################

class QuizIncompletePListTable(Table):
    action = TemplateColumn(template_name='FREE_quizes/incomplete_link.html')
    q_left = Column(accessor='questions_left',verbose_name='Questions Left')
    q_total = Column(accessor='get_max_score',verbose_name='Total Questions')
    category = Column(accessor='category',verbose_name='Category')

    class Meta:
        model = Sitting
        fields = ['user','quiz','category','q_left','q_total']    
        
class QuizIncompleteListView(SingleTableView):
    template_name = 'FREE_quizes/incomplete_list.html'
    table_class = QuizIncompletePListTable
    def get_queryset(self):
        return Sitting.objects.filter(user=self.request.user,complete=False)


class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CategoriesListView(ListView):
    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'FREE_quizes/view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)


class QuizUserProgressView(TemplateView):
    template_name = 'FREE_quizes/progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, _ = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        return context


class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] =\
            context['sitting'].get_questions(with_answers=True)
        return context

class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'FREE_quizes/question.html'
    result_template_name = 'FREE_quizes/result.html'
    single_complete_template_name = 'FREE_quizes/single_complete.html'
    not_submited_template_name = 'FREE_quizes/send_result.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        try:
            self.logged_in_user = self.request.user.is_authenticated()
        except TypeError:
            self.logged_in_user = self.request.user.is_authenticated

        context = {}
        if self.request.session.get('lti_login') is not None:
            context['base'] = "free/base_stripped.html"
            context['lti'] = True
        else:
            context['lti'] = False


        if self.logged_in_user:
            self.sitting = Sitting.objects.unsent_sitting(request.user,self.quiz)
            if (self.sitting is False 
                or self.request.session.get('lti_login') is None):
                self.sitting = Sitting.objects.user_sitting(request.user,
                                                        self.quiz)
            else:
                score_send = self.sitting.get_percent_correct/100
                context['quiz']= self.quiz
                context['score']= self.sitting.get_current_score
                context['max_score']= self.sitting.right_max_score
                context['percent']= self.sitting.get_percent_correct
                context['sitting']= self.sitting
                context['score_send']= score_send
                context['app_name']= __package__.rsplit('.', 1)[-1]
                

                print("context:",context)
                print("app name:",__package__.rsplit('.', 1)[-1])
                return render(request, self.not_submited_template_name, context)
        else:
            self.sitting = self.anon_load_sitting()

        if self.sitting is False:
            return render(request, self.single_complete_template_name, context)

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()
        else:
            self.question = self.anon_next_question()
            self.progress = self.anon_sitting_progress()

        if self.question.__class__ is Essay_Question:
            form_class = EssayForm
        elif self.question.__class__ is Experiment_Execution:
            form_class = Experiment_ExectionForm
        else:
            form_class = self.form_class

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
        else:
            self.form_valid_anon(form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return self.final_result_anon()

        self.request.POST = {}


        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        if self.question.__class__ is Experiment_Execution:
            context['apparatus'] = self.question.category.apparatus_protocol
            context['protocol'] = self.question.category.apparatus_protocol
            if self.question.sub_category == 'Fetch':
                context['question_type'] = "FETCH"
                random_exec = self.get_random_execution(context['protocol'])
                context['execution_id'] = random_exec.pk
            else:
                if not self.sitting.execution:
                    config_generator = JSF(context['protocol'].config)
                    config = config_generator.generate()
                    context['sample_config'] = config
                    context['question_type'] = "CREATE"
                else:
                    context['question_type'] = "FETCH"
                    context['execution_id'] = self.sitting.execution
        else:
            context['question_type'] = self.question.question_type()
            pass

        context['quiz'] = self.quiz
        context['execution'] = self.sitting.execution
        if self.question.__class__ is Essay_Question:       
            context['decimal_cases'] = self.question.decimal_precision



        if self.request.session.get('lti_login') is not None:
            context['base'] = "free/base_stripped.html"
            context['lti'] = True
        else:
            context['base'] = "free/base.html"
            context['lti'] = False

        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        if self.sitting.execution != None:
            context['execution_id'] = self.sitting.execution.id
        context['execution_json'] = {}
        context['final_result'] = {}
        #self.sitting.decimal_precision = random.randint(3,7)
        self.sitting.save()
        return context

    def form_valid_user(self, form):
        progress, _ = Progress.objects.get_or_create(user=self.request.user)
        if self.question.__class__ is Experiment_Execution:
            if self.question.sub_category == 'Fetch':
                execution_id = self.request.POST.get('execution_id')
                progress.update_score(self.question, 1, 1)
                guess = None
                is_correct = True
                self.sitting.add_execution(execution_id)

                self.sitting.add_user_answer(self.question, guess)
                self.sitting.remove_first_question()
            else:
                if self.sitting.execution_id and self.sitting.execution.status == 'F':
                    guess = None
                    is_correct = True
                    progress.update_score(self.question, 1, 1)

                    self.sitting.add_user_answer(self.question, guess)
                    self.sitting.remove_first_question()
                else:
                    guess = None
                    is_correct = True
                    execution_id = self.request.POST.get('execution_id')
                    self.sitting.add_execution(execution_id)     
        else:
            guess = form.cleaned_data['answer']
            if self.request.POST.get('protocol_id') != None:
                id = self.request.POST.get(protocol_id)
                random_exec = self.get_random_execution(int(id))
                random_result = Result.objects.get(execution=random_exec.pk,result_type='f')
            
                random_exec.pk = None
                random_exec.user = self.sitting.user
                random_exec.save()
                self.sitting.execution = random_exec
                
                random_result.pk = None
                random_result.execution = random_exec
                random_result.save()

            if self.question.__class__ is Essay_Question:
                is_correct = (
                    self.question.check_if_correct(guess,self.quiz, self.sitting.execution
                                                ,self.question.decimal_precision))
            else:
                is_correct = self.question.check_if_correct(guess)

            if is_correct is True:
                self.sitting.add_to_score(1)
                progress.update_score(self.question, 1, 1)
            else:
                self.sitting.add_incorrect_question(self.question)
                progress.update_score(self.question, 0, 1)

            self.sitting.add_user_answer(self.question, guess)
            self.sitting.remove_first_question()

        if self.quiz.show_answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                            'previous_outcome': is_correct,
                            'previous_question': self.question,
                            'answer': self.question.get_answers(),
                            'question_type': {self.question
                                            .__class__.__name__: True}}
        else:
            self.previous = {}


    def final_result_user(self):
        score_send = self.sitting.get_percent_correct/100
        answer = json.loads(self.sitting.user_answers)
        answered_questions = self.sitting._question_ids()
        incorrect_questions = self.sitting.get_incorrect_questions
        details = []
        for q_id in answered_questions :
            
            q_answ = answer[str(q_id)]
            q = Question.objects.get(pk=q_id)
            if q_id not in incorrect_questions:
                q_correct = True
            else:
                q_correct = False
            q_details = {'id': q_id, 
                         'ans': q_answ,
                         'content': q.content,
                         'correct': q_correct, 
                         'expl': q.explanation}
            details.append(q_details)
        results = {
            'details': details,
            'quiz': self.quiz,
            'score': self.sitting.get_current_score, 
            'max_score': self.sitting.right_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
            'score_send': score_send,
            'app_name': __package__.rsplit('.', 1)[-1]
        }
        self.sitting.mark_quiz_complete()
        if self.request.session.get('lti_login') is not None:
            results['lti'] = True
        else:
            results['lti'] = False

        if self.quiz.show_answers_at_end:
            results['questions'] =\
                self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] =\
                self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False:
            self.sitting.delete()


        return render(self.request, self.result_template_name, context = results)

    def get_random_execution(self,appar_id):
        exe_query = Execution.objects.filter(protocol_id=appar_id,status='F')
        pks = list(exe_query.values_list('id',flat=True))
        print("pks:",pks)
        random_pk = random.choice(pks)
        print("rabnd pks:",random_pk)
        return exe_query.get(pk=random_pk)

    def anon_load_sitting(self):
        if self.quiz.single_attempt is True:
            return False

        if self.quiz.anon_q_list() in self.request.session:
            return self.request.session[self.quiz.anon_q_list()]
        else:
            return self.new_anon_quiz_session()

    def new_anon_quiz_session(self):
        """
        Sets the session variables when starting a quiz for the first time
        as a non signed-in user
        """
        self.request.session.set_expiry(259200)  # expires after 3 days
        questions = self.quiz.get_questions()
        question_list = [question.id for question in questions]

        if self.quiz.random_order is True:
            random.shuffle(question_list)

        if self.quiz.max_questions and (self.quiz.max_questions
                                        < len(question_list)):
            question_list = question_list[:self.quiz.max_questions]

        # session score for anon users
        self.request.session[self.quiz.anon_score_id()] = 0

        # session list of questions
        self.request.session[self.quiz.anon_q_list()] = question_list

        # session list of question order and incorrect questions
        self.request.session[self.quiz.anon_q_data()] = dict(
            incorrect_questions=[],
            order=question_list,
        )

        return self.request.session[self.quiz.anon_q_list()]

    def anon_next_question(self):
        next_question_id = self.request.session[self.quiz.anon_q_list()][0]
        return Question.objects.get_subclass(id=next_question_id)

    def anon_sitting_progress(self):
        total = len(self.request.session[self.quiz.anon_q_data()]['order'])
        answered = total - len(self.request.session[self.quiz.anon_q_list()])
        return (answered, total)

    def form_valid_anon(self, form):
        guess = form.cleaned_data['answer']
        is_correct = (
            self.question.check_if_correct(guess,self.sitting.execution))

        if is_correct:
            self.request.session[self.quiz.anon_score_id()] += 1
            anon_session_score(self.request.session, 1, 1)
        else:
            anon_session_score(self.request.session, 0, 1)
            self.request\
                .session[self.quiz.anon_q_data()]['incorrect_questions']\
                .append(self.question.id)

        self.previous = {}
        if self.quiz.show_answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answer': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}

        self.request.session[self.quiz.anon_q_list()] =\
            self.request.session[self.quiz.anon_q_list()][1:]

    def final_result_anon(self):
        score = self.request.session[self.quiz.anon_score_id()]
        q_order = self.request.session[self.quiz.anon_q_data()]['order']
        max_score = len(q_order)
        percent = int(round((float(score) / max_score) * 100))
        session, session_possible = anon_session_score(self.request.session)
        if score == 0:
            score = "0"
        results = {
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'session': session,
            'possible': session_possible
        }

        del self.request.session[self.quiz.anon_q_list()]

        if self.quiz.show_answers_at_end:
            results['questions'] = sorted(
                self.quiz.question_set.filter(id__in=q_order)
                                      .select_subclasses(),
                key=lambda q: q_order.index(q.id))

            results['incorrect_questions'] = (
                self.request
                    .session[self.quiz.anon_q_data()]['incorrect_questions'])
        else:
            results['previous'] = self.previous

        del self.request.session[self.quiz.anon_q_data()]

        return render(self.request, 'FREE_quizes/result.html', results)



def anon_session_score(session, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score.

    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score
                                    without modification

    Left this as an individual function for unit testing
    """
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]
