from django.conf.urls import url
from oauth import views

urlspattern = [
    url(r'qq/authorizations/$', views.QQAuthURLView.as_view()),
]