from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'webhook_bookie$', views.bookie_hook, name='base_url_check'),
    url(r'table_add$', views.add_table, name='add table'),
    url(r'check_table', views.check_table_avaialbility, name='Check availability'),
    url(r'add_dummy', views.add_dummy_reservation, name='Add Dummy Reservation')
]
