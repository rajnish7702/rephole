from common.utils import MongoHelper
from livis.settings import *
from bson import ObjectId
from plan.utils import get_todays_planned_production_util
from common.utils import GetLabelData
import json

# ###############################################PART CRUDS#####################################
# def add_part_details_task(data):
#     """
#     {
# 	"part_number": "pt11",
# 	"part_description": "fjjff"
#     }
#     """
#     try:
#         family_name = data.get('part_number',None)
#         part_description = data.get('part_description',None)
#         kanban = data.get('kanban',None)
#         isdeleted = False
#         mp = MongoHelper().getCollection("parts")
#         collection_obj = {
#            'family_name' : family_name,
#         #    'part_description' : part_description,
#             'deployed':True,
#             'kanban':{'defects':['excess_material','scratch','Hole_blockage'],
#             'features':[]},
#            'isdeleted' : isdeleted
#         }
#         part_id = mp.insert(collection_obj)
#         print(part_id)
#         return part_id
#     except Exception as e:
#         return "Could not add part: "+str(e)
# def add_part_details_task(data):
# 	"""
# 	{
# 	"part_number": "pt11",
# 	"part_description": "fjjff"
# 	}
# 	"""
# 	try:
# 		part_name = data.get('part_name',None)
# 		family_name = data.get('part_type',None)
# 		worker_number = data.get('worker_number',None)


# 		isdeleted = False


# 		mp = MongoHelper().getCollection("parts")

# 		mp_data = mp.find_one({'family_name':family_name})
# 		part_names = mp_data.get('part_names')
# 		# worker_number=  mp_data.get('worker_number')
# 		# print(worker_number,"worker_numberworker_number")
# 		# part_names.append({'part_name':part_name,'worker_number':worker_number})


		


# 		collection_obj = {
# 		   'family_name' : family_name,
# 			'deployed':True,
# 			'kanban':{'defects':['excess_material','scratch','Hole_blockage'],
# 			'features':[]},
# 			'part_names':part_names,
# 			# 'worker_number':worker_number,
# 		   'isdeleted' : isdeleted
# 		}


# 		print(collection_obj)
# 		mp.update({'_id' : mp_data['_id']}, {'$set' :  collection_obj})

# 		return "Part added successfully"
# 	except Exception as e:
# 		return "Could not add part: "+str(e)


def add_part_details_task(data):
	"""
	{
	"part_number": "pt11",
	"part_description": "fjjff"
	}
	"""
	part_name = data.get('part_name',None)
	family_name = data.get('part_type',None)
	worker_number = data.get('worker_number',None)

	if part_name is None or part_name is "":
		return "Please provide part name", {}, 403

	if family_name is None or family_name is "":
		return "Please proide family name", {}, 403
	# if worker_number is None or worker_number is "": 
	# 	return "Please proide worker number", {}, 403


	

	mp = MongoHelper().getCollection("parts")

	# mp_data = mp.find_one({'family_name':family_name})
	# print(mp_data,'mp dataaaaa')
	# part_names = mp_data.get('part_names')
	# print(len(part_names),'\n\n\n\n')
	
	# part_names.append({'part_name':part_name,'worker_number':worker_number})
			



	collection_obj = {
		'family_name' : family_name,
		'deployed':True,
		'kanban':{'defects':['excess_material','scratch','Hole_blockage'],
		'features':[]},
		# 'part_names':part_names,
		'part_name':part_name,
		'worker_number':worker_number,
		'isdeleted' : False
	}


	print(collection_obj)
	# print(mp_data['_id'],'iddddddddd')
	# id_ = ObjectId(mp_data['_id'])
	# mp.update_one({'_id' : id_}, {'$set' :  collection_obj})
	mp.insert_one(collection_obj)



	return "Part added successfully",{},200
	






def delete_part_task(part_id):
	_id = part_id
	mp = MongoHelper().getCollection("parts")
	p = mp.find_one({'_id' : ObjectId(_id)})
	if p:
		isdeleted = p.get('isdeleted')
		if not isdeleted:
			p['isdeleted'] = True
		mp.update_one({'_id' : p['_id']}, {'$set' :  p})
		return _id
	else:
		return "Part not found."


# def update_part_task(data):
#     """
#     {
#         "_id": "242798143hdw7q33913413we2",
# 	    "part_number": "pt11",
# 	    "part_description": "fjjff"
#     }
#     """
#     _id = data.get('part_id')
#     if _id:
#         mp = MongoHelper().getCollection("parts")
#         pc = mp.find_one({'_id' : ObjectId(_id)})
#         if pc:
#             part_number = data.get('part_number',None)
#             part_description = data.get('part_description',None)
#             kanban = data.get('kanban',None)
#             if part_number:
#                 pc['part_number'] = part_number
#             if part_description:
#                 pc['part_description'] = part_description
#             if kanban:
#                 pc['kanban'] = kanban
#             mp.update({'_id' : pc['_id']}, {'$set' :  pc})
#         else:
#             return "Part not found"
#         return "Updated Successfully"
#     else:
#         return "Please enter the part ID."
def update_part_task(data):
	"""
	{
		"_id": "242798143hdw7q33913413we2",
		"family_name": "Rear_Acqustic_Panel",
		"part_names": "p3"
	}
	"""
	_id = data.get('part_id')
	# _id=True
	if _id:
		mp = MongoHelper().getCollection("parts")
		pc = mp.find_one({'_id' : ObjectId(_id)})
		if pc:
			family_name = data.get('family_name',None)
			part_names = data.get('part_names',None)
			worker_number = data.get('worker_number',None)


			kanban = data.get('kanban',None)
			if family_name:
				pc['family_name'] = family_name
			if part_names:
				pc['part_names'] = part_names
			if worker_number:
				pc['worker_number'] = worker_number
			# if kanban:
			#     pc['kanban'] = kanban
			mp.update_one({'_id' : pc['_id']}, {'$set' :  pc})
		else:
			return "Part not found"
		return "Updated Successfully"
	else:
		return "Please enter the part ID.",400
		

def get_part_details_task(part_id):
	mp = MongoHelper().getCollection("parts")
	p = mp.find_one({'_id' : ObjectId(part_id)})
	if p:
		return p
	else:
		return {}
#previously using 
# def get_all_family_names_task():
# 	mp = MongoHelper().getCollection("parts")
# 	families =[p for p in  mp.find({'isdeleted' : False})]
# 	family_data = []

# 	for p in families:
# 		family_data.append(p.get('family_name'))
# 	if family_data:
# 		return {'family_data': families}
# 	else:
# 		return {}
def get_all_family_names_task():
	mp = MongoHelper().getCollection("family_names")
	my_data=[]
	for x in mp.find():
		print(x)
		my_data.append(x)
	if my_data:
		return {'family_data': my_data}
	return my_data	

		# return x 
	# families =[p for p in  mp.find({'isdeleted' : False})]
	# family_data = []

	# for p in families:
	# 	family_data.append(p.get('family_name'))
	# if family_data:
	# 	return {'family_data': families}
	# else:
	# 	return {}

def get_all_parts():
	mp = MongoHelper().getCollection("parts")
	parts =[p for p in  mp.find({'isdeleted' : False})]
	# family_name = []
	# part_name=[]

	# for p in parts:
	# 	family_name.append(p.get('family_name'))
	# 	if family_name:
	# 		return {'parts_data': family_name}
	# 	else:
	# 		return {}
	# return parts
	# if part_name:


	# else:
	# 	return  "data not found",{}

		# parts_data.append(p.get('part_name'))
		# parts_data.append(p.get('worker_number'))


		
	# print(parts_data,"parts_dataparts_dataparts_data")
	print("parts",parts)
	return parts, 200
#prevously using 
# def get_all_part_type_util(data):
# 	family_name = data.get('family_name',None)
# 	if family_name is None:
# 		return "Family name not found", 400

# 	mp = MongoHelper().getCollection("parts")
# 	part_names = mp.find_one({'isdeleted':False,'family_name':family_name})
# 	if bool(part_names):
# 		return part_names, 200
# 	else:
# 		return {}, 200

def get_all_part_type_util(data):
	family_name = data.get('family_name',None)
	if family_name is None:
		return "Family name not found", 400

	mp = MongoHelper().getCollection("parts")
	# print(mp)
	parts =[p for p in  mp.find({'isdeleted' : False,'family_name':family_name})]
	# parts = mp.find().sort("part_name")
	# parts = mp.find()


	# part_name=[]

	# for p in parts:
	# 	# part_name.append(p.get('part_name'))
	# 	part_name.append(p)

	# print("part_name",part_name)
	if parts:
		return {'part_names': parts},200
	else:
		return {},200

	
	# return parts
	# if part_name:


	# else:
	# 	return  "data not found",{}

		# parts_data.append(p.get('part_name'))
		# parts_data.append(p.get('worker_number'))


	# mp = MongoHelper().getCollection("parts")

	# my_data=[]

	# for x in  mp.find().sort("part_name"):
	# 	my_data.append(x)
	# if bool(my_data):
	# 	# return my_data, 200
	# 	return {'part_names': my_data}

	# else:
	# 	return {}, 200
	

	

# def get_parts_task():
#     mp = MongoHelper().getCollection("parts")
	
#     parts = [p for p in mp.find({"$and" : [{"isdeleted": False}, { "isdeleted" : {"$exists" : True}}]}).sort( "$natural", -1 )]

#     for i in parts:
#         data = {}
#         part_obj_id = i["_id"]
#         mp = MongoHelper().getCollection('experiment')
#         i["experiments"] = [i for i in mp.find({'part_id' : str(part_obj_id)})]
#         info = GetLabelData(part_obj_id).get_metrics()
#         i["label_info"] = info
#     if parts:
#         return parts
#     else:
#         return []

######################################TBAL>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_configuration_list_util():
	#Get Configuration collection list
	mp = MongoHelper().getCollection(CONFIGURATION_COLLECTION)
	conf_list = []
	cc = mp.find({"in_use":True})
	for c in cc :
		conf_list.append(c["configuration_number"])
	return conf_list

def get_aircraft_number_new_util():
	mp = MongoHelper().getCollection(AIRCRAFT_NUMBER_COLLECTION)
	ac_num_list = []
	cc = mp.find({"is_used":False})#inprogress,completed
	for c in cc :
		ac_num_list.append(c["aircraft_number"])
	return ac_num_list

def get_aircraft_number_used_util():
	mp = MongoHelper().getCollection(AIRCRAFT_NUMBER_COLLECTION)
	ac_num_list = []
	cc = mp.find({"is_used":True})#inprogress,completed
	for c in cc :
	#     print(c)
		ac_num_list.append(c["aircraft_number"])
	return ac_num_list

# def get_aircraft_number_completed_util():
#     mp = MongoHelper().getCollection(AIRCRAFT_NUMBER_COLLECTION)
#     ac_num_list = []
#     cc = mp.find({"status":"completed"})#inprogress,completed
#     for c in cc :
#     #     print(c)
#         ac_num_list.append(c["aircraft_number"])
#     return ac_num_list

# def get_aircraft_number_inprogress_completed_util():
#     mp = MongoHelper().getCollection(AIRCRAFT_NUMBER_COLLECTION)
#     ac_num_list = []
#     cc = mp.find({"$or" :[{"status":"completed"},{"status":"inprogress"} ]})#inprogress,completed
#     for c in cc :
#     #     print(c)
#         ac_num_list.append(c["aircraft_number"])
#     return ac_num_list