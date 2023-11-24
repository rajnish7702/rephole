from json import encoder
import json
from django.http import HttpResponse, response
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from common.utils import Encoder
from .utils import *
from rest_framework.permissions import AllowAny
from accounts.views import check_permission
from django.http import HttpResponse, StreamingHttpResponse



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
# @permission_classes((AllowAny,))
def start_process(request):
    ''''''
    # check_permission(request,"can_start_process")
    data = json.loads(request.body)
    response,status_code = start_process_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type = "application/json")



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
# @permission_classes((AllowAny,))
def check_serial_no(request):
    ''''''
    # check_permission(request,"can_start_process")
    data = json.loads(request.body)
    response,status_code = check_serial_no_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type = "application/json")




@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
# @permission_classes((AllowAny,))
def get_all_serial_no(request):
    ''''''
    # check_permission(request,"can_start_process")
    response,status_code = get_all_serial_no_util()
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type = "application/json")



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
# @permission_classes((AllowAny,))
def server_upload(request):
    check_permission(request,"can_upload_images")
    data = json.loads(request.body)

    from inspection.utils import server_upload_util
    response,status_code = server_upload_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type = "application/json")


