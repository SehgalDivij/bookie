from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.base_url, name='base_url_check')
]
