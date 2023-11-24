from django.urls import path,re_path
from inspection_mobile_app import views


urlpatterns = [

    #mobile app ups
    re_path(r'^get_all_parts_mobile/$', views.get_all_parts_mobile),
    re_path(r'^get_reference_image/$', views.get_reference_image),
    re_path(r'^get_inference_mobile/$', views.get_inference_mobile),
    re_path(r'^get_inference/$', views.get_inferences),

    
    re_path(r'^get_all_regions/$', views.get_all_regions_view),

    ## Label inspection - v1
    re_path(r'^check_barcode_number/$', views.check_barcode_number),
    re_path(r'^get_inference/$', views.get_inference),

    ## Label inspection - v2
    re_path(r'^check_model_number/$', views.check_model_number),
    re_path(r'^get_inference_model/$', views.get_inference_model),







]

