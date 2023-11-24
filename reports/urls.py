from django.urls import path,re_path
from reports import views

urlpatterns = [
    re_path(r'^getMegaReport/$', views.get_mega_report),
    re_path(r'^exportCSV/$', views.export_report),

  
    re_path(r'^get_daywise_report/$', views.get_daywise_report),
    re_path(r'^get_dash_board_reports/$', views.get_dash_board_reports),
    re_path(r'^get_overall_report/$', views.get_overall_report),
    re_path(r'^export/$', views.export),

]


