from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserVIew.as_view()),
    # Django REST framework JWT提供了登录签发JWT的视图，可以直接使用
    url(r'^authorizations/$', obtain_jwt_token),  # obtain_jwt_token = ObtainJSONWebToken.as_view()
    url(r'^user/$', views.UserDetailView.as_view())
]