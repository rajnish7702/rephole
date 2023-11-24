
from operator import is_
from pyexpat import model
from turtle import left, right
from urllib.request import CacheFTPHandler
from common.utils import CacheHelper, MongoHelper
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
import bson


####################################################### mobile app +++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_all_parts_mobile_util(data):
	print(data)
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





def get_all_regions_util():
	
	project_mp = MongoHelper().getCollection("regions")
	col = project_mp.find()
	regions = []
	for i in col:
		regions.append(i.get('region_name'))
	return {'regions':regions}, 200
	mp = MongoHelper().getCollection("regions")
	regions =[p for p in  mp.find({'isdeleted' : False})]
	if regions:
		return regions, 200
	else:
		return {},200




def check_barcode_number_util(data):
	barcode_number = data.get('barcode_number',None)
	if barcode_number is None:
		return "Barcode number not present", 400

	mp = MongoHelper().getCollection("parts")
	mp_data = mp.find_one({'isdeleted' : False,'barcode_number':barcode_number})
	print(mp_data)
	print(type(mp_data))
	if mp_data is None:
		return "Barcode number not found", 400
	else:
		return mp_data, 200



def check_model_number_util(data):
	print(data,'data from check model number')
	model_number = data.get('model_number',None)
	if model_number is None:
		return "Model number not present", 400

	mp = MongoHelper().getCollection("parts")

	mp_data = mp.find_one({'isdeleted' : False,'model_number.model':model_number})

	if mp_data is None:
		return {"message":"Model number not found in DB"}, 200
	else:
		return mp_data, 200



def check_deployment(part_id):
	print("part_id::::",part_id)
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
		# url = f"http://{IP_ADDRESS}:8001/gorad/lincode/schneider/Blue_door/standalone/ai_controller/{dc_1}.jpg"
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
		
		# missing_features_dict['dummy'] = "1"

		print("defects:::",defects)
		print("missing_features_dict::::",missing_features_dict)
		print("status::::",status)
		overall_status_list.append(status)
		overall_defects.extend(defects)


		overall_missing_features.extend(missing_features)
		img_path = f'{IMAGE_STORAGE}/{dc_1}.jpg'
		cv2.imwrite(img_path,predicted_frame)
		# url = f"http://{IP_ADDRESS}:8001/gorad/lincode/schneider/Blue_door/standalone/ai_controller/{dc_1}.jpg"
		url = f"http://{IP_ADDRESS}:8001/{dc_1}.jpg"
		# status = "rejected"
		# missing_features_dict['test'] = "1"
		# missing_features_dict = list(missing_features_dict.keys())


		ind_dict_list.append({"image_url":url ,"status":status,"missing_features":missing_features_dict,"defects":defects})
	#Overall status
	if bool(len(overall_status_list)) :  
		if "rejected"  in overall_status_list:
			overall_status = "rejected"
		else:
			overall_status = "accepted"

		# overall_status = "accepted"
		resp = {"overall_status":overall_status,"ind_dict_list":ind_dict_list}
		print(resp)
		return resp 
	return resp


def get_defects_from_mongo(family_name):
	mp = MongoHelper().getCollection('parts')
	col = mp.find_one({'family_name':family_name})
	defects = col.get('kanban').get('defects')
	return defects



def get_defect_list(detector_predictions,family_name):
	# print(defects)
	defect_list = []
	for i in detector_predictions:
		if i in get_defects_from_mongo(family_name):
			defect_list.append(i)
	return defect_list


def check_kanban(defect_list):
	if bool(defect_list):
		is_accepted = "Rejected"
	else:
		is_accepted = "Accepted"
	return is_accepted

def list_to_dict(list_):
	to_dict = {}
	for i in list_:
		if not i in to_dict:
			to_dict[i] = list_.count(i)
	return to_dict

def check_feature(feature_list,pred_list):
	'''
	feature_list == > Fetch from mongodb 
	pred_list ==> predictions from worker
	'''
	missing_features = []
	for i in feature_list:
		if not i in pred_list:
			missing_features.append(i)
	return missing_features


def check_wrong_labels(feature_list,pred_list):
	'''
	feature_list == > Fetch from mongodb 
	pred_list ==> predictions from worker
	'''
	wrong_labels = []
	for i in pred_list:
		if not i in feature_list:
			wrong_labels.append(i)
	return wrong_labels


	   
def get_features_from_mongo(part_number):
	'''
	part_number is variant1, variant2
	'''
	mp = MongoHelper().getCollection('parts')
	mp_data = mp.find_one({'part_number':part_number})
	features = mp_data.get('kanban').get('features')
	return features



def check_kanban_mongo(inspection_id,predicted_frame_dict_list,prediction_dict_list,family_name,operator_name,worker_number,mobile_id,part_name):


	overall_status_list = []
	# overall_defect_list = ["laptop","book","person"]
	overall_defect_list=[]
	ind_dict_list = []

	ind_dict_list_accepted = []
	ind_dict_list_rejected = []
	
	ind_dict_list = []



	inference_images = []

	for i,j  in zip(predicted_frame_dict_list,prediction_dict_list):


		region = i
		predicted_frames_dict = predicted_frame_dict_list[i]
		predicted_labels_dict = prediction_dict_list[i]
		print(predicted_labels_dict,region,'from utils.................... ')

		

		for dict_key , dc_1 in zip(predicted_frames_dict,predicted_labels_dict):
			print(dict_key,dc_1)
			predicted_frame = predicted_frames_dict[dict_key]
			detector_predictions = predicted_labels_dict[dc_1]

			cv2.imwrite('dummy/'+str(bson.ObjectId())+'.jpg',predicted_frame)



		
			
			defect_list = get_defect_list(detector_predictions,family_name)
			is_accepted = check_kanban(defect_list)

			overall_status_list.append(is_accepted)
			overall_defect_list.extend(defect_list)
	
			fname = bson.ObjectId()

			cv2.imwrite(datadrive_path+'inspection_images/'+region+'_'+str(fname)+'.jpg',predicted_frame)
			img_url = f"http://{IP_ADDRESS}:8001/inspection_images/{region}_{str(fname)}.jpg"
			inference_images.append(img_url)

			ind_dict_list.append({"image_url":img_url ,"status":is_accepted,"defects":list_to_dict(defect_list),"region":region})
			if is_accepted == 'Rejected':
				ind_dict_list_rejected.append({"image_url":img_url ,"status":is_accepted,"defects":list_to_dict(defect_list),"region":region})
			
			if is_accepted == 'Accepted':
				ind_dict_list_accepted.append({"image_url":img_url ,"status":is_accepted,"defects":list_to_dict(defect_list),"region":region})




	if bool(len(overall_status_list)) :  
		if "Rejected"  in overall_status_list :
			overall_status = "Rejected"
		else:
			overall_status = "Accepted"

	

	# resp = {"inspection_id":inspection_id, "ind_dict_list":ind_dict_list_filter,"overall_status":overall_status}
	resp = {"inspection_id":inspection_id, "ind_dict_list_accepted":ind_dict_list_accepted,"ind_dict_list_rejected":ind_dict_list_rejected,"overall_status":overall_status}



	inspection_id = inspection_id

	createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print(createdAt)
	resp_col = resp
	resp_col['createdAt'] = createdAt
	resp_col['created_month'] =  datetime.now().strftime("%m")
	resp_col['created_year'] =  datetime.now().strftime("%Y")
	resp_col['created_date'] =  datetime.now().strftime("%d")

	resp_col['inference_images'] = inference_images
	resp_col['overall_status']=overall_status
	resp_col['overall_defect_list'] = list_to_dict(overall_defect_list)
	resp['part_name'] = part_name
	resp['family_name'] = family_name
	resp['operator_name'] = operator_name
	resp['worker_number'] = worker_number
	resp['mobile_id'] = mobile_id
	resp['start_time'] = CacheHelper().get_json('start_time')
	resp['end_time'] = createdAt
	
	resp_col['status'] = 'completed'
	mp = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')
	# mp_col = mp.find_one({"$and":[{"status":"started"},{"_id":ObjectId(inspection_id)}]})
	mp_col = mp.find_one({"$and":[{"family_name":family_name},{"_id":ObjectId(inspection_id)}]})
	print(mp_col,'mpcol mpcol ')

	mp.update_one({'_id' : mp_col['_id']}, {"$set" : resp_col})


	# mp.insert(resp_col)
	
	# resp_col['ind_dict_list'] = ind_dict_list_filter
	return resp_col


def get_model_numbers(barcode_number):
	mp = MongoHelper().getCollection('parts')
	mp_data = mp.find_one({'barcode_number':barcode_number})
	if bool(mp_data):
		return mp_data.get('model_number')
	else:
		return []

# def check_status(model_number_list,detector_predictions):
#     defect_list = []
#     for i in model_number_list:
#         if not i in detector_predictions:
#             defect_list.append(i) 
#     if bool(defect_list):
#         status = 'Rejected'
#     else:
#         status = 'Accepted'
#     return status, defect_list


def check_status(ocr_number,detector_predictions):
	if ocr_number in detector_predictions:
		is_accepted = 'Accepted'
	else:
		is_accepted = 'Rejected'
	return is_accepted    


def get_ocr_number(model_number):
	mp = MongoHelper().getCollection('parts')
	mp_data = mp.find_one({'isdeleted':False,'model_number.model':model_number})
	if bool(mp_data):
		return mp_data.get('ocr_number')
	else:
		return ""


def check_kanban_label(inspection_id,predicted_frame_dict_list,prediction_dict_list,operator_name,mobile_id,model_number):


	overall_status_list = []
	overall_defect_list = []
	ind_dict_list = []

	
	ind_dict_list = []

	inference_images = []

	for i,j  in zip(predicted_frame_dict_list,prediction_dict_list):


		region = i
		predicted_frames_dict = predicted_frame_dict_list[i]
		predicted_labels_dict = prediction_dict_list[i]

		

		for dict_key , dc_1 in zip(predicted_frames_dict,predicted_labels_dict):
			print(dict_key,dc_1)
			predicted_frame = predicted_frames_dict[dict_key]
			detector_predictions = predicted_labels_dict[dc_1]

			cv2.imwrite('dummy/'+str(bson.ObjectId())+'.jpg',predicted_frame)



			ocr_number = get_ocr_number(model_number)
			is_accepted = check_status(ocr_number,detector_predictions)

		
			overall_status_list.append(is_accepted)
			overall_defect_list.extend(detector_predictions)
	
			fname = bson.ObjectId()

			cv2.imwrite(datadrive_path+'inspection_images/'+region+'_'+str(fname)+'.jpg',predicted_frame)
			img_url = f"http://{IP_ADDRESS}:8001/inspection_images/{region}_{str(fname)}.jpg"
			inference_images.append(img_url)

			# ind_dict_list.append({"image_url":img_url ,"status":is_accepted,"defects":list_to_dict(defect_list),"region":region})
			# ind_dict_list.append({"image_url":img_url ,"status":is_accepted,"region":region})

	# ocr_number = get_ocr_number(model_number)
	# print(ocr_number)
	# print(detector_predictions)
	# is_accepted = check_status(ocr_number,detector_predictions)


	overall_status_list.append(is_accepted)

	if bool(len(overall_status_list)) :  
		if "Rejected"  in overall_status_list:
			overall_status = "Rejected"
		else:
			overall_status = "Accepted"

	

	resp = {"inspection_id":inspection_id, "ind_dict_list":ind_dict_list,"overall_status":overall_status}
 

	inspection_id = inspection_id

	createdAt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print(createdAt)
	resp_col = resp
	resp_col['createdAt'] = createdAt
	resp_col['created_month'] =  datetime.now().strftime("%m")
	resp_col['created_year'] =  datetime.now().strftime("%Y")
	resp_col['created_date'] =  datetime.now().strftime("%d")

	resp_col['inference_images'] = inference_images
	resp_col['overall_status']=overall_status
	resp_col['overall_defect_list'] = list_to_dict(overall_defect_list)
	
	resp['operator_name'] = operator_name
	resp['mobile_id'] = mobile_id
	resp['start_time'] = CacheHelper().get_json('start_time')
	resp['end_time'] = createdAt
	resp['model_number'] = model_number
	resp['ocr_number'] = ocr_number

	
	resp_col['status'] = 'completed'
	mp = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')

	mp_col = mp.find_one({"$and":[{"status":"started","model_number":model_number},{"_id":ObjectId(inspection_id)}]})

	mp.update({'_id' : mp_col['_id']}, {"$set" : resp_col})

	return resp_col




# def get_inference_mobile_util(data):
# 	print(data,'from inference mobile util..')
# 	t0 = datetime.now()
# 	CacheHelper().set_json({'start_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

# 	rch = CacheHelper()
# 	parameter = data.data.get("parameter",None)
# 	if parameter is None:
# 		return "Parameter is not present", 400

# 	mobile_id = data.data.get("mobile_id",None)
# 	if mobile_id is None:
# 		return "Mobile ID is not present", 400

# 	operator_name = data.data.get("operator_name",None)
# 	if operator_name is None:
# 		return "Operator Name is not present", 400

	
# 	inspection_id = data.data.get('inspection_id',None)
# 	if inspection_id is None:
# 		return "Inspection ID not present", 400

# 	barcode_number = data.data.get('barcode_number',None)
# 	if barcode_number is None:
# 		return "Barcode Number not present", 400

	

# 	parameter_id = ""
	
# 	print(parameter,'parameter parameter parameter parameter')
# 	print(mobile_id,'mobile_id mobile_id mobile_id mobile_id')
# 	print(operator_name,'operator_name operator_name operator_name operator_name')
# 	# print(part_type,'part_type part_type part_type part_type')
# 	# print(serial_no,'serial_no serial_no serial_no serial_no')
# 	print(inspection_id,'inspection_id inspection_id inspection_id inspection_id')

# 	print('\n\n\n\n')




# 	# mp = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')
# 	# mp.insert_one({'inspection_status':'started'})
# 	# print("parameter:::",parameter)

# 	if bool(parameter):
# 		#get part id
# 		project_mp = MongoHelper().getCollection("parts")
# 		a = project_mp.find({"part_number":parameter})
# 		print(a,'aaaaaaaaaaaaa')
# 		for i in a :
# 			print(i,'iiiiiiiiiiiiiiiiiii')
# 			parameter_id = i["_id"]
# 			print(parameter_id,'parameter idddddddddddddddddddddddddddddd')
# 		# form = NameForm(data.POST)

# 		#check whether the model in deplyed or not
# 		deployed_do_inspection = check_deployment(part_id = parameter_id )

# 		if deployed_do_inspection:
# 			# print("mobile_id",mobile_id)

# 			zone_data = {
# 						"parameter":parameter_id,
# 						"operator_name":operator_name}
# 			try:
# 				top_images = data.FILES.getlist('top')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not top_images:
# 				return "Empty file", 200

# 			try:
# 				left_images = data.FILES.getlist('left')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not left_images:
# 				return "Empty file", 200

# 			try:
# 				right_images = data.FILES.getlist('right')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not right_images:
# 				return "Empty file", 200

# 			try:
# 				front_images = data.FILES.getlist('front')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not front_images:
# 				return "Empty file", 200

# 			try:
# 				back_images = data.FILES.getlist('back')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not back_images:
# 				return "Empty file", 200


# 			try:
# 				screw = data.FILES.getlist('screw')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not screw:
# 				return "Empty file", 200
			
# 			try:
# 				sticker = data.FILES.getlist('sticker')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not sticker:
# 				return "Empty file", 200

# 			try:
# 				sticker_aesthatic = data.FILES.getlist('sticker_aesthatic')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not sticker_aesthatic:
# 				return "Empty file", 200

			
# 			try:
# 				missing_label = data.FILES.getlist('missing_label')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not missing_label:
# 				return "Empty file", 200

# 			try:
# 				switch_hole = data.FILES.getlist('switch_hole')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not switch_hole:
# 				return "Empty file", 200

# 			try:
# 				loose_fitting = data.FILES.getlist('loose_fitting')
# 			except:
# 					message = "No file provided"
# 					status_code = 400
# 					return message, status_code
# 			if not loose_fitting:
# 				return "Empty file", 200

# 			inspection_files = {'top':top_images,'left':left_images,'right':right_images,'front':front_images,'back':back_images,'screw':screw,'sticker':sticker,'sticker_aesthatic':sticker_aesthatic,'missing_label':missing_label,'switch_hole':switch_hole,'loose_fitting':loose_fitting}
			
# 			input_image_dict = {}


# 			for file_region, files in inspection_files.items():
# 				input_image_array = [] 

# 				for file in files:
# 					img_str = b''
# 					for chunk in file.chunks():
# 						img_str += chunk
# 					nparr = np.fromstring(img_str, np.uint8)
# 					img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# 					w,h,c = img_np.shape
					
# 					# img_np = cv2.resize(img_np,(w//2,h//2))#cv2.resize(predicted_frame,(w//2,h//2))
# 					# img_np = cv2.resize(img_np,(1920,1080))
# 					img_np = cv2.resize(img_np,(640,480))

# 					input_image_array.append(img_np)

# 					print(img_np.shape)
				
# 				input_image_dict[file_region] = input_image_array
			
# 			print(f"size of input_image_dict is :: {sys.getsizeof(input_image_dict)} bytes")
# 			rch.set_json({f"{mobile_id}_input_image_dict":input_image_dict})
# 			# rch.set_json({"input_image_dict":input_image_dict})
# 			# CacheHelper().set_json({'temp':input_image_dict})
# 			# print(input_image_dict)
# 			rch.set_json({f"{mobile_id}_parameter":parameter})
# 			rch.set_json({f"{mobile_id}_mobile_trigger":True})
# 			print('triggered.....')


# 			# rch.set_json({f"{mobile_id}_zone_data":zone_data})

# 			while True:
# 				inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
# 				mobile_trigger = rch.get_json(f"{mobile_id}_mobile_trigger")
# 				if mobile_trigger == False:
# 					if inspection_completed == True:
# 						predicted_frame_dict_list = rch.get_json(f"{mobile_id}_output_frame_list")
# 						prediction_dict_list =  rch.get_json(f"{mobile_id}_prediction_dict_list")
						

# 						print('***************',prediction_dict_list,'***************')
# 						# temp = predicted_frame_dict_list.get('top')
# 						# print(len(temp),'#############################')

# 						# inspection_id = str(bson.ObjectId())

# 						# inspection_id = INSPECTION_DATA_LOGS
# 						# inspection_name = INSPECTION_DATA_LOGS

# 						resp = check_kanban_mongo(inspection_id,predicted_frame_dict_list,prediction_dict_list,parameter,operator_name,mobile_id,part_type,serial_no)
# 						rch.set_json({f"{mobile_id}_inspection_completed":False})
# 						t1 = datetime.now()

# 						print(resp)
# 						print(f'Time taken for one complete cycle >>>image transfer and inference GPU:::  {(t1-t0).total_seconds()} sec')
# 						return resp ,200
# 		else:
# 			return "Not Deployed",200
# 	else:
# 		return "parameter missing!!!",401  

def get_inference_mobile_util(data):

	# print(data.data,"data")

	# print("datadatadatadatadatadatadatadatadatadatadatadata",data)

	# family_name=data.get('family_name',None)
	# mobile_id = data.get("mobile_id",None)
	# operator_name = data.get("operator_name",None)
	# part_name = data.get("part_name",None)

	# worker_number = data.get("worker_number",None)
	# inspection_id = data.get('inspection_id',None)
	# images = data.get('images')
	# imgs = images.FILES.getlist(images)
	# # imgs = images.getlist(images)


	# print(type(images),"typeos images")


	# print("imageimage",imgs)







	# print("family_namefamily_namefamily_namefamily_name",family_name)
	# print("mobile_idmobile_idmobile_idmobile_id",mobile_id)
	# print("operator_nameoperator_nameoperator_nameoperator_name",operator_name)
	# print("part_namepart_namepart_name",part_name)
	# # print("worker_numberworker_numberworker_number",worker_number)
	# print("inspection_idinspection_idinspection_idinspection_id",inspection_id)


	# print("data",data.data)

	# print(type(data.data))


	# data=json.loads(data)
	# print("data after dumps ",data)




	t0 = datetime.now()
	CacheHelper().set_json({'start_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

	rch = CacheHelper()
	family_name = data.data.get("family_name",None)
	if family_name is None:
		return "family_name is not present", 400

	mobile_id = data.data.get("mobile_id",None)
	CacheHelper().set_json({"mobile_id":mobile_id})
	if mobile_id is None:
		return "Mobile ID is not present", 400

	operator_name = data.data.get("operator_name",None)
	if operator_name is None:
		return "Operator Name is not present", 400

	part_name = data.data.get("part_name",None)
	if part_name is None:
		return "part name is not present", 400

	# worker_number = data.data.get("worker_number",None)
	# if worker_number is None:
	# 	return "worker_number  is not present", 400

	worker_number = "worker_number"

	
	inspection_id = data.data.get('inspection_id',None)
	if inspection_id is None:
		return "Inspection ID not present", 400

	# barcode_number = data.data.get('barcode_number',None)
	# if barcode_number is None:
	# 	return "Barcode Number not present", 400

	

	parameter_id = ""
	
	print(family_name,'parameter parameter parameter parameter')
	print(mobile_id,'mobile_id mobile_id mobile_id mobile_id')
	print(operator_name,'operator_name operator_name operator_name operator_name')
	# print(part_type,'part_type part_type part_type part_type')
	# print(serial_no,'serial_no serial_no serial_no serial_no')
	print(inspection_id,'inspection_id inspection_id inspection_id inspection_id')
	print(part_name,"part_name")

	print('\n\n\n\n')




	# mp = MongoHelper().getCollection(INSPECTION_DATA_LOGS+'_log')
	# mp.insert_one({'inspection_status':'started'})
	# print("parameter:::",parameter)

	if bool(family_name):
		#get part id
		project_mp = MongoHelper().getCollection("parts")
		a = project_mp.find({"family_name":family_name})
		# print(a,'aaaaaaaaaaaaa')
		# for i in a :
		# 	# print(i,'iiiiiiiiiiiiiiiiiii')
		# 	family_name_id = i["_id"]
		# 	print(family_name_id,'family_name_id idddddddddddddddddddddddddddddd')
		# form = NameForm(data.POST)

		#check whether the model in deplyed or not
		# deployed_do_inspection = check_deployment(part_id = family_name_id )
		deployed_do_inspection=True

		# images = data.FILES.getlist('images')
		# print(images,'imgess.................')
		if deployed_do_inspection:
			# print("mobile_id",mobile_id)

			# zone_data = {
			# 			"family_name":family_name_id,
			# 			"operator_name":operator_name}
			try:
				# images = data.FILES.getlist('images')
				images = data.FILES.getlist('Image')

			except:
					message = "No file provided"
					status_code = 400
					return message, status_code
			if not images:
				return "Empty file", 400
			
			
			inspection_files={"images":images}
			print(inspection_files,'inspection filewssssssssss')
			
			# inspection_files = {'top':top_images,'left':left_images,'right':right_images,'front':front_images,'back':back_images,'screw':screw,'sticker':sticker,'sticker_aesthatic':sticker_aesthatic,'missing_label':missing_label,'switch_hole':switch_hole,'loose_fitting':loose_fitting}
			
			input_image_dict = {}


			for file_region, files in inspection_files.items():
				input_image_array = [] 

				for file in files:
					img_str = b''
					for chunk in file.chunks():
						img_str += chunk
					nparr = np.fromstring(img_str, np.uint8)
					img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
					img_np=cv2.resize(img_np,(1280,1280))
					w,h,c = img_np.shape
					fname = bson.ObjectId()
					print("***********************************")
					print(w,h,c)
					
					
					# img_np = cv2.resize(img_np,(w//2,h//2))#cv2.resize(predicted_frame,(w//2,h//2))
					# img_np = cv2.resize(img_np,(1920,1080))
					# img_np = cv2.resize(img_np,(640,480))

					cv2.imwrite("/home/rajnish/Videos/livis_be_TASL_raphole/datadrive/input_images/"+'_'+str(fname)+'.jpg',img_np)

					input_image_array.append(img_np)

					print(img_np.shape)
				
				input_image_dict[file_region] = input_image_array
			
			print(f"size of input_image_dict is :: {sys.getsizeof(input_image_dict)} bytes")
			rch.set_json({f"{mobile_id}_input_image_dict":input_image_dict})
			rch.set_json({"input_image_dict":input_image_dict})
			CacheHelper().set_json({'temp':input_image_dict})
			# print(input_image_dict)
			rch.set_json({f"{mobile_id}_parameter":family_name})
			rch.set_json({f"{mobile_id}_mobile_trigger":True})
			print('triggered.....')


			# rch.set_json({f"{mobile_id}_zone_data":zone_data})

			while True:
				inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
				mobile_trigger = rch.get_json(f"{mobile_id}_mobile_trigger")
				
				print("#"*20)
				print(mobile_trigger)
				if mobile_trigger == False:
					if inspection_completed == True:
						predicted_frame_dict_list = rch.get_json(f"{mobile_id}_output_frame_list")
						prediction_dict_list =  rch.get_json(f"{mobile_id}_prediction_dict_list")
						

						print('***************',prediction_dict_list,'***************')
						# temp = predicted_frame_dict_list.get('top')
						# print(len(temp),'#############################')

						# inspection_id = str(bson.ObjectId())

						# inspection_id = INSPECTION_DATA_LOGS
						# inspection_name = INSPECTION_DATA_LOGS

						resp = check_kanban_mongo(inspection_id,predicted_frame_dict_list,prediction_dict_list,family_name,operator_name,worker_number,mobile_id,part_name)
						# family={"family_name":family_name,part_name}
						# part={"part_name":part_name}
						# resp.update(family)
						# resp.update(part)



						rch.set_json({f"{mobile_id}_inspection_completed":False})
						t1 = datetime.now()

						print(resp)
						print(f'Time taken for one complete cycle >>>image transfer and inference GPU:::  {(t1-t0).total_seconds()} sec')
						return resp ,200
		else:
			return "Not Deployed",200
	else:
		return "parameter missing!!!",401  




def get_inference_utils(data):
	print(data.data)
	images = data.FILES.getlist('images')
	images=cv2.resize(images,(1920,1280))
	print(images)
	return {'data':'data'}, 200



def get_inference_util(data):
	t0 = datetime.now()
	CacheHelper().set_json({'start_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

	rch = CacheHelper()
	# parameter = data.data.get("parameter",None)
   
	mobile_id = data.data.get("mobile_id",None)
	if mobile_id is None:
		return "Mobile ID is not present", 400

	operator_name = data.data.get("operator_name",None)
	if operator_name is None:
		return "Operator Name is not present", 400

	
	inspection_id = data.data.get('inspection_id',None)
	if inspection_id is None:
		return "Inspection ID not present", 400

	# barcode_number = data.data.get('barcode_number',None)
	# if barcode_number is None:
	# 	return "Barcode Number not present", 400

	
	
	try:
		raw_image = data.FILES.getlist('raw_image')
	except:
			message = "No file provided"
			status_code = 400
			return message, status_code
	if not raw_image:
		return "Empty file", 200

	
	inspection_files = {'raw_image':raw_image}

			
	input_image_dict = {}


	for file_region, files in inspection_files.items():
		input_image_array = [] 

		for file in files:
			img_str = b''
			for chunk in file.chunks():
				img_str += chunk
			nparr = np.fromstring(img_str, np.uint8)
			img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
			
			img_np = cv2.resize(img_np,(640,480))

			input_image_array.append(img_np)

			print(img_np.shape)
		
		input_image_dict[file_region] = input_image_array
	
	print(f"size of input_image_dict is :: {sys.getsizeof(input_image_dict)} bytes")
	rch.set_json({f"{mobile_id}_input_image_dict":input_image_dict})
	# rch.set_json({"input_image_dict":input_image_dict})
	# CacheHelper().set_json({'temp':input_image_dict})
	# print(input_image_dict)
	# rch.set_json({f"{mobile_id}_parameter":parameter})
	rch.set_json({f"{mobile_id}_mobile_trigger":True})
	print('triggered.....')


	# rch.set_json({f"{mobile_id}_zone_data":zone_data})

	while True:
		inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
		mobile_trigger = rch.get_json(f"{mobile_id}_mobile_trigger")
		if mobile_trigger == False:
			if inspection_completed == True:
				predicted_frame_dict_list = rch.get_json(f"{mobile_id}_output_frame_list")
				prediction_dict_list =  rch.get_json(f"{mobile_id}_prediction_dict_list")
				

				resp = check_kanban_label(inspection_id,predicted_frame_dict_list,prediction_dict_list,operator_name,mobile_id,barcode_number)

				rch.set_json({f"{mobile_id}_inspection_completed":False})
				t1 = datetime.now()

				print(resp)
				print(f'Time taken for one complete cycle >>>image transfer and inference GPU:::  {(t1-t0).total_seconds()} sec')
				return resp ,200

  

def get_inference_model_util(data):
	t0 = datetime.now()
	CacheHelper().set_json({'start_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

	rch = CacheHelper()
	# parameter = data.data.get("parameter",None)
   
	mobile_id = data.data.get("mobile_id",None)
	if mobile_id is None:
		return "Mobile ID is not present", 400

	operator_name = data.data.get("operator_name",None)
	if operator_name is None:
		return "Operator Name is not present", 400

	
	inspection_id = data.data.get('inspection_id',None)
	if inspection_id is None:
		return "Inspection ID not present", 400

	model_number = data.data.get('model_number',None)
	if model_number is None:
		return "Model Number not present", 400

	
	
	# try:
	#     model_image = data.FILES.getlist('model_image')
	# except:
	#         message = "No file provided"
	#         status_code = 400
	#         return message, status_code
	# if not model_image:
	#     return "Empty file", 200


	
	try:
		ocr_image = data.FILES.getlist('ocr_image')
		print(ocr_image,'ocr image')
	except:
			message = "No file provided"
			status_code = 400
			return message, status_code
	if not ocr_image:
		return "Empty file", 200

	
	inspection_files = {'ocr_image':ocr_image}

			
	input_image_dict = {}


	for file_region, files in inspection_files.items():
		input_image_array = [] 

		for file in files:
			img_str = b''
			for chunk in file.chunks():
				img_str += chunk
			nparr = np.fromstring(img_str, np.uint8)
			img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
			
			img_np = cv2.resize(img_np,(640,480))

			input_image_array.append(img_np)

			print(img_np.shape)
		
		input_image_dict[file_region] = input_image_array
	
	print(f"size of input_image_dict is :: {sys.getsizeof(input_image_dict)} bytes")
	rch.set_json({f"{mobile_id}_input_image_dict":input_image_dict})
	# rch.set_json({"input_image_dict":input_image_dict})
	# CacheHelper().set_json({'temp':input_image_dict})
	# print(input_image_dict)
	# rch.set_json({f"{mobile_id}_parameter":parameter})
	rch.set_json({f"{mobile_id}_mobile_trigger":True})
	print('triggered.....')


	# rch.set_json({f"{mobile_id}_zone_data":zone_data})

	while True:
		inspection_completed = rch.get_json(f"{mobile_id}_inspection_completed")
		mobile_trigger = rch.get_json(f"{mobile_id}_mobile_trigger")
		if mobile_trigger == False:
			if inspection_completed == True:
				predicted_frame_dict_list = rch.get_json(f"{mobile_id}_output_frame_list")
				prediction_dict_list =  rch.get_json(f"{mobile_id}_prediction_dict_list")
				

				resp = check_kanban_label(inspection_id,predicted_frame_dict_list,prediction_dict_list,operator_name,mobile_id,model_number)

				rch.set_json({f"{mobile_id}_inspection_completed":False})
				t1 = datetime.now()

				print(resp)
				print(f'Time taken for one complete cycle >>>image transfer and inference GPU:::  {(t1-t0).total_seconds()} sec')
				return resp ,200  

def get_reference_image_util(data):
	family_name = data.get('family_name',None)
	if family_name is None:
		return "Family name is not present", 400
	if bool(data):
			# parameter = data.get("parameter",None)
		# image_url_path = f"http://localhost:8001/F:/tata_raphole/BE_RAP_HOLE/label_inspction/datadrive/Reference_images/{parameter}/reference_image.jpg"
		image_url_path = f"http://{IP_ADDRESS}:8001/Reference_images/{family_name}/reference.jpg"

		# image_url_path = f"http://{IP_ADDRESS}:8001/gorad/lincode/schneider/Blue_door/standalone/ai_controller/bluedoor_weights/bluedoor/reference.jpg"
		return image_url_path,200
	else:
		return "None",401

	

