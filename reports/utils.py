from ast import operator
from textwrap import indent
from common.utils import *
from bson import ObjectId
from livis.settings import *
from django.utils import timezone
from pymongo import MongoClient
from datetime import timedelta
import numpy as np
from common.utils import CacheHelper, MongoHelper


def get_megareport_util(data):
    print(data)
    from_date = data.get('from_date', None)
    to_date = data.get('to_date', None)
    status = data.get('status',None) #pass / fail
    skip = int(data.get('skip',None))
    limit = int(data.get('limit',None))
    operator_name = data.get('operator_id')
    part_name = data.get('part_name',None)
    part_type = data.get('part_type',None)
    worker_number = data.get('worker_number',None)

    



    query = []
    if from_date:
        query.append({'start_time': {"$gte":from_date}})
    if to_date:
        query.append({'end_time': {"$lte":to_date}})
    if status == 'Accepted' or status == 'Rejected':
        query.append({'overall_status':status})
    if status == 'Aborted':
        query.append({'status':'started'})
        
    if operator_name:
        query.append({'operator_name':operator_name})
    if part_name:
        query.append({'part_name':part_name})
    if part_type:
        query.append({'part_type':part_type})
    if worker_number:
        query.append({'worker_number':worker_number})
    


    if bool(query):
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find({"$and":query}).sort([( '$natural', -1)]) ]
    else:
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find().sort([( '$natural', -1)])]
    
    q = []
    #print("********Len of objs "+str(len(p)))
    if skip is not None and limit is not None:
        # for items in objs[skip:skip+limit]:
        for items in objs[skip:limit]:


            q.append(items)
    else:
        q = objs.copy()

    print("length of objects"+str(len(objs)))
    
    response = {"data":q,"total_length":str(len(objs))}
    print(response,"response from be ")
    return response



# def set_flag_util(data):
#     master_obj_id = data['master_obj_id']
#     slave_obj_id = data['slave_obj_id']
#     remark = data['remark']

#     mp = MongoHelper().getCollection(master_obj_id+"_log")

#     process_attributes = mp.find_one({'_id' : ObjectId(slave_obj_id)})

#     process_attributes['remarks']= remark
#     process_attributes['flagged']= True
#     print(process_attributes)
#     mp.update({'_id' : ObjectId(slave_obj_id) }, {'$set' :  process_attributes})
#     process_attributes = mp.find_one({'_id' : ObjectId(slave_obj_id)})
    
#     #goto annotation and set as untagged
#     part_id = process_attributes['part_id']
#     captured_original_frame_http = process_attributes['captured_original_frame_http']
#     captured_original_frame = process_attributes['captured_original_frame']
    
#     mp = MongoHelper().getCollection(str(part_id)+"_dataset")
    
#     capture_doc = {
#                         "file_path": captured_original_frame,
#                         "file_url": captured_original_frame_http,
#                         "state": "untagged",
#                         "annotation_detection": [],
#                         "annotation_detection_history": [],
#                         "annotation_classification": "",
#                         "annotation_classification_history": [],
#                         "annotator": "",
#                         "date_added":timezone.now()}
#     mp.insert(capture_doc)
#     return process_attributes


# def edit_remark_util(data):
#     master_obj_id = data['master_obj_id']
#     slave_obj_id = data['slave_obj_id']
#     remark = data['remarks']

#     mp = MongoHelper().getCollection(master_obj_id)

#     process_attributes = mp.find_one({'_id' : ObjectId(slave_obj_id)})

#     process_attributes['remarks']= remark
#     print(process_attributes)
#     mp.update({'_id' : ObjectId(slave_obj_id) }, {'$set' :  process_attributes})
#     process_attributes = mp.find_one({'_id' : ObjectId(slave_obj_id)})
#     return "success"


def get_daywise_report_util(data):
    "This function return the daywise report"
    # from_date = data.get('from_date',None)
    date = data.get("date",None)


    format = "%Y-%m-%d %H:%M:%S"#'%b %d %Y %I:%M%p' # The format
    
    datetime_str = datetime.datetime.strptime(date, format)
    day_after = str(datetime_str  + timedelta(days = 1))
    print(date, day_after)

    print(date)
    # mp = MongoHelper().getCollection('inspections_log')
    query = []
    if date:
        query.append({'createdAt':{'$gte':date}}) # "date":"2022-09-07 13:42:36"
        query.append({'createdAt':{'$lte':day_after}}) # "date":"2022-10-07 13:42:36"



    if bool(query):
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find({"$and":query}).sort([( '$natural', -1)]) ]
    else:
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find().sort([( '$natural', -1)])]
    
   
    

    resp = {}
    print(len(objs))

    print(resp,"respresprespresp")
    print(objs)
   

    resp['data'] = objs
    return  resp,200
        

def  get_dash_board_reports_util(data):
    import datetime
    print(data)

    date = str(datetime.datetime.now()).split('.')[0]
    print(date,'dateeeeeeee')
    today_date = str(datetime.datetime.now().replace(hour=0,minute=0,second=1)).split('.')[0]

    format = "%Y-%m-%d %H:%M:%S"#'%b %d %Y %I:%M%p' # The format
    
    datetime_str = datetime.datetime.strptime(today_date, format)
    day_after = str(datetime_str  + timedelta(days = 1))


    family_name = data.get('family_name',  None)
    part_name = data.get('part_name',  None)





    query_1 = []
    # today_date = datetime.datetime.now().strftime("%d")
    # print(today_date)
    # query_1.append({'created_date':{'$gte':today_date}})

    # date = "2022-09-29 00:00:01"

    query_1.append({'produced_on':{'$gte':today_date}})
    query_1.append({'produced_on':{'$lte':day_after}})
    
    print(date, day_after)


    resp = {}
    if family_name:
        query_1.append({'family_name':family_name})
    if part_name:
        query_1.append({'part_name':part_name})

    
    
    total_accepted = 0
    total_rejected = 0
    total_aborted = 0
    mp = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')
    print(query_1,'qyery 1')

    mp_col = mp.find({"$and":query_1})
   

    print(mp_col,'mp col')
    for i in mp_col:
        print(i,'iiiiiiiiii')
        print(i.get('part_name'))
        if i.get('overall_status') == 'Accepted':
            total_accepted += 1
        if i.get('overall_status') == 'Rejected':
            total_rejected += 1
        if i.get('status') == 'started':
            total_aborted += 1


    resp['total_inspecetd'] = total_accepted + total_rejected + total_aborted
    resp['total_accepted'] = total_accepted
    resp['total_rejected'] = total_rejected
    resp['total_aborted'] = total_aborted
    print(resp)
    return resp ,200
                


def get_overall_report_util(data):
    print("HERRRRE>>>>")
    print(data, "inside get over report")
    "This function return the overall report"
    # from_date = data.get('from_date',None)
    aircraft_number = data.get("aircraft_number")
    from_date = data.get('from_date',None)
    end_date = data.get('to_date',None)
    # date = data.get("date",None)
    fod = data.get("fod",None)
    zone_level_1 = data.get("zone_level_1",None)
    zone_level_2 = data.get("zone_level_2",None)
    fs_range = data.get("fs_range",None)
    wl_bl_range = data.get("wl_bl_range",None)
    operator_name = data.get("operator",None)
    supervisor_name = data.get("supervisor",None)
    scan_status = "completed"
    inspection_status = data.get("inspection_status",None)
    ais_mp = MongoHelper().getCollection(AIRCRAFT_INSPECTION_SUMMARY)
    query_1 = []
    query_2 = []
    resp = {}
    aircraft_numbers_list = []
    zone_level_1_list = []
    zone_level_2_list = []
    scanned_by_list = []
    supervisor_list = []
    fs_range_list = []
    wl_bl_range_list = []
    overall_region_list = []
    if bool(aircraft_number):
        query_1.append({"aircraft_number" : aircraft_number})

    if bool(from_date):query_2.append({"scanned_at":{"$gte":from_date}})
    if bool(end_date):query_2.append({"scanned_at":{"$lte":end_date}})
    if bool(zone_level_1):query_2.append({"zone_level_1":zone_level_1})
    if bool(zone_level_2):query_2.append({"zone_level_2":zone_level_2})
    if bool(fs_range):query_2.append({"fs_range":fs_range})
    if bool(wl_bl_range):query_2.append({"wl_bl_range":wl_bl_range}) 
    if bool(operator_name):query_2.append({"scanned_by":operator_name}) 
    if bool(supervisor_name):query_2.append({"supervisor":supervisor_name}) 
    if bool(inspection_status):query_2.append({"inspection_status":inspection_status}) 
    query_2.append({"scan_status":"completed"})
    query_2.append({"operator_flag":False})
    if bool(query_1):
        aircraft_collections_cursor = ais_mp.find({"$and":query_1})
    else:
        aircraft_collections_cursor = ais_mp.find()#{"$and":query_1}
    aircraft_number_list= []
    for collection in aircraft_collections_cursor:
        # print("collection",collection)
        aircraft_number_list.append(collection["aircraft_number"])
    for ac_numbers in aircraft_number_list:
        ac_collection = MongoHelper().getCollection(ac_numbers)
        if bool(query_2):
            inspections_collection_cursor = ac_collection.find({"$and":query_2})
        else:
            inspections_collection_cursor = ac_collection.find()#{"scanned_at" : {"$eq":date}}
        # print("inspections_collection_cursor",inspections_collection_cursor)
        for inspections_collection in inspections_collection_cursor:
            # print("inspections_collection",inspections_collection)

            obj = { 
                    "Plant":"TBAL",
                    "Program":"AH64_fuselage",
                    "aircraft_number": inspections_collection["aircraft_number"],
                    "date" : inspections_collection["scanned_at"],
                    "discovered_by" : inspections_collection["scanned_by"],
                    "defects":inspections_collection["defects"],
                    "status":inspections_collection["inspection_status"],
                    "supervisor":inspections_collection["supervisor"],
                    # "discovered_by": inspections_collection["supervisor"],
                    "exterior/interior":inspections_collection["zone_level_1"],
                    "sub_assembly":inspections_collection["zone_level_2"],
                    "fs_range":inspections_collection["fs_range"],
                    "wl_bl_range":inspections_collection["wl_bl_range"],
                    "zone":inspections_collection["fs_range"]+"-"+inspections_collection["wl_bl_range"]+"_"+inspections_collection["zone_level_2"]+"-"+inspections_collection["zone_level_1"],
                    "image_folder_path":"oasfn"#inspections_collection["image_folder_path"]
            }

            overall_region_list.append(obj)
            aircraft_numbers_list.append(inspections_collection["aircraft_number"],)
            zone_level_1_list.append(inspections_collection["zone_level_1"])
            zone_level_2_list.append(inspections_collection["zone_level_2"])
            scanned_by_list.append(inspections_collection["scanned_by"])
            supervisor_list.append(inspections_collection["supervisor"])
            fs_range_list.append(inspections_collection["fs_range"])
            wl_bl_range_list.append(inspections_collection["wl_bl_range"])

    resp = {
        "aircraft_numbers_list" : list(np.unique(aircraft_numbers_list)),
        "zone_level_1_list" : list(np.unique(zone_level_1_list)),
        "zone_level_2_list" : list(np.unique(zone_level_2_list)),
        "scanned_by_list" : list(np.unique(scanned_by_list)),
        "supervisor_list" : list(np.unique(supervisor_list)),
        "fs_range_list" : list(np.unique(fs_range_list)),
        "wl_bl_range_list" : list(np.unique(wl_bl_range_list)),
        "overall_region_list" : overall_region_list
    }
    print("overall_region_list",len(overall_region_list))
    return resp ,200

def create_folder(directory):
    if os.path.exists(directory):
        pass
        # print(f'{directory} is exist!!')
    else:
        os.makedirs(directory) 
        print(f'{directory} is created!!')

def write_excel(list_dict, file_name):
    print(len(list_dict))
    create_folder(file_name)
    # list_dict 
    df = pd.DataFrame(list_dict)
    file_path = file_name + '/overall_report.xlsx'
    # df.to_excel(file_path)
    # file_path = file_name + ".csv"
    df.to_excel(file_path)
    file_path = file_path.split("tbal")[1]
    return file_path

def export_util(data):
    print(data,"Thisis export>>>>>>")
    resp ,status = get_overall_report_util(data)
    # print(len(resp), "Thisis export>>>>>>")
    list_dict = resp["overall_region_list"]

    # fn ="/home/tbal/Desktop/reports/"
    fn = EXPORT_DIRECTORY
    file_path = write_excel(list_dict, file_name = fn)
    print(file_path)
    return f"http://{IP_ADDRESS}:8001{file_path}" , 200



def export_csv_util(data):
    
    # from_date = data.get('from_date', None)
    # to_date = data.get('to_date', None)
    # status = data.get('status',None) #pass / fail
    # skip = int(data.get('skip',None))
    # limit = int(data.get('limit',None))
    # operator_name = data.get('operator_name')
    # part_name = data.get('part_name',None)
    # part_type = data.get('part_type',None)



    # query = []
    # if from_date:
    #     query.append({'start_time': {"$gte":from_date}})
    # if to_date:
    #     query.append({'end_time': {"$lte":to_date}})
    # if status:
    #     query.append({'overall_status':status})
    # if operator_name:
    #     query.append({'operator_name':operator_name})
    # if part_name:
    #     query.append({'part_name':part_name})
    # if part_type:
    #     query.append({'part_type':part_type})

    # if bool(query):
    #     inspectionid_collection = MongoHelper().getCollection('inspections_log')
    #     objs = [i for i in inspectionid_collection.find({"$and":query}).sort([( '$natural', -1)]) ]
    # else:
    #     inspectionid_collection = MongoHelper().getCollection('inspections_log')
    #     objs = [i for i in inspectionid_collection.find().sort([( '$natural', -1)])]
    from_date = data.get('from_date', None)
    to_date = data.get('to_date', None)
    status = data.get('status',None) #pass / fail
    # skip = int(data.get('skip',None))
    # limit = int(data.get('limit',None))
    operator_name = data.get('operator_name')
    part_name = data.get('part_name',None)
    part_type = data.get('part_type',None)
    



    query = []
    if from_date:
        query.append({'start_time': {"$gte":from_date}})
    if to_date:
        query.append({'end_time': {"$lte":to_date}})
    if status == 'Accepted' or status == 'Rejected':
        query.append({'overall_status':status})
    if status == 'Aborted':
        query.append({'status':'started'})
        
    if operator_name:
        query.append({'operator_name':operator_name})
    if part_name:
        query.append({'part_name':part_name})
    if part_type:
        query.append({'part_type':part_type})
    


    if bool(query):
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find({"$and":query}).sort([( '$natural', -1)]) ]
    else:
        inspectionid_collection = MongoHelper().getCollection('inspections_log')
        objs = [i for i in inspectionid_collection.find().sort([( '$natural', -1)])]
    
    print(objs)
    import pandas as pd
    df = pd.DataFrame(objs)
    import bson
    filename = bson.ObjectId()
    df.to_csv(datadrive_path+'reports/'+str(filename)+".csv")
  
    return f"http://{IP_ADDRESS}:8001/reports/"+str(filename)+".csv"