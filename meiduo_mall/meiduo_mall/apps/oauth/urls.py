from django.conf.urls import url
from oauth import views

urlpatterns = [
    url(r'qq/authorizations/$', views.QQAuthURLView.as_view()),
    url(r'qq/user/$', views.QQAuthUserView.as_view())
]