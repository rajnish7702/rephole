import os
from kafka import KafkaProducer,  KafkaConsumer
import json
import cv2
import numpy as np
import base64
import time
import sys
import logging
import pandas as pd
from pymongo import MongoClient
from common.utils import MongoHelper
from django.utils import timezone
from bson import ObjectId
import multiprocessing
from .consumer import *
from livis.settings import *
import uuid 


consumer_mount_path = TRAIN_DATA_STATIC


def get_inference_feed_url_util(wsid , partid, camera_name):

    try:
        mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    except:
        message = "Cannot connect to db"
        status_code = 500
        return message,status_code

    workstation_id = wsid

    feed_urls = []
    dummmy_dct = {}
    
    
    workstation_id = ObjectId(wsid)
    mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    ws_row = mp.find_one({'_id': workstation_id})
    ws_camera_dict = ws_row.get('cameras')
    #print(ws_camera_dict)
    
    for i in ws_camera_dict:
        if i['camera_name'] == camera_name:
            ## check camera in preprocess table for the part
            #url = "http://127.0.0.1:8000/livis/v1/capture/inference_camera_preview/{}/{}/{}/".format(workstation_id,i['camera_name'], partid)
            url = "http://"+BASE_URL+":8000/livis/v1/capture/inference_camera_preview/{}/{}/{}/".format(workstation_id,i['camera_name'], partid)
            dummmy_dct = {"camera_name":i['camera_name'] , "camera_url":url,"workstation_id":str(workstation_id),"camera_id":str(i['camera_id'])}
            feed_urls.append(dummmy_dct)
    return feed_urls


def get_camera_feed_urls():

    try:
        mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    except:
        message = "Cannot connect to db"
        status_code = 500
        return message,status_code


    p = [p for p in mp.find()]

    feed_urls = []
    for coll in p:
    
        workstation_id = coll['_id']

        
        dummmy_dct = {}
    
    
        workstation_id = ObjectId(workstation_id)
        mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
        ws_row = mp.find_one({'_id': workstation_id})
        ws_camera_dict = ws_row.get('cameras')

    
        for i in ws_camera_dict:
            url = "http://"+BASE_URL+":8000/livis/v1/capture/consumer_camera_preview/{}/{}/".format(workstation_id,i['camera_name'])
            dummmy_dct = {"camera_name":i['camera_name'], "camera_url":url,"workstation_id":str(workstation_id),
                          "camera_id":str(i['camera_id']),"workstation_name": str(ws_row.get('workstation_name'))}
            feed_urls.append(dummmy_dct)
    if feed_urls:
        return feed_urls
    else:
        return {}


def apply_crops(img, x,y,w,h):
    height,width,channels = img.shape
    x0 = x * width
    y0 = y * height
    x1 = ((x + w) * width)
    y1 = ((y + h) * height)
    img = img[y0:y1,x0:x1]
    return img
    
    
def capture_image_util(data):
    #print("in capture@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    try:
        part_id = data['part_id']
    except:
        message = "part id not provided"
        status_code = 400
        return message, status_code

    try:
        workstation_id = data['workstation_id']
    except:
        message = "workstation id not provided"
        status_code = 400
        return message, status_code
        
    try:
        camera_id = data['camera_id']
    except:
        message = "camera_id not provided"
        status_code = 400
        return message, status_code   
    #print("in capture abc   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # access the workstation table
    workstation_id = ObjectId(workstation_id)
    mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    ws_row = mp.find_one({'_id': workstation_id})
    ws_camera_dict = ws_row.get('cameras')

    #for i in ws_camera_dict:
    #    camera_id = i['camera_id']
    #    camera_name1 = i['camera_name']
    #    if camera_name1 == camera_name:
    #        break

    topic = str(workstation_id) + "_" + str(camera_id) + "_i"
    topic = topic.replace(":","")
    topic = topic.replace(".","")

    consumer = KafkaConsumer(topic, bootstrap_servers=KAFKA_BROKER_URL, auto_offset_reset='latest', fetch_max_bytes=41943040)
    #print("Consumer initialized")
    for message in consumer:
        #print("checking for msg")
        a = message.value.decode('utf-8')
        b = json.loads(a)
        im_b64_str = b["frame"]
        im_b64 = bytes(im_b64_str[2:], 'utf-8')
        im_binary = base64.b64decode(im_b64)

        im_arr = np.frombuffer(im_binary, dtype=np.uint8)
        frame = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        height, width, _ = frame.shape

        #print(frame.shape)
        preprocessing_list = MongoHelper().getCollection(str(part_id) + "_preprocessingpolicy")
        p = [p for p in preprocessing_list.find()]
        #print("p is")
        #print(p)
        if len(p) == 0 or p[0]['policy']['crop'] == "":
            #print("i am here ... ")
            # no preprocessing policy set - use image as is

            uuid_str = str(uuid.uuid4()) 
            img_name = consumer_mount_path+"/"+str(uuid_str)+".png"
            #print(img_name)
            cv2.imwrite(img_name,frame)
            
            #http_name = "http://0.0.0.0:3306/" +str(uuid_str)+".png"
            http_name = "http://"+BASE_URL+":3306/"+str(uuid_str)+".png"

            capture_doc = {
                "file_path": img_name,
                "file_url": http_name,
                "state": "untagged",
                "annotation_detection": [],
                "annotation_detection_history": [],
                "annotation_classification": "",
                "annotation_classification_history": [],
                "annotator": "",
                "date_added":timezone.now()}
                
            mp = MongoHelper().getCollection(part_id + "_dataset")
            mp.insert(capture_doc)
            
        else:
            #print("in else blok")
            #preprocessing exists
            #check if regions exists 
            p = p[0]
            regions = None
        
            try:
                regions = p['policy']['crop']
            except:
                pass
                

            policy_crop = []
            for j in regions:

                x = j["x"]
                y = j["y"]
                w = j["w"]
                h = j["h"]

                x0 = x * width
                y0 = y * height
                x1 = ((x+w) * width)
                y1 = ((y+h) * height)

                #label = j["cls"]
                cords = [x0,y0,x1,y1]

                policy_crop.append(cords)


            #print(policy_crop)

            if policy_crop == []:
                uuid_str = str(uuid.uuid4()) 
                img_name = consumer_mount_path+"/"+str(uuid_str)+".png"
                #print(img_name)
                cv2.imwrite(img_name,frame)

                #http_name = "http://0.0.0.0:3306/" +str(uuid_str)+".png"
                http_name = "http://"+BASE_URL+":3306/"+str(uuid_str)+".png"

                capture_doc = {
                "file_path": img_name,
                "file_url": http_name,
                "state": "untagged",
                "annotation_detection": [],
                "annotation_detection_history": [],
                "annotation_classification": "",
                "annotation_classification_history": [],
                "annotator": "",
                "date_added":timezone.now()}

                mp = MongoHelper().getCollection(part_id + "_dataset")
                mp.insert(capture_doc)
 
            for pol in policy_crop:
                cords=pol
                #print(cords)
                #for i in cords:
                x0 = int(cords[0])
                y0 = int(cords[1])
                x1 = int(cords[2])
                y1 = int(cords[3])

                crop = frame[y0:y1,x0:x1].copy()
                
                    #crop = resize_pad(crop)
                id_uuid = str(uuid.uuid4())+'.png'
                uuid_str = str(uuid.uuid4()) 
                img_name = consumer_mount_path+"/"+str(uuid_str)+".png"
                #print(img_name)
                cv2.imwrite(img_name,crop)
            
                #http_name = "http://0.0.0.0:3306/" +str(uuid_str)+".png"
                http_name = "http://"+BASE_URL+":3306/"+str(uuid_str)+".png"
                capture_doc = {
                        "file_path": img_name,
                        "file_url": http_name,
                        "state": "untagged",
                        "annotation_detection": [],
                        "annotation_detection_history": [],
                        "annotation_classification": "",
                        "annotation_classification_history": [],
                        "annotator": "",
                        "date_added":timezone.now()}
                
                mp = MongoHelper().getCollection(part_id + "_dataset")
                mp.insert(capture_doc)
        
        break
        
    return "success",200               


def start_camera_preview(workstation_id,camera_name):
    # access the workstation table
    workstation_id = ObjectId(workstation_id)
    mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    ws_row = mp.find_one({'_id': workstation_id})
    ws_camera_dict = ws_row.get('cameras')
    
    for i in ws_camera_dict:
        camera_id = i['camera_id']
        camera_name1 = i['camera_name']
        if camera_name1 ==  camera_name:
            break
    
    
    topic = str(workstation_id) + "_" + str(camera_id) + "_i"
    topic = topic.replace(":","")
    topic = topic.replace(".","")
    print("camera topic", topic)
    consumer = KafkaConsumer(topic, bootstrap_servers=KAFKA_BROKER_URL, auto_offset_reset='latest', fetch_max_bytes=41943040)
    for message in consumer:
        a = message.value.decode('utf-8')
        b = json.loads(a)
        
        im_b64_str = b["frame"]
        im_b64 = bytes(im_b64_str[2:], 'utf-8')
        im_binary = base64.b64decode(im_b64)

        im_arr = np.frombuffer(im_binary, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
            

        ret, jpeg = cv2.imencode('.jpg', img)
        
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def start_inference(workstation_id,camera_name,partid):
    # access the workstation table
    workstation_id = ObjectId(workstation_id)
    mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    ws_row = mp.find_one({'_id': workstation_id})
    ws_camera_dict = ws_row.get('cameras')
    
    for i in ws_camera_dict:
        camera_id = i['camera_id']
        camera_name1 = i['camera_name']
        if camera_name1 ==  camera_name:
            break
    
    topic = str(workstation_id) + "_" + str(str(camera_id).replace(".","")) + "_o"
    topic = topic.replace(":","")
    topic = topic.replace(".","")
    print(topic)
    consumer = KafkaConsumer(topic, bootstrap_servers=KAFKA_BROKER_URL, auto_offset_reset='latest', fetch_max_bytes=41943040)
    #consumer.poll()
    #consumer.seek_to_end()
        
    for message in consumer:
        a = message.value.decode('utf-8')
        b = json.loads(a)
        
        im_b64_str = b["frame"]
        im_b64 = bytes(im_b64_str[2:], 'utf-8')
        im_binary = base64.b64decode(im_b64)

        im_arr = np.frombuffer(im_binary, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
            

        ret, jpeg = cv2.imencode('.jpg', img)
        #cv2.imwrite("frame.jpg", jpeg)
        
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def start_camera_selection(data):
    # get data from the JSON POST object
    logging.basicConfig(filename='Status_producer.log',
                        level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    try:
        part_id_json = data['part_id']
    except:
        message = "part id not provided"
        status_code = 400
        return message, status_code

    try:
        workstation_id = data['workstation_id']
    except:
        message = "workstation id not provided"
        status_code = 400
        return message, status_code

    try:
        camera_select_list_from_post = data['camera_selected']
    except:
        message = "camera selected list not provided"
        status_code = 400
        return message, status_code

    try:
        overwrite_flag = data['overwrite_flag']
    except:
        overwrite_flag = False


    # access the parts table
    part_id = ObjectId(part_id_json)
    mp = MongoHelper().getCollection(PARTS_COLLECTION)
    part_row = mp.find_one({'_id': part_id})
    parts_camera_dict = None
    try:
        parts_camera_dict = part_row.get('camera_selected')
    except:
        pass
    #print("var is")
    #print(parts_camera_dict)

    ## Logic for if camera_selected not exist
    if parts_camera_dict == {} or parts_camera_dict is None:#--- Check this condition
        parts_camera_dict = {}
        parts_camera_dict[workstation_id] = camera_select_list_from_post
        new = {workstation_id:camera_select_list_from_post}
        #print(new)
        #new['camera_selected'] = camera_select_list_from_post
        new1 = {}
        new1['camera_selected'] = new
        #part_row['camera_selected'] = parts_camera_dict
        

        mp.update({'_id': part_row['_id']}, {'$set': new1})
        message = "Camera selected list updated successfully"
        status_code = 200
        return message, status_code
    else:
        ## Logic for if camera_selected exists
        if overwrite_flag is True:
            for key in parts_camera_dict:
                if key == workstation_id:
                    parts_camera_dict[key] = camera_select_list_from_post
                    new = {}
                    new = {workstation_id:camera_select_list_from_post}
                    #part_row['camera_selected'] = parts_camera_dict
                    new1 = {}
                    new1['camera_selected'] = new
                    #print(new1)
                    mp.update({'_id': part_row['_id']}, {'$set': new1})
                    message = "Camera selection updated"
                    status_code = 200
                    return message, status_code

        else:
            for key in parts_camera_dict:
                if key == workstation_id:
                    ### Checking for overwrite camera id's [camera_id's present and need to be raised]
                    existing_camera_list = parts_camera_dict[key]
                    for current_ in existing_camera_list:
                        if current_ in camera_select_list_from_post:
                            experiments_list = MongoHelper().getCollection(str(part_id)+"_experiment")
                            p = [p for p in experiments_list.find()]
                            for experiment in p:
                                experiment_status = experiment.get('status')
                                if experiment_status == "Running":
                                    message = "Overwrite flag is raised"
                                    status_code = 422
                                    return message, status_code
                    for new_ in camera_select_list_from_post:
                        if new_ not in existing_camera_list:
                            existing_camera_list.append(new_)
                    parts_camera_dict[key] = existing_camera_list
                    new = {}
                    new = {workstation_id:camera_select_list_from_post}
                    #part_row['camera_selected'] = parts_camera_dict
                    new1 = {}
                    new1['camera_selected'] = new
                    #print(new1)
                    mp.update({'_id': part_row['_id']}, {'$set': new1})
                    message = "Camera selection updated"
                    status_code = 200
                    return message, status_code


def get_camera_index_util(ws_id, camera_id):

    topic = str(ws_id)+"_"+str(camera_id)+"_i"
    topic = topic.replace(":","")
    topic = topic.replace(".","")
    #print("listening to topic "+str(topic))
    consumer = KafkaConsumer(topic, bootstrap_servers=KAFKA_BROKER_URL, auto_offset_reset='latest', fetch_max_bytes=41943040)

    if ws_id == "":
        return "workstation location not provided", 400

    for message in consumer:
        a = message.value.decode('utf-8')
        b = json.loads(a)
        im_b64_str = b["frame"]
        print(im_b64_str)
        im_b64 = bytes(im_b64_str[2:], 'utf-8')
        im_binary = base64.b64decode(im_b64)

        im_arr = np.frombuffer(im_binary, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

        ret, jpeg = cv2.imencode('.jpg', img)
        
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def get_camera_select_url_util(ws_name):
    if ws_name == "":
       return "workstation name not provided", 400

    mp = MongoHelper().getCollection(WORKSTATION_COLLECTION)
    coll = mp.find_one({"workstation_name": ws_name})
    cam_index_list = coll['available_indexs']
    ws_id = coll["_id"]

    feed_urls = []
    for i in eval(cam_index_list):
        dummmy_dct = {}
        url = "http://" + BASE_URL + ":8000/livis/v1/capture/camera_select_preview/{}/{}/".format(ws_id, i)
        dummmy_dct = {"camera_url": url, "workstation_name": str(ws_name), "camera_id": i}
        feed_urls.append(dummmy_dct)

    return feed_urls


############--
def start_demo_stream_util(data):
    try:
        file = data.get('myfile')
    except:
            message = "No file provided"
            status_code = 400
            return message, status_code

    try:
        w_id = data.get('workstation_id')
    except:
        message = "Workstation ID not provided"
        status_code = 400
        return message, status_code

    topic = str(w_id) + "_demo"
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                             value_serializer=lambda value: json.dumps(value).encode(), max_request_size=41943040000000000000000)

    if (str(file).split('.')[-1]) == "mp4" or (str(file).split('.')[-1]) == "avi":
        cap = cv2.VideoCapture(file)
        frames_iter = 0
        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                frames_iter = frames_iter + 1
                # Encoding and sending the frame
                cv2.imwrite("tmp.jpg", frame)
                with open("tmp.jpg", 'rb') as f:
                    im_b64 = base64.b64encode(f.read())
                payload_video_frame = {"frame": str(im_b64)}
                producer.send(topic, value=payload_video_frame)
            else:
                break
        cap.release()

    if (str(file).split('.')[-1]) == "jpg" or (str(file).split('.')[-1]) == "png":
        with open(file, 'rb') as f:
            im_b64 = base64.b64encode(f.read())
        payload_video_frame = {"frame": str(im_b64)}
        producer.send(topic, value=payload_video_frame)

    return "Success", 200


def start_inference_for_demo_util(workstation_id):

    topic = str(workstation_id) + "_demo"

    consumer = KafkaConsumer(topic, bootstrap_servers=KAFKA_BROKER_URL, auto_offset_reset='latest', fetch_max_bytes=41943040)

    for message in consumer:
        a = message.value.decode('utf-8')
        b = json.loads(a)

        im_b64_str = b["frame"]
        im_b64 = bytes(im_b64_str[2:], 'utf-8')
        im_binary = base64.b64decode(im_b64)

        im_arr = np.frombuffer(im_binary, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

        ret, jpeg = cv2.imencode('.jpg', img)

        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def quick_test_upload_util(data):
    try:
        file = data.FILES.get('myfile')
    except:
            message = "No file provided"
            status_code = 400
            return message, status_code

    ext=str(file).split('.')[-1]

    if ext not in ['mp4','avi','jpg','png']:
            message = "Not a valid file"
            status_code = 415
            return message,status_code

    return "Success", 200


def generate_quick_test_url_util(workstation_id):
    url = "http://" + BASE_URL + ":8000/livis/v1/capture/start_inference_for_demo/{}/".format(workstation_id)
    return url


def mobile_upload_util(data):
    try:
        files = data.FILES.getlist('myfile[]')
    except:
            message = "No file provided"
            status_code = 400
            return message, status_code

    if not files:
        return "Empty file", 200
    i = 0
    for file in files:
        file_name = "temp_mobile"+str(i)
        with open(file_name+".jpg", 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        i = i +1

    return "Success", 200





