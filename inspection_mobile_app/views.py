
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

###################################mobile app####################################
@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_all_parts_mobile(request):
    # print("Inside?>>>>>>>>>>>>>>>>>>>>>>>>>>get_all_parts_mobile>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # print("request:::",request)
    # print("request.body::::",request.body)
    # check_permission(request,"can_upload_images")
    # token_user_id = request.user.user_id
    # operation_type = "inspection"
    # notes = "start inspection"
    
    # add_logs_util(token_user_id,operation_type,notes)
    
    
    data = json.loads(request.body)
    # print(data,'qwwqdqwdwq')
    
    
    response,status_code = get_all_parts_mobile_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")


@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_reference_image(request):
    # check_permission(request,"can_upload_images")
    # token_user_id = request.user.user_id
    # operation_type = "inspection"
    # notes = "start inspection"
    
    # add_logs_util(token_user_id,operation_type,notes)
    
    
    data = json.loads(request.body)
    # print("request:::",request)
    
    response,status_code = get_reference_image_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")



# @api_view(['POST'])
# @renderer_classes((TemplateHTMLRenderer,JSONRenderer))
# @csrf_exempt
# @permission_classes((AllowAny,))
# def get_reference_image(request):
#       if bool(data):
#         parameter = data.get("parameter",None)
#         # image_url_path = f"http://localhost:8001/F:/tata_raphole/BE_RAP_HOLE/label_inspction/datadrive/Reference_images/{parameter}/reference_image.jpg"
#         image_url_path = f"http://localhost:8001/F:/tata_raphole/BE_RAP_HOLE/label_inspction/datadrive/Reference_images/Front_Acqustic_Panel/image0000002.jpg"

#         # image_url_path = f"http://{IP_ADDRESS}:8001/gorad/lincode/schneider/Blue_door/standalone/ai_controller/bluedoor_weights/bluedoor/reference.jpg"
#         return image_url_path,200
#       else:
#         return "None",401

@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_inference_mobile(request):
    # check_permission(request,"can_upload_images")
    # token_user_id = request.user.user_id
    operation_type = "inspection"
    notes = "start inspection"
    
    # add_logs_util(token_user_id,operation_type,notes)
    
    
    # data = json.loads(request.data)
    
    
    response,status_code = get_inference_mobile_util(request)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_inferences(request):
    # check_permission(request,"can_upload_images")
    # token_user_id = request.user.user_id
    operation_type = "inspection"
    notes = "start inspection"
    
    # add_logs_util(token_user_id,operation_type,notes)
    
    
    # data = json.loads(request.data)
    
    
    response,status_code = get_inference_utils(request)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")


@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_inference(request):
    
    response,status_code = get_inference_util(request)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")


@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_inference_model(request):
    
    response,status_code = get_inference_model_util(request)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")

@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def get_all_regions_view(request):
   
    response,status_code = get_all_regions_util()
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")



@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def check_barcode_number(request):
    data = request.data
    response,status_code = check_barcode_number_util(data)
    print(response,'ressssssssssssss')
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")




@api_view(['POST'])
@renderer_classes((TemplateHTMLRenderer,JSONRenderer))
@csrf_exempt
@permission_classes((AllowAny,))
def check_model_number(request):
    data = request.data
    response,status_code = check_model_number_util(data)
    if status_code != 200:
        return HttpResponse( {response}, status=status_code)
    else:
        return HttpResponse(json.dumps(response, cls=Encoder), content_type="application/json")

