
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
# Create your views here.




@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def save_data(request):
    # print(request.body)
   
    # data = json.loads(request.body)
    data = request

    response,status_code = save_data_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")





@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_captured_data(request):
    data = json.loads(request.body)
    response, status_code = get_captured_data_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def delete_captured_image(request):
    data = json.loads(request.body)
    response, status_code = delete_captured_image_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")




