try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

# from .views import QuizListView, CategoriesListView, \
#     ViewQuizListByCategory, QuizUserProgressView, QuizMarkingList, \
#     QuizMarkingDetail, QuizDetailView, QuizTake
from .views import *
from django.urls import path

app_name = 'FREE_quizes'
urlpatterns = [

    url(r'^$',
        view=QuizListView.as_view(),
        name='quiz_index'),
    
    url(r'^incomplete/$',
        view=SittingListView.as_view(),
        name='quiz_incomplete'),

#    url(r'^category/$',
#        view=CategoriesListView.as_view(),
#        name='quiz_category_list_all'),

    url(r'^category/(?P<category_name>[\w|\W-]+)/$',
        view=ViewQuizListByCategory.as_view(),
        name='quiz_category_list_matching'),

    url(r'^progress/$',
        view=QuizUserProgressView.as_view(),
        name='quiz_progress'),

    url(r'^progress_list/$',
        view=SittingListView.as_view(),
        name='quiz_progress_list'),

    url(r'^marking/$',
        view=QuizMarkingList.as_view(),
        name='quiz_marking'),

    url(r'^marking/(?P<pk>[\d.]+)/$',
        view=QuizMarkingDetail.as_view(),
        name='quiz_marking_detail'),

    #  passes variable 'quiz_name' to quiz_take view
    url(r'^(?P<slug>[\w-]+)/$',
        view=QuizDetailView.as_view(),
        name='quiz_start_page'),

    url(r'^(?P<quiz_name>[\w-]+)/take/$',
        view=QuizTake.as_view(),
        name='quiz_question'),

    url(r'^(?P<quiz_name>[\w-]+)/submitLTIGrade/$',
        view=QuizLTIPostGrade.as_view(),
        name='quiz_submit_lti'),


        
]
