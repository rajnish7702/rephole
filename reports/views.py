from django.shortcuts import render
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from django.http import HttpResponse
import json
from common.utils import *
from drf_yasg import openapi
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_ARRAY
from drf_yasg.utils import swagger_auto_schema
from accounts.views import check_permission



# @api_view(['POST'])
# @renderer_classes((TemplateHTMLRenderer,JSONRenderer))
# @csrf_exempt
# def edit_remark(request):
#     #check_permission(request,"can_edit_remark")
#     from reports.utils import edit_remark_util
#     data = json.loads(request.body)
#     response = edit_remark_util(data)
#     return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")

# @api_view(['POST'])
# @renderer_classes((TemplateHTMLRenderer,JSONRenderer))
# @csrf_exempt
# def set_flag(request):
#     #check_permission(request,"can_set_flag")
#     from reports.utils import set_flag_util
#     data = json.loads(request.body)
#     response = set_flag_util(data)
#     return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")


@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
def get_mega_report(request):
    print('get megareport views...')
    #check_permission(request,"can_get_mega_report")
    from reports.utils import get_megareport_util
    data = json.loads(request.body)
    response = get_megareport_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")
    
##################TBAL>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..

@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
def get_daywise_report(request):
    # check_permission(request,"can_daywise_report")
    from reports.utils import get_daywise_report_util
    data = json.loads(request.body)
    response,status = get_daywise_report_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")
    

@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
def get_dash_board_reports(request):
    # check_permission(request,"can_zone_wise_report")
    from reports.utils import get_dash_board_reports_util
    data = json.loads(request.body)
    print(data, 'data from utils...')

    response,status = get_dash_board_reports_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")
    

@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
def get_overall_report(request):
    check_permission(request,"can_zone_wise_report")
    from reports.utils import get_overall_report_util
    print(request)
    data = json.loads(request.body)
    print(data)
    response,status = get_overall_report_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")

@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
def export(request):
    check_permission(request,"can_zone_wise_report")
    from reports.utils import export_util
    data = json.loads(request.body)
    response,status = export_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")
    


@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
# @permission_classes((AllowAny,))
def export_report(request):
    # check_permission(request,"can_get_mega_report")
    from reports.utils import export_csv_util
    data = json.loads(request.body)
    response = export_csv_util(data)
    return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")


