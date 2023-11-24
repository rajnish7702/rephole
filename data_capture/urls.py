
from django.urls import path,re_path
from data_capture import views


urlpatterns = [

   
    re_path(r'^save_data/$', views.save_data),
    re_path(r'^get_captured_data/$', views.get_captured_data),

    re_path(r'^delete_captured_image/$', views.delete_captured_image),



   
]







