# from tkinter import E
# from common.utils import CacheHelper, MongoHelper
# from livis.settings import *
# from bson import ObjectId
# import datetime
# import base64
# import uuid 
# import datetime
# from inspection_mobile_app.virtualbutton import *
# from inspection_mobile_app.plcbutton import *
# # from kafka import KafkaProducer,  KafkaConsumer
# import numpy as np
# import sqlite3

# from tkinter import E
from common.utils import CacheHelper
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
# import datetime
from datetime import  datetime
from dateutil import tz


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class MongoHelper:
    client = None
    def __init__(self):
        if not self.client:
            self.client = MongoClient(host='localhost', port=27017)

        self.db = self.client[settings.MONGO_DB]
        # if settings.DEBUG:
        #     self.db.set_profiling_level(2)
        # placeholder for filter
    """
    def getDatabase(self):
        return self.db
    """

    def getCollection(self, cname, create=False, codec_options=None):
        _DB = "LIVIS_bluedoor"
        DB = self.client[_DB]
        return DB[cname]
    
    def createCollection(self ,cname ):
        self.db.create_collection(str(cname))
        return self.db[str(cname)]

####################################################### mobile app +++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_all_parts_mobile_util(data):
    # print(data)
    project = data.get("project",None)
    parameter_list = []
    if True: #bool(project ):
        project_mp = MongoHelper().getCollection("parts")
        # print(project_mp)
        col = project_mp.find()
        # col = project_mp.find({"part_number":})
        # print(col)
        for i in col:
            # print(i["part_number"])
            try:
                # if cd project in i["part_number"]:
                parameter = i['part_number']
                part_id = str(i["_id"])
                deployed = check_deployment(part_id)
                if deployed:
                    parameter_list.append(parameter)
            except Exception as e:
                print(e)
        return parameter_list ,200
    return parameter_list , 400

def check_deployment(part_id):
    # print("part_id::::",part_id)
    do_inspection = False
    exp_mp = MongoHelper().getCollection("parts")
    id = ObjectId(part_id)
    col = exp_mp.find({"_id":id})
    # print("col:::",col)
    for i in col:
        # print(i)
        # container_deployed = i["deployed"]
        deployed = i["deployed"]
        # print("container_deployed::::",container_deployed)
        # print("deployed:::",deployed)
        if (deployed == True):
            do_inspection = True
            break
    return do_inspection

def get_class_counts(dc_1,label_list): 
    # print("label_list::",label_list)
    # dict ->  list ->dict
    # All im ->ind  -> ind_prediction
    classes = {}
    #iterate through list of dicts
#     for dc_1 in range(len(label_list)):
    for d2 in label_list[dc_1]:
        # print("d2::",d2)
        label = d2#["label"]
        if label in list(classes.keys()):
            classes[label] += 1
        else:
            classes[label] = 1
    return classes

def get_kanban(parameter_id):
    project_mp = MongoHelper().getCollection("parts")
    col = project_mp.find({"_id":ObjectId(parameter_id)})
    for i in col:
        kanban = i["kanban"]
    return kanban

def check_kanban_1(kanban, predicted_frame_dict_list,label_list,part_id): #usingf
    overall_status = None
    defect_list = []#kanban["defect_list"]
    feature_list = []#kanban["feature_list"]
    kanban_details = {}#kanban["kanban_details"]
    try:
        defect_list = kanban["defects"]
        feature_list = kanban["features"]
        kanban_details = kanban["kanban_details"]
    except Exception as e:
        print(e)
        pass
    resp = {}
    status_list = []
    ind_dict_list = []
    #iterate through predictes frames list and label list
    # print("label_list:::",label_list)
    for dict_key , dc_1 in zip(predicted_frame_dict_list,range(len(label_list))):
        defects = []
        missing_features = []
        predicted_frame = predicted_frame_dict_list[dict_key]
        # print(dict_key,dc_1)
        classes = get_class_counts(dc_1,label_list)
        # print("classes:::",classes)
        #defect 
        for label in list(classes.keys()):
            if label in defect_list:
                defects.append(label)

        #missing parameter
        if len(kanban_details)>0:
            # print("list(kanban_details.keys()):::",list(kanban_details.keys()))
            for kd_label in list(kanban_details.keys()):
                if kd_label in list(classes.keys()):
                    if kanban_details[kd_label] != classes[kd_label]:
                        missing_features.append(kd_label)
                else:
                    missing_features.append(kd_label)
        
        for feature in feature_list:
            if feature in list(classes.keys()):
                pass
            else:
                missing_features.append(feature)
                
        if (len(missing_features) == 0) and (len(defects) == 0):
            status = "accepted"   
        else: 
            status = "rejected"  
        status_list.append(status)

        img_path = f'{IMAGE_STORAGE}/{dc_1}.jpg'
        # print("predicted_frame:::",predicted_frame.shape)
        cv2.imwrite(img_path,predicted_frame)
        # missing_features_dict
        missing_features_dict = {}
        if bool(missing_features):
            # print("missing_features::",missing_features)
            missing_features_classes = np.unique(missing_features)
            for missing_class in missing_features_classes:
                if missing_class in list(kanban_details.keys()):
                    try:
                        missing_features_dict[missing_class] = kanban_details[missing_class] - classes[missing_class]#.count(missing_class)
                    except Exception as e:
                        print(e)
                        missing_features_dict[missing_class] = kanban_details[missing_class] 
                else:
                    missing_features_dict[missing_class] = 1

        # ip_address = BASE_URL #"52.66.203.16" #"server_IP address"
        print(missing_features_dict,'missing features dictttttttttttttt')

        url = f"http://{IP_ADDRESS}:8001/{dc_1}.jpg"
        ind_dict_list.append({"image_url":url ,"status":status,"missing_features":missing_features_dict,"defects":defects})
        # print("status_list:::",status_list)
    if bool(len(status_list)) :  
        if "rejected"  in status_list:
            overall_status = "rejected"
        else:
            overall_status = "accepted"
        resp = {"overall_status":overall_status,"ind_dict_list":ind_dict_list}
        print(resp)
        return resp 
    return resp

def check_kanban(kanban, predicted_frame_dict_list,prediction_dict_list,part_id): #usingf
    overall_status = None
    overall_defects = []
    overall_missing_features = []
    overall_status_list = []
    defect_list = []#kanban["defect_list"]
    feature_list = []#kanban["feature_list"]
    kanban_details = {}#kanban["kanban_details"]
    ind_dict_list = []
    
    defect_list = kanban["defects"]
    feature_list = kanban["features"]
    try:
        kanban_details = kanban["kanban_details"]
    except Exception as e:
        print(e)
        pass
    resp = {}
    
    print("defect_list::",defect_list)
    print("feature_list::",feature_list)
    print("kanban_details::",kanban_details)
    #iterate through predictes frames list and label list
    for dict_key , dc_1 in zip(predicted_frame_dict_list,range(len(prediction_dict_list))):
        defects = []
        missing_features = []
        missing_features_dict = {}
        
        predicted_frame = predicted_frame_dict_list[dict_key]
        classes = get_class_counts(dc_1,prediction_dict_list)
        #defect 
        defects.append("features missing")
        for label in list(classes.keys()):
            if label in defect_list:
                defects.append(label)
                
        #missing parameter
        if len(kanban_details)>0:
            print("kanban_details:::",kanban_details)
            print("list(kanban_details.keys()):::",list(kanban_details.keys()))
            for kd_label in list(kanban_details.keys()):
                if kd_label in list(classes.keys()):
                    if kanban_details[kd_label] != classes[kd_label]:
                        missing_features.append(kd_label)
                        missing_features_dict[kd_label] = kanban_details[kd_label] - classes[kd_label]
                else:
                    missing_features.append(kd_label)
                    missing_features_dict[kd_label] = kanban_details[kd_label] 
        else:
            for feature in feature_list:
                if feature in list(classes.keys()):
                    pass
                else:
                    missing_features.append(feature)
                    missing_features_dict[feature] = 1

        if (len(missing_features) == 0) and (len(defects) == 0):
            status = "accepted"   
        else: 
            status = "rejected"  
        print("defects:::",defects)
        print("missing_features_dict::::",missing_features_dict)
        print("status::::",status)
        overall_status_list.append(status)
        overall_defects.extend(defects)
        overall_missing_features.extend(missing_features)
        img_path = f'{IMAGE_STORAGE}/{dc_1}.jpg'
        cv2.imwrite(img_path,predicted_frame)
        url = f"http://{IP_ADDRESS}:8001/{dc_1}.jpg"
        missing_features_dict = list(missing_features_dict.keys())
        ind_dict_list.append({"image_url":url ,"status":status,"missing_features":missing_features_dict,"defects":defects})
    #Overall status
    if bool(len(overall_status_list)) :  
        if "rejected"  in overall_status_list:
            overall_status = "rejected"
        else:
            overall_status = "accepted"
        resp = {"overall_status":overall_status,"ind_dict_list":ind_dict_list}
        print(resp)
        return resp 
    return resp

def get_inference_mobile_util(data):
#     aircraft_number = data.data.get("aircraft_number",None)
    t0 = datetime.now()
    rch = CacheHelper()
    parameter = data.data.get("parameter",None)
    mobile_id = data.data.get("mobile_id",None)
    operator_name = data.data.get("operator_name",None)
    parameter_id = ""
    # print("parameter:::",parameter)
    if bool(parameter):
        #get part id
        project_mp = MongoHelper().getCollection("parts")
        a = project_mp.find({"part_number":parameter})
        for i in a :
            parameter_id = i["_id"]
        # form = NameForm(data.POST)

        #check whether the model in deplyed or not
        deployed_do_inspection = check_deployment(part_id =parameter_id )
        if deployed_do_inspection:
            # print("mobile_id",mobile_id)
            zone_data = {
                        "parameter":parameter_id,
                        "operator_name":operator_name}
            try:
                files = data.FILES.getlist('myfiles')
            except:
                    message = "No file provided"
                    status_code = 400
                    return message, status_code
            if not files:
                return "Empty file", 200
            i = 0
            input_image_array = [] 
            for file in files:
                img_str = b''
                for chunk in file.chunks():
                    img_str += chunk
                nparr = np.fromstring(img_str, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                w,h,c = img_np.shape
                img_np = cv2.resize(img_np,(w//2,h//2))#cv2.resize(predicted_frame,(w//2,h//2))
                input_image_array.append(img_np)
                i = i +1
                print(img_np.shape)
            rch.set_json({f"{mobile_id}_input_frame_list":input_image_array})
            rch.set_json({f"{mobile_id}_parameter":parameter})
            rch.set_json({f"{mobile_id}_mobile_trigger":True})
            
            # rch.set_json({f"{mobile_id}_zone_data":zone_data})

            while True:
                inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
                mobile_trigger = rch.get_json(f"{mobile_id}_mobile_trigger")
                if mobile_trigger == False:
                    if inspection_completed == True:
                        predicted_frame_dict_list = rch.get_json(f"{mobile_id}_output_frame_list")
                        prediction_dict_list =  rch.get_json(f"{mobile_id}_prediction_dict_list")
                        #label_list.append({"label":names[c], "confidence_score" : conf,"coords":[p1,p2],"img_size":imgsz })
                        # classes_count = get_class_counts(label_list)
                        kanban = get_kanban(parameter_id)
                        resp = check_kanban(kanban, predicted_frame_dict_list,prediction_dict_list,part_id = parameter_id)
                        rch.set_json({f"{mobile_id}_inspection_completed":False})
                        # print("kanban::",kanban)
                        # print("resp:::",resp)
        #                 status , missing_features,defects = check_kanban(kanban, classes_count)
                        t1 = datetime.now()
                        print(f'Time taken for one complete cycle >>>image transfer and inference GPU:::  {(t1-t0).total_seconds()} sec')
                        return resp ,200
        else:
            return "Not Deployed",200
    else:
        return "parameter missing!!!",401  

def get_reference_image_util(data):
    # print(data)
    if bool(data):
        parameter = data.get("parameter",None)
        image_url_path = f"http://{IP_ADDRESS}:8001/bluedoor_weights/{parameter}/reference_image.jpg"
        # image_url_path = f"http://{IP_ADDRESS}:8001/gorad/lincode/schneider/Blue_door/standalone/ai_controller/bluedoor_weights/bluedoor/reference.jpg"
        return image_url_path,200
    else:
        return "None",401