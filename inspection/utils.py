from common.utils import CacheHelper,MongoHelper
from django.http import response
import numpy as np
import cv2 
from numpy import array
import json
import base64
import multiprocessing
import sys
from pymongo import MongoClient
from bson import ObjectId
from livis import settings as settings
from livis.settings import BASE_URL
from livis.settings import *
import os
import time
import datetime
from dateutil import tz




def create_process_collection(c_name):
    pc = MongoHelper().createCollection(c_name)
    print("Process collection >>>>>>",pc)
    return pc

# #API to save inspection from all cameras.
# def save_inspection_ocr(data):
#     print(">>>>>>>>>>>>>>>>>>>inside save OCR")
#     current_inspection_id = data.get('inspection_id',None)
#     quick_report = {}
#     raw_data = {}
#     ocr_status = ""
#     mp = MongoHelper().getCollection('inspection')
#     doc = mp.find_one({'_id' : ObjectId(current_inspection_id)})

#     part_name = doc["part_name"]
#     ocr_status = CacheHelper().get_json("OCR_status")
#     quick_report["overall_status"] = ""
#     # OCR results match the PLC part
#     if ocr_status == "Rejected":
#         coll = MongoHelper().getCollection(str(current_inspection_id))
#         # print("-----------------Save inspection ID--------------------------",str(inspection_id))
#         quick_report['time_stamp'] = str(datetime.datetime.now().replace(microsecond=0))
#         #save images
#         # quick_report["inspection_id"] = inspection_id
#         quick_report['inference_ocr_images_list'] = []
#         quick_report["inference_ocr_status_list"] = []
#         quick_report["ocr_status"] = ocr_status
#         ###  get predicted frames from front end
#         predicted_frames_dict = CacheHelper().get_json("ocr_frame")
#         #print("predicted_frames_dict",predicted_frames_dict)
#         img = CacheHelper().get_json("ocr_frame")
#         path = "/"
#         fname = "temp"+str(img)+".jpg"
#         #print("Writing image ,",fname, cv2.imwrite(path+fname, img))
#         quick_report['inference_ocr_images_list'].append("http://127.0.0.1:8000/livis/data/" + fname+'.jpg')
#         quick_report['inference_ocr_status_list'].append(ocr_status)
#         quick_report['burr_status'] = "Rejected"
#         quick_report['overall_status'] = "Rejected"

#         id_ = coll.insert_one(quick_report)
#         #print(id_, quick_report)
#         quick_report['_id'] = str(quick_report['_id'])
#         quick_report['part_name'] = part_name
#     elif ocr_status == "Accepted":
#         coll = MongoHelper().getCollection(str(current_inspection_id))
#         # print("-----------------Save inspection ID--------------------------",str(inspection_id))
#         quick_report['time_stamp'] = str(datetime.datetime.now().replace(microsecond=0))
#         #save images
#         # quick_report["inspection_id"] = inspection_id
#         quick_report['inference_ocr_images_list'] = []
#         quick_report["inference_ocr_status_list"] = []
#         quick_report["ocr_status"] = ocr_status
#         ###  get predicted frames from front end
#         predicted_frames_dict = CacheHelper().get_json("ocr_frame")
#         #print("predicted_frames_dict",predicted_frames_dict)
#         img = CacheHelper().get_json("ocr_frame")
#         path = "/"
#         fname = "temp"+str(img)+".jpg"
#         #print("Writing image ,",fname, cv2.imwrite(path+fname, img))
#         quick_report['inference_ocr_images_list'].append("http://127.0.0.1:8000/livis/data/" + fname+'.jpg')
#         quick_report['inference_ocr_status_list'].append(ocr_status)
#         quick_report['overall_status'] = ""

#         id_ = coll.insert_one(quick_report)
#         #print(id_, quick_report)
#         quick_report['_id'] = str(quick_report['_id'])
#         quick_report['part_name'] = part_name

#     return quick_report

# #API to save inspection from all cameras.
# def save_inspection_burr(data):
    
#     current_inspection_id = data.get('inspection_id',None)
#     print(">>>>>>>>>>>Inspection ID"+str(current_inspection_id))
#     quick_report = {}
#     raw_data = {}
#     status = ""
#     burr_status = ""

#     mp = MongoHelper().getCollection('inspection')
#     doc = mp.find_one({'_id' : ObjectId(current_inspection_id)})
#     part_name = doc["part_name"]
#     #ocr_status = "Accepted"
#     mp = MongoHelper().getCollection(str(current_inspection_id))
#     log_coll = [i for i in mp.find()]
#     doc = log_coll[::-1]
#     print(type(doc))
#     print(doc[0])
#     doc = doc[0]
#     if doc["ocr_status"] == "Accepted" and doc["overall_status"] == "":
#         # print("-----------------Save inspection ID--------------------------",str(inspection_id))
#         doc['time_stamp'] = str(datetime.datetime.now().replace(microsecond=0))
#         #save images
#         # quick_report["inspection_id"] = inspection_id
#         doc['inference_burr_images_list'] = []
#         doc["inference_burr_status_list"] = []
#         ###  get predicted frames from front end
#         doc["burr_status"] = CacheHelper().get_json("burr_status")
#         if doc["burr_status"] == "Accepted":
#             doc["overall_status"] = "Accepted"
#         else:
#             doc["overall_status"] = "Rejected"


#         predicted_frames_dict = CacheHelper().get_json("predicted_frames")
#         for key in predicted_frames_dict:
#             img = predicted_frames_dict[key]["predicted_frame"]
#             #print("****Image is"+str(img))
#             path = "/"
#             fname = "temp"+str(key)+".jpg"
#             #print("Writing imgae ,",fname, cv2.imwrite(path+fname, img))
#             doc['inference_burr_images_list'].append("http://127.0.0.1:8000/livis/data/" + fname+'.jpg')
#             doc['inference_burr_status_list'].append(predicted_frames_dict[key]["is_accepted"])

#         mp.update({"_id":doc["_id"]}, {"$set":doc})
    
#     doc['_id'] = str(doc['_id'])
#     doc['part_name'] = part_name
#     return doc


# def create_urls_from_camera(camera_id, BASE_URL):
#     fmt_url = BASE_URL + '/livis/v1/inspection/get_output_stream/{}/' 
#     return fmt_url.format(camera_id)


# def get_running_process_utils():
#     mp = MongoHelper().getCollection('inspection')
#     insp_coll = [i for i in mp.find({"status":"started"})]
#     inspection_id = ""
#     response = {}
#     if len(insp_coll) > 0:
#         res = insp_coll[-1]
#         response["inspection_id"] = str(res['_id'])
#         response["part_name"] = res["part_name"]
#         # print("*****************Running process inspection_id*********************",inspection_id)
#     return response,200

def check_serial_no_util(data):
    serial_no = data.get('serial_no')
    mp = MongoHelper().getCollection('inspections_log')
    mp_data_sn = mp.find_one({'serial_no':serial_no})
    if bool(mp_data_sn):
        mp.delete_one(mp_data_sn)
        return {"message":"Serial Number exists","id":mp_data_sn.get('_id')}, 200
    return mp_data_sn, 200



def get_all_serial_no_util():
    mp = MongoHelper().getCollection('inspections_log')
    mp_data_sn = mp.find()
    serial_nos = []
    for i in mp_data_sn:
        print(i,'iiiiiiiiiiiiiiiiiii')
        serial_no = i.get('serial_no')
        if not serial_no is None:
            serial_nos.append({'serial_no':serial_no})
    print(serial_nos)
    return serial_nos, 200

    

def start_process_util(data):
    operator_name = data.get('operator_name',None)
    family_name = data.get('family_name',None)

    if operator_name is None:
        return "operator name not present", 400
 
    if family_name is None:
        return "Model Number is not present", 400


    mp = MongoHelper().getCollection('inspections_log')
    
   

    mp = MongoHelper().getCollection('inspection')
    current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    createdAt = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    coll = {
    "family_name":family_name,
    "start_time":createdAt,
    "end_time":createdAt,
    "operator_name":operator_name,
    "produced_on":current_date,
    'created_date':datetime.datetime.now().strftime("%d"),
    "status":"started",
    }

    curr_insp_id = mp.insert_one(coll)
    bb = MongoHelper().getCollection('current_inspection')
    ps = bb.find_one()

    mp1 = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')
    mp1.insert(coll)
    if ps is None:
        bb.insert_one({'current_inspection_id' : str(curr_insp_id.inserted_id)})       
    else:
        ps['current_inspection_id'] = str(curr_insp_id.inserted_id)
        bb.update({"_id" : ps['_id']}, {"$set" : ps})
    response = {"current_inspection_id":str(curr_insp_id.inserted_id)}
    return  response,200


# def end_process_util(data):
#     inspection_id  = data.get('inspection_id', None)
#     if inspection_id is None:
#         return "Failed", 200
#     mp = MongoHelper().getCollection('inspection')
#     ps = mp.find_one({'_id' : ObjectId(inspection_id)})
#     current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
#     ending = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

#     ps["end_time"] = ending
#     ps["status"] = "completed"

#     mp.update({'_id' : ps['_id']}, {"$set" : ps})

#     bb = MongoHelper().getCollection('current_inspection')
#     ps = bb.find_one()
#     if ps is None:
#         bb.insert_one({'current_inspection_id' : None})
#     else:
#         ps['current_inspection_id'] = None
#         bb.update({"_id" : ps['_id']}, {"$set" : ps})
#     return "Success" ,200


# def get_defect_list(inspectionid):
#     print(inspectionid)
#     inspectionid_collection = MongoHelper().getCollection(str(inspectionid))
#     objs = [i for i in inspectionid_collection.find()]
#     total = 0
#     total_accepted = 0
#     total_rejected = 0
#     response = {}
#     for ins in objs:
#             if ins["overall_status"] == "Accepted":
#                 total_accepted += 1
#                 total += 1
#             elif ins["overall_status"] == "Rejected":
#                 total_rejected += 1
#                 total += 1


#     mp = MongoHelper().getCollection(str(inspectionid))
#     list_ = [i for i in mp.find()]
#     doc = {}
#     ocr_defect_list = []
#     burr_defect_list = []
#     if list_:
#         #print(list_)
#         doc = list_[::-1][0]
#         #print(doc)
#         ocr_defects = doc.get("inference_ocr_status_list")
#         if ocr_defects:
#             for key in range(0,len(ocr_defects)):
#                 if ocr_defects[key] == "Rejected":
#                     ocr_defect_list.append(key)
#         burr_defects = doc.get("inference_burr_status_list")
#         if burr_defects:
#             #burr_defect_dict = dict(burr_defect_dict)
#             #print(burr_defect_dict)
#             for key in range(0, len(burr_defects)):
                
#                 if burr_defects[key] == "Rejected":
#                     burr_defect_list.append(key)

#     response = {"ocr_status":doc.get("ocr_status"),"burr_status":doc.get("burr_status"), 
#             "overall_status": doc.get("overall_status"), "total_count":total, "total_accepted":total_accepted, 
#             "total_rejected":total_rejected, "defect_list":{"ocr":ocr_defect_list,"burr":burr_defect_list}}
#     print(response)
#     return response, 200



# def get_inference_feed(cam_id):
#     if cam_id == "ocr_frame":  ## OCR frame
#         key = "ocr_frame"
#         cam_id = "0"
#         while True:
    
#             v = CacheHelper().get_json(key)
#             im_b64_str = v
#             ret, jpeg = cv2.imencode('.jpg', im_b64_str)
#             frame = jpeg.tobytes()
        
#             yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
#     else:
#         key = "predicted_frames"
        

#     while True:
    
#         v = CacheHelper().get_json(key)
#         im_b64_str = v[int(cam_id)]["predicted_frame"]
#         ret, jpeg = cv2.imencode('.jpg', im_b64_str)
#         frame = jpeg.tobytes()
        
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    


#####################################################TBAL>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
rch = CacheHelper()

def get_configuration_collection(configuration_number):
    """This function returns the collections wrt the given configuration number"""
    resp = []
    mp = MongoHelper().getCollection(configuration_number)
    cc = mp.find()
    for c in cc :
        resp.append(c)
        # print(c)
    return resp








def get_aircraft(aircraft_number):
    mp = MongoHelper().getCollection(AIRCRAFT_INSPECTION_SUMMARY)
    ac_num_list = []
    cc = mp.find({"status":"inprogress"})#inprogress,completed
    for c in cc :
    #     print(c)
        acn = c["aircraft_number"]
        ac_num_list.append(acn)
    return ac_num_list 





def get_camera_feed_urls_util(mobile_id,image_count):
    feed_urls = []
    # workstation_info = RedisKeyBuilderServer(workstation_id).workstation_info
    # camera_info = get_camera_details()
    mobile_id = "0"
    for c in range(image_count):
        url = "http://localhost:8000/livis/v1/tbal/stream/{}/".format(mobile_id+"_"+str(c)+"_predicted_frame")
        feed_urls.append(url)
    return feed_urls

def redis_ui_data_util(key):
    # key = data.get("key")
    rch = CacheHelper()
    while True:
        frame1 = rch.get_json(key)
        # print("KEY :      : :: :  : : : : :" , key )
        # print(frame1.shape)
        ret, jpeg = cv2.imencode('.jpg', frame1)
        frame =  jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



def redis_predicted_frames(key):
    rch = CacheHelper()
    while True:
        frame1 = rch.get_json(key)
        # print("KEY :      : :: :  : : : : :" , key )
        # print(frame1.shape)
        ret, jpeg = cv2.imencode('.jpg', frame1)
        frame =  jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# def get_camera_feed_urls_util():
#     feed_urls = []
#     # workstation_info = RedisKeyBuilderServer(workstation_id).workstation_info
#     # camera_info = get_camera_details()
#     for camera in camera_info:
#         url = "http://localhost:8000/livis/v1/indo/stream/{}/".format("WS_01"+"_"+str(camera['camera_id'])+"_predicted_frame")
#         feed_urls.append(url)
#     return feed_urls

def edit_path(image_path):
    if "tbal" in image_path:
        img_path = image_path.split("tbal")[1]
    elif "goku" in image_path:
        img_path = image_path.split("goku")[1]
    return img_path

def get_aircraft_zone_levels_util(data):
    aircraft_number = data.get("aircraft_number")
    ai_mp = MongoHelper().getCollection(AIRCRAFT_INSPECTIONS_COLLECTION)
    aircraft_collection = ai_mp.find({"aircraft_number":aircraft_number})
    col = {}
    for entries in aircraft_collection:
        col = entries
    return col ,200



# from django import forms

# class NameForm(forms.Form):
#     your_name = forms.CharField(label='username', max_length=100)
def resize_frame(frame):
    w,h,_ = frame.shape
    if w > 10000 or h > 10000 :
        frame = cv2.resize(frame,(w//10,h//10))
    elif w > 5000 or h > 5000 :
        frame = cv2.resize(frame,(w//5,h//5))
    elif w > 2500 or h > 2500 :
        frame = cv2.resize(frame,(w//2,h//2))
    print("frame.shape:::",frame.shape)
    return frame





def server_upload_util(data):
    mobile_id = data.get("mobile_id",None)
    rch = CacheHelper()
    # while True:
    time.sleep(1)
    inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
    print(inspection_completed)
    if inspection_completed:
        predicted_response = rch.get_json(f"{mobile_id}_predicted_response")
        rch.set_json({f"{mobile_id}_inspection_completed" : False})
        inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
        print(inspection_completed)
        print("predicted_response",predicted_response)
        print("Inside server upload>>>>>>>>completed!!!!!!!!!")
        return  predicted_response ,200
    print("inside server upload >>>> inprogress!!!")
    return "inprogress",200

