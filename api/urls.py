from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'webhook_bookie$', views.bookie_hook, name='base_url_check')
]
