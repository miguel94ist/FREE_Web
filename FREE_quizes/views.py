import random
from time import time
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import QuestionForm, EssayForm, Experiment_ExectionForm, Navigate_quizz
from .models import Quiz, Progress, Sitting, Question, Essay_Question
from FREE_quizes.models.questions_models import Experiment_Execution

from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView


from free.models import *
from jsf import JSF

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from lti_provider.mixins import LTIAuthMixin
from pylti.common import LTIPostMessageException, post_message
from django.contrib import auth

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


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'FREE_quizes/view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        return super(ViewQuizListByCategory, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self).get_context_data(**kwargs)

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



class QuizLTIPostGrade(LTIAuthMixin, View):

    def message_identifier(self):
        return '{:.0f}'.format(time.time())

    def post(self, request, *args, **kwargs):
        """
        Post grade to LTI consumer using XML

        :param: score: 0 <= score <= 1. (Score MUST be between 0 and 1)
        :return: True if post successful and score valid
        :exception: LTIPostMessageException if call failed
        """
        # meter o codigo de submissão do resultado
        context={}
        context['lti'] = True
        context['base'] = "free/base_stripped.html"
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        context['quiz'] = self.quiz
        context['lti_submited'] = 'ERROR'

        try:
            self.request.session.get('lti_login')
            self.sitting = Sitting.objects.get_currrent_sitting(request.user,self.quiz)

            context['sitting']= self.sitting

            score = self.sitting.final_result['grade']
            message_identifier = '{:.0f}'.format(time())
            xml = self.lti.generate_request_xml(
                message_identifier, 'replaceResult',
                self.lti.lis_result_sourcedid(self.request), score, None)
            consumers = self.lti.consumers()
            consumer_key = self.lti.oauth_consumer_key(self.request)
            outcome_service_url = self.lti.lis_outcome_service_url(self.request)
            submit_outcome = post_message(consumers, consumer_key, outcome_service_url, xml)
            if submit_outcome:
                self.sitting.archive_quiz()
                context['lti_submited'] = 'OK'
                context['redirect_url'] = self.lti.launch_presentation_return_url(self.request)
                context['final_result'] = self.sitting.final_result
                auth.logout(request) 
            else:
                context['final_result'] = self.sitting.final_result
                pass
        except:
            pass
        return render(request, 'FREE_quizes/result.html', context)



class QuizTake(LoginRequiredMixin, FormView):
    form_class = QuestionForm
    template_name = 'FREE_quizes/question.html'
    result_template_name = 'FREE_quizes/result.html'
    single_complete_template_name = 'FREE_quizes/single_complete.html'
    not_submited_template_name = 'FREE_quizes/send_result.html'

    def dispatch(self, request, *args, **kwargs):
        #code executed when receives a request FREE_quizes/xxx/take (1)
        try:
            if not self.request.user.is_authenticated:
                raise PermissionDenied
        except TypeError:
            raise PermissionDenied
        self.logged_in_user = self.request.user


        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
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

        self.success_url = self.request.path
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        #code executed when filling the page (2)
        
        context = super(QuizTake, self).get_context_data(**kwargs)
        try:
            context['redirect_url'] = self.redirect_url
            context['lti_submited'] = self.lti_submited
        except:
            pass
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
                context['question_result']['grade'] = self.sitting.user_answers[self.sitting.current_question]['grade']

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
                else:
                    pass
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
                        self.question.check_if_correct(guess,self.quiz, last_execution, previous_executions
                                                    ,self.question.multiple_answer_fields))
                else:
                    is_correct = self.question.check_if_correct(guess)
                current_question_user_answer = {
                    "answer": guess,
                    "req_parameters": None,
                    "evaluationWeight":  self.question.evaluationWeight,
                    "execution_id": None,
                    'evaluated': self.question.evaluated,
                    'grade': is_correct
                }
                self.sitting.user_answers.append(current_question_user_answer)
                self.sitting.answered_questions_list.append(True)
                self.sitting.save()


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

        return context

    def get_random_execution(self,appar_id):
        exe_query = Execution.objects.filter(protocol_id=appar_id,status='F')
        pks = list(exe_query.values_list('id',flat=True))
        print("pks:",pks)
        random_pk = random.choice(pks)
        print("rabnd pks:",random_pk)
        return exe_query.get(pk=random_pk)

