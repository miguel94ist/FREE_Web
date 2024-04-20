from binascii import Incomplete
import random
from unicodedata import category
from urllib import request

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.shortcuts import redirect

from .forms import QuestionForm, EssayForm, Experiment_ExectionForm, Navigate_quizz
from .models import Quiz, Progress, Sitting, Question, Essay_Question
from FREE_quizes.models.questions_models import Experiment_Execution

from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView

from model_utils.managers import InheritanceManager

from free.models import *
from jsf import JSF
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

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

class QuizListView(LoginRequiredMixin, SingleTableView):
    template_name = 'FREE_quizes/quiz_list.html'
    table_class = QuizListTable
    def get_queryset(self):
        if self.request.user.is_superuser:            
            queryset = Quiz.objects.all().filter(Q(draft=True) | Q(visible=True)) 
        else:
            queryset = Quiz.objects.all().filter(draft=False, visible=True) 
        return queryset

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


#class CategoriesListView(ListView):
#    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'FREE_quizes/view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        #self.category = get_object_or_404(
        #    Category,
        #    category=self.kwargs['category_name']
        #)

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
        #code executed when receives a request FREE_quizes/xxx/take (1)
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        try:
            self.logged_in_user = self.request.user#.is_authenticated()
        except TypeError:
            raise PermissionDenied

        context = {}
        if self.request.session.get('lti_login') is not None:
            context['base'] = "free/base_stripped.html"
            context['lti'] = True
        else:
            context['base'] = "free/base.html"
            context['lti'] = False

        #get the current sitting for the user
        #or creates a new one
        try:
            self.sitting = Sitting.objects.get_currrent_sitting(request.user,self.quiz)
        except Sitting.DoesNotExist:
            self.sitting = Sitting.objects.new_sitting(request.user,self.quiz)

        #verify if the user clicke on Archive quiz Button
        try:
            if request.POST['archive_quiz'] == 'true' and self.sitting.complete:
                self.sitting.archive_quiz()
                print('Terminating quizz')
                return redirect('FREE_quizes:quiz_index')
        except: 
            pass


        return super(QuizTake, self).dispatch(request, *args, **kwargs)
    
    def get_form(self, *args, **kwargs):



        #verify if the user clicke on terminate quiz Button
        try:
            if self.request.POST['terminate_quiz'] == 'true' and len(self.sitting.quiz.orderedQuestions.all()) == len (self.sitting.answered_questions_list):
                self.sitting.mark_quiz_complete()
                print('Terminating quizz')
        except: 
            pass

        #verify is user navigated on quiz (prev, next buttons)
        try:
            self.sitting.current_question -= int(self.request.POST['previous_step'])
            self.sitting.current_question += int(self.request.POST['next_step'])
        except:
            pass
        if self.sitting.current_question > len(self.sitting.answered_questions_list):
            self.sitting.current_question = len(self.sitting.answered_questions_list)
        if self.sitting.current_question < 0 :
            self.sitting.current_question = 0
        self.sitting.save()
        
        #get current question and progress.....
        self.question =  self.quiz.orderedQuestions.all()[self.sitting.current_question]
        self.progress = self.sitting.progress()

        #update the form and initialize relevant information
        form_class = self.form_class
        #Essay
        try:
            self.question = self.question.essay_question
            form_class = EssayForm
        except:
            pass
        
        #Experiment execution
        try:
            self.question = self.question.experiment_execution
            form_class = Experiment_ExectionForm

            #Tries to get the current execution from the sitting
            self.current_execution = None
            try:
                cur_exec_id = self.sitting.user_answers[self.sitting.current_question]["execution_id"]
                self.current_execution = Execution.objects.filter(pk = cur_exec_id)[0]
            except:
                pass

            #if the user just access this question there is no execution defined.
            if self.current_execution == None:
                #creat or fect a nex experiment
                current_experiment_info = { }
                current_apparatus = None
                protocol = self.quiz.experiments_protocol

                #fetch a random execution
                if self.question.sub_category == 'Fetch':
                    random_exec = self.get_random_execution(protocol)
                    self.current_execution = random_exec
                    #if there is an execution, saves on the sitting
                    if self.current_execution != None:
                        current_experiment_info["execution_id"] = self.current_execution.id
                        current_experiment_info["req_parameters"] = None
                        current_experiment_info['evaluated']= False
                        current_experiment_info['grade'] = 0 

                        self.sitting.user_answers.append(current_experiment_info)

                        #mark the question as already answered
                        self.sitting.answered_questions_list.append(True)
                        self.sitting.save()

                #create a new execution
                if self.question.sub_category == 'Create':
                    current_apparatus = self.find_available_apparatus()
                    if current_apparatus:
                        required_experiment_parameters = self.question.get_student_experiment_parameters(self.quiz, self.question, self.sitting.user_answers)
                        current_experiment_info["req_parameters"] = required_experiment_parameters
                        #self.sitting.current_execution_req_parameters = student_experiment_parameters
                        config_generator = JSF(protocol.config)
                        config = config_generator.generate()
                        config = self.question.update_experiment_input(config, self.quiz)

                        e = Execution()
                        e.user = self.logged_in_user
                        e.apparatus = current_apparatus
                        e.protocol = protocol
                        e.config = config
                        e.status = 'C'
                        e.save()
                        self.current_execution = e
                        current_experiment_info["execution_id"] = self.current_execution.id
                        try:
                            self.sitting.user_answers[self.sitting.current_question] = current_experiment_info
                        except:
                            self.sitting.user_answers.append(current_experiment_info)
                        self.sitting.save()
        except:
            pass

        #verify if questin was allready answered
        try:
            if self.sitting.answered_questions_list[self.sitting.current_question]:
                self.already_answered = True
            else:
                self.already_answered = False
        except:
            self.already_answered = False
     
        
        return form_class(**self.get_form_kwargs())

    def find_available_apparatus(self):
        current_apparatus = None
        if self.quiz.single_apparatus:
            #single_apparatus
            if self.sitting.apparatus == None:
                online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
                try:
                    self.sitting.apparatus = random.choice(online_apparatus)
                    current_apparatus = self.sitting.apparatus
                except:
                    pass
            else:
                current_apparatus = self.sitting.apparatus

        else:
            # differente apararyus per execution
            online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
            try:
                current_apparatus = random.choice(online_apparatus)
            except:
                pass
        return current_apparatus



    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):

        if form.__class__ != Navigate_quizz:
            ## code executed when user presses a button (continue to quiz, submit answer, restart execution, re-answer)
            
            self.form_valid_user(form)

        else:
            pass
            #self.request.POST = {}

        self.success_url = self.request.path
        return super().form_valid(form)
        return super(QuizTake, self).get(self, self.request)

    #fiil the page
    def get_context_data(self, **kwargs):
        #code executed when filling the page (2)
        
        context = super(QuizTake, self).get_context_data(**kwargs)


        context['quiz'] = self.quiz
        if self.request.session.get('lti_login') is not None:
            context['base'] = "free/base_stripped.html"
            context['lti'] = True
        else:
            context['base'] = "free/base.html"
            context['lti'] = False

        if self.sitting.complete:
            context = self.final_result_user(context)
            context['view'].template_name = context['view'].result_template_name
        else:

            context['prev_button'] = False
            context['next_button'] = False
            if self.sitting.current_question < len(self.sitting.answered_questions_list):
                context['next_button'] = True
            if self.sitting.current_question > 0:
                context['prev_button'] = True

            context['already_answered'] = self.already_answered

            if self.already_answered:
                context['question_result'] = {}
                context['question_result']['evaluated'] = self.sitting.user_answers[self.sitting.current_question]['evaluated']
                context['question_result']['answer'] = self.sitting.user_answers[self.sitting.current_question]['answer']
                context['question_result']['expected_result'] = ""
                context['question_result']['weight'] = self.sitting.user_answers[self.sitting.current_question]['evaluationWeight']
                context['question_result']['grade'] = int(self.sitting.user_answers[self.sitting.current_question]['grade'])

            if self.sitting.current_question +1 == len(self.sitting.quiz.orderedQuestions.all()):
                context['next_button'] = False
            if len(self.sitting.quiz.orderedQuestions.all()) == len(self.sitting.answered_questions_list):
                context['completed_quiz'] = True

            context['question'] = self.question
            if self.question.__class__ is Experiment_Execution:
                context['protocol'] = self.quiz.experiments_protocol
                if self.question.sub_category == 'Fetch':
                    context['question_type'] = "FETCH"
                if self.question.sub_category == 'Create':
                    context['question_type'] = "CREATE"

                if self.current_execution:
                        ## retrieve a already created execution
                    context['student_experiment_parameters'] = self.sitting.user_answers[self.sitting.current_question]['req_parameters']
                    context['question_type'] = "CREATE"
                    context['execution_id'] = self.current_execution.id
                    context['execution'] = self.current_execution
                    """            else:
                    if self.question.sub_category == 'Fetch':
                        context['question_type'] = "FETCH"
                        if self.current_execution == None:
                            random_exec = self.get_random_execution(context['protocol'])
                            self.current_execution = random_exec
                        context['execution_id'] = self.current_execution.pk
                    else:
                        if self.quiz.single_apparatus:
                            # differente apararyus per execution
                            if self.sitting.apparatus == None:
                                online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
                                try:
                                    self.sitting.apparatus = random.choice(online_apparatus)
                                    context['apparatus'] = self.sitting.apparatus
                                except:
                                    pass
                        else:
                            online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
                            try:
                                context['apparatus'] = random.choice(online_apparatus)
                            except:
                                pass

                        student_experiment_parameters = self.question.get_student_experiment_parameters(self.quiz, self.question, self.sitting.user_answers)
                        context['student_experiment_parameters'] = student_experiment_parameters
                        self.sitting.current_execution_req_parameters = student_experiment_parameters
                        config_generator = JSF(context['protocol'].config)
                        config = config_generator.generate()
                        config = self.question.update_experiment_input(config, self.quiz)

                        e = Execution()
                        e.user = self.logged_in_user
                        e.apparatus = context['apparatus'] 
                        e.protocol = context['protocol']
                        e.config = config
                        e.status = 'C'
                        e.save()
                        self.current_execution = e
                        context['question_type'] = "CREATE"
                        context['execution_id'] = self.current_execution.id
                        context['execution'] = self.current_execution

                        current_experiment_user_answer = {
                            "req_parameters": self.sitting.current_execution_req_parameters,
                            "execution_id": self.current_execution.id
                        }
                        self.sitting.user_answers.append(current_experiment_user_answer)
                        
                    ## create a new execution
                    ## generate the parameters of the execution
                    #student_experiment_parameters = self.question.get_student_experiment_parameters(self.quiz, self.question, self.sitting.user_answers)
                    #context['student_experiment_parameters'] = student_experiment_parameters
                    #self.sitting.current_execution_req_parameters = student_experiment_parameters
                    #config_generator = JSF(context['protocol'].config)
                    #config = config_generator.generate()
                    #config = self.question.update_experiment_input(config, self.quiz)
                    #context['sample_config'] = config
                    #context['question_type'] = "CREATE"

                    """


            if self.question.__class__ is Essay_Question:

                context['answered_question'] = False

                try:
                    if self.sitting.answered_questions_list[self.sitting.current_question]:
                        for f in context['form'].fields.keys():
                            context['form'].fields[f].initial = float(self.sitting.user_answers[self.sitting.current_question]['answer'][f])
                        context['answered_question'] = True
                except:
                    pass

                context['question_type'] = self.question.question_type()

                previous_executions = []        
                for ans in self.sitting.user_answers:
                    if ans['execution_id']:
                        previous_executions.append(ans['execution_id'])
                
                multiple_answer_fields = []
                for k in self.question.multiple_answer_fields.keys():
                    d = self.question.multiple_answer_fields[k].copy()
                    d['name'] = k
                    multiple_answer_fields.append(d)
                context['multiple_answer_fields'] = multiple_answer_fields
                if len(previous_executions) > 0:
                    context['execution_id'] = previous_executions[-1]
                    context['execution'] = Execution.objects.filter(id= previous_executions[-1]).first()
                if len(previous_executions) > 1:
                    context['previous_executions'] = previous_executions[:-1]

    #            if self.sitting.current_execution != None:
    #                context['execution_id'] = self.sitting.current_execution.id
    #                context['execution'] = self.sitting.current_execution
    #            else:
    #                if self.sitting.finished_executions.count()>0:
    #                    context['execution_id'] = self.sitting.finished_executions.last().id
    #                    context['execution'] = self.sitting.finished_executions.last()
                context['decimal_cases'] = self.question.decimal_precision



            context['execution_json'] = {}
            context['final_result'] = {}
            context['current_question']= self.sitting.current_question+1
            self.sitting.save()
        return context

    ## code executed when user presses a button (continue to quiz, submit answer, restart execution, re-answer)
    def form_valid_user(self, form):
        progress, _ = Progress.objects.get_or_create(user=self.request.user)


        if not self.already_answered:
            if self.question.__class__ is Experiment_Execution:
                #user presses the continue button on the experiment executions
                if False: # self.question.sub_category == 'Fetch':
                    execution_id = self.request.POST.get('execution_id')
                    progress.update_score(self.question, 1, 1)
                    guess = None
                    is_correct = True
                    self.sitting.add_execution(execution_id)
    #self.sitting.finished_executions.add(self.sitting.current_execution)
                    self.sitting.current_execution = None
                    self.sitting.add_user_answer(self.question, guess)
                    self.sitting.remove_first_question()
                else:
                    try:
                        if self.request.POST['restart_execution'] == 'true':
                            self.current_execution.delete()
                            self.current_execution = None
                            self.last_execution = None
                            self.sitting.save()
                            print('restart execution')
                    except: 
                        pass


                    if self.current_execution:# and self.sitting.current_execution.status == 'F':
                        #user presses continue to quiz
                        # exepriment is finished and we need to store:
                        # exepriment parameters: answer self.sitting.current_execution.config
                        #rewquested parameters: self.sitting.current_execution_req_parameters
                        # wether it is to be evaluated evaluated : true of false
                        # score - 0 or none
                        # 
                        try:
                            if self.request.POST['confirm_execution'] == 'true' and self.current_execution.status == 'F':
                                self.sitting.user_answers[self.sitting.current_question]['evaluationWeight'] = self.question.evaluationWeight
                                self.sitting.user_answers[self.sitting.current_question]['answer'] = self.current_execution.config
                                if self.question.evaluated and self.question.sub_category != 'Fetch':
                                    is_correct = self.question.check_if_correct(self.current_execution, self.sitting.current_execution_req_parameters) 
                                    self.sitting.user_answers[self.sitting.current_question]['evaluated']= True  
                                    self.sitting.user_answers[self.sitting.current_question]['grade'] =  is_correct
                                else:
                                    self.sitting.user_answers[self.sitting.current_question]['evaluated']= False
                                    self.sitting.user_answers[self.sitting.current_question]['grade'] = 0 
                                self.sitting.answered_questions_list.append(True)
                                self.sitting.save()
                        except: 
                            pass
                            a = false
                            if a:
                                guess = None
                                current_experiment_user_answer = {
                                    "answer": self.current_execution.config,
                                    "req_parameters": self.sitting.current_execution_req_parameters,
                                    "evaluationWeight":  self.question.evaluationWeight,
                                    "execution_id": self.current_execution.id
                                }
                                if self.question.evaluated and self.question.sub_category != 'Fetch':
                                    is_correct = self.question.check_if_correct(self.sitting.current_execution, self.sitting.current_execution_req_parameters) 
                                    if is_correct is True:
                                        self.sitting.add_to_score(1, self.question.evaluationWeight)
                                        progress.update_score(self.question, 1, 1)
                                    else:
                                        pass
                                        #self.sitting.add_to_score(0, self.question.evaluationWeight)
                                        #self.sitting.add_incorrect_question(self.question)
                                        #progress.update_score(self.question, 0, 1)
        #                                self.sitting.user_answers.append({'answer': guess, 
        #                                                                'grade': is_correct })
                                    current_experiment_user_answer['evaluated']= True  
                                    current_experiment_user_answer['grade'] =  is_correct

                                else:
                                    current_experiment_user_answer['evaluated']= False
                                    current_experiment_user_answer['grade'] = 0 

                                self.sitting.user_answers.append(current_experiment_user_answer)

                                self.sitting.finished_executions.add(self.current_execution)
                                self.current_execution = None
                                self.sitting.current_execution_req_parameters = None
                                self.sitting.add_user_answer(self.question, guess)
                                self.sitting.answered_questions_list.append(True)
                                #self.sitting.current_question += 1
                                ##self.sitting.remove_first_question()
                    else:
                        pass
                        #creates an new execution
                        """                        current_experiment_info = { }
                        current_apparatus = None
                        protocol = self.quiz.experiments_protocol
                        if self.question.sub_category == 'Fetch':
                            random_exec = self.get_random_execution(protocol)
                            self.current_execution = random_exec
                        else:
                            available_apparatus = True
                            if self.quiz.single_apparatus:
                                # differente apararyus per execution
                                if self.sitting.apparatus == None:
                                    online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
                                    try:
                                        self.sitting.apparatus = random.choice(online_apparatus)
                                        current_apparatus = self.sitting.apparatus
                                    except:
                                        available_apparatus = False

                            else:
                                online_apparatus = [x for x in Apparatus.objects.filter(protocols=self.quiz.experiments_protocol) if x.current_status=='Online']
                                try:
                                    current_apparatus = random.choice(online_apparatus)
                                except:
                                    available_apparatus = False

                            if available_apparatus:
                                required_experiment_parameters = self.question.get_student_experiment_parameters(self.quiz, self.question, self.sitting.user_answers)
                                current_experiment_info["req_parameters"] = required_experiment_parameters
                                #self.sitting.current_execution_req_parameters = student_experiment_parameters
                                config_generator = JSF(protocol.config)
                                config = config_generator.generate()
                                config = self.question.update_experiment_input(config, self.quiz)

                                e = Execution()
                                e.user = self.logged_in_user
                                e.apparatus = current_apparatus
                                e.protocol = protocol
                                e.config = config
                                e.status = 'C'
                                e.save()
                                self.current_execution = e
                                current_experiment_info["execution_id"] = self.current_execution.id
                                try:
                                    self.sitting.user_answers[self.sitting.current_question] = current_experiment_info
                                except:
                                    self.sitting.user_answers.append(current_experiment_info)
                            else:
                                self.current_execution = None
                            self.sitting.save()
                        """               














                        pass
                        #guess = None
                        #is_correct = True
                        #execution_id = self.request.POST.get('execution_id')
                        #self.sitting.add_execution(execution_id)     
            else:
                #user answers a question and presses submit answer
                guess = {}
                for f in form.fields.keys():
                    guess[f] = form.cleaned_data[f]
                #guess = form.cleaned_data['answer']
                if self.request.POST.get('protocol_id') != None:
                    id = self.request.POST.get(protocol_id)
                    random_exec = self.get_random_execution(int(id))
                    random_result = Result.objects.get(execution=random_exec.pk,result_type='f')
                
                    random_exec.pk = None
                    random_exec.user = self.sitting.user
                    random_exec.save()
                    self.sitting.current_execution = random_exec
                    self.sitting.save()

                    random_result.pk = None
                    random_result.execution = random_exec
                    random_result.save()


                if self.question.__class__ is Essay_Question:

                    previous_executions = []
                    for ans in self.sitting.user_answers:
                        if ans['execution_id']:
                            e = Execution.objects.filter(id= ans['execution_id']).first()
                            previous_executions.append(e)

                    try:
                        last_execution = previous_executions[-1]
                    except:
                        last_execution = None

                    is_correct = (
                        #self.sitting.finished_executions.order_by("id")
                        self.question.check_if_correct(guess,self.quiz, last_execution, previous_executions
                                                    ,self.question.multiple_answer_fields))
                else:
                    is_correct = self.question.check_if_correct(guess)

                if is_correct is True:
                    self.sitting.add_to_score(1, self.question.evaluationWeight)
                    progress.update_score(self.question, 1, 1)
                else:
                    self.sitting.add_to_score(0, self.question.evaluationWeight)
                    self.sitting.add_incorrect_question(self.question)
                    progress.update_score(self.question, 0, 1)

                self.sitting.add_user_answer(self.question, guess)
                self.sitting.remove_first_question()
                current_experiment_user_answer = {
                    "answer": guess,
                    "req_parameters": None,
                    "evaluationWeight":  self.question.evaluationWeight,
                    "execution_id": None,
                    'evaluated': self.question.evaluated,
                    'grade': is_correct
                }
                self.sitting.user_answers.append(current_experiment_user_answer)
                self.sitting.answered_questions_list.append(True)
                self.sitting.save()
                #self.sitting.current_question += 1
                #self.sitting.answered_questions_list.append(True)

            #if self.quiz.show_answers_at_end is not True:
            #    self.previous = {'previous_answer': guess,
            #                    'previous_outcome': is_correct,
            #                    'previous_question': self.question,
            #                    'answer': self.question.get_answers(),
            #                    'question_type': {self.question
            #                                    .__class__.__name__: True}}
            #else:
            #    self.previous = {}


    def final_result_user(self, context):
        # calculo da informação a presentar no fim
        
        correct_questions = 0
        total_questions = 0
        correct_score = 0
        max_score = 0
        for ans in self.sitting.user_answers:
            if ans['evaluated']:
                total_questions +=1
                max_score += ans[ 'evaluationWeight']
                if ans['grade']:
                    correct_questions += 1
                    correct_score += ans[ 'evaluationWeight']
        quiz_details =[]
        for i in range(len(self.sitting.user_answers)):
            quiz_details.append({
                'question': self.quiz.orderedQuestions.all()[i], 
                'answer': self.sitting.user_answers[i]
            })
        context['final_result'] = self.sitting.final_result
        context['details'] = quiz_details
        context['quiz']= self.quiz
        context['max_score']= max_score
        context['sitting']= self.sitting
        context['app_name']= __package__.rsplit('.', 1)[-1]
        context['questions']= self.quiz.orderedQuestions.all()
         

        #if self.quiz.exam_paper is False:
        #    self.sitting.delete()

        return context
        return render(self.request, self.result_template_name, context = results)
    

        score_send = self.sitting.get_percent_correct/100
        answer = self.sitting.user_answers
        correct_answers = self.sitting.correct_answers
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
                         'evaluated': q.evaluated,
                         'evaluationWeight': q.evaluationWeight,
                         'correct': q_correct, 
                         'expl': q.explanation}
            details.append(q_details)
        results = {
            'details': details,
            'quiz': self.quiz,
            'correct_answers': correct_answers,
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
            self.question.check_if_correct(guess,self.sitting.current_execution))

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
