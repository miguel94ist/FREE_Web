from  free.videoConfig.views import *
from django.urls import re_path, path
urlpatterns = []

urlpatterns += [
    path('videoConfig/', VideoConfigList.as_view(), name='video-config-list'),
    path('videoConfig/<int:id>/', VideoConfig.as_view(), name='video-config'),
    path('videoConfig/<int:id>/error', ErrorVideoConfig.as_view(), name='video-config-error'),
    path('videoConfig/<int:id>/assign/', VideoConfigAssignStream.as_view(), name='video-config-assign'),
    path('videoConfig/<int:id>/remove/', VideoConfigRemoveStream.as_view(), name='video-config-remove'),
]
