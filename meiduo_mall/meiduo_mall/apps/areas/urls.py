from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

urlpatterns = [
    # url(r'^/areas/$', views.AreasView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$', views.SubAreasView.as_view()),
]

# 视图集的路由注册就可以使用Router来实现
router = DefaultRouter()
router.register('areas',views.AreaViewSet, base_name='areas')
urlpatterns += router.urls