from django.contrib import admin
from django.urls import path, re_path
from django.urls import path,re_path
from django.conf.urls import url
from inspection import views

urlpatterns = [
    
    re_path(r'^start_process/$', views.start_process),

    # re_path(r'^check_serial_no/$', views.check_serial_no),
    re_path(r'^check_serial_no/$', views.check_serial_no),

    re_path(r'^get_all_serial_no/$', views.get_all_serial_no),


   
    re_path(r'^server_upload/$', views.server_upload),

]


