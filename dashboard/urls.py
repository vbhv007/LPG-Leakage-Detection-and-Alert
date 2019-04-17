from . import views
from django.urls import re_path, include

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'index', views.index, name='index'),
    re_path(r'history', views.history, name='history'),
    re_path(r'helpline', views.helpline, name='helpline'),
]
