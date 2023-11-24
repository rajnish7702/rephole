
from livis import settings as settings
from livis.settings import *
import os
from datetime import  datetime
import numpy as np
import cv2
import bson
import os
import shutil

from common.utils import MongoHelper



def create_folder_structure(family_name,part_name):
    '''
    part_name = varient1
    part_type = tower/rack
    '''

    today_date = datetime.now().strftime("%Y-%m-%d")
    date_path = os.path.join(datadrive_path+'/data_capture', today_date)
    
    f_str = os.path.join(date_path,family_name,part_name)
    print(f_str,'fstrrrrrrrrrrrr')

   
    if not os.path.isdir(f_str):
        os.makedirs(f'{f_str}')
        
    # return f_str+'/top',f_str+'/left',f_str+'/right',f_str+'/front',f_str+'/back',f_str+'/label_data'
    return f"{f_str}"






def save_data_util(data):
    print(data.data, ' save data API')
    from livis.settings import IP_ADDRESS
    
    '''
    payload as form data

    pay_load = {
        'part_name':'part1',
        'part_type':'tower',
        'operator':'xyz',
        'serial_id':'xyz',
        'top':[],
        'left':[],
        'right':[],
        'front':[],
        'back':[],
        'label_data:[]
        
    }
    '''
    part_name = data.data.get('part_name')
    family_name = data.data.get('family_name')
    operator = data.data.get('operator_name')
    images = data.data.get('Image')

    print("images*************************",images)

    # mob = data.data.get('operator_name')

    # serial_number = data.data.get('serial_no')
    # orientation = data.data.get('orientation')

    # print(orientation,'orientation nnnnnnnnnnn')

    print(part_name,'part nameeeeeeeeeeeeeeeeeeeee')

    if part_name is None:
        return "Part Name is not present",400
    if family_name is None:
        return "Part type is not present", 400
    if operator is None:
        return "Operator is not present", 400


    # top_path,left_path, right_path,front_path, back_path, label_data_path = create_folder_structure(serial_number,part_name,part_type,orientation)
    region_path = create_folder_structure(family_name,part_name)
    # print(region_path,'region pathhhhhhhhhhh',orientation)

    
    consolidated_files = {'images':images}

    # consolidated_files = {orientation:orientation_files}


    orientation_files_host = []





    for file_region, files in consolidated_files.items():

        for file in files:
            img_str = b''
            for chunk in file.chunks():
                img_str += chunk
            nparr = np.fromstring(img_str, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print(type(img_np),file_region)

            x = str(bson.ObjectId())
            c = os.path.join(region_path,consolidated_files+x+'.jpg')
            print(c)
            print('aaaaaaaaaaaaaaaaaaaaaaa')
            cv2.imwrite(os.path.join(region_path,consolidated_files+x+'.jpg'),img_np)
            serve = region_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            print(serve,'serveeeeeeeeeee path')
            orientation_files_host.append(serve+'/'+consolidated_files+x+'.jpg')
            # orientation_files_host.append(serve+orientation+'_'+x+'.jpg')

            # if file_region.lower() == 'top':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(top_path,'top_'+x+'.jpg'),img_np)
            #     serve = top_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     top_images_host.append(serve+'/top_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/top_'+x+'.jpg')


            # if file_region.lower() == 'left':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(left_path,'left_'+x+'.jpg'),img_np)
            #     serve = left_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     left_images_host.append(serve+'/left_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/left_'+x+'.jpg')


            # if file_region.lower() == 'right':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(right_path,'right_'+x+'.jpg'),img_np)
            #     serve = right_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     right_images_host.append(serve+'/right_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/right_'+x+'.jpg')


            # if file_region.lower() == 'front':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(front_path,'front_'+x+'.jpg'),img_np)
            #     serve = front_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     front_images_host.append(serve+'/front_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/front_'+x+'.jpg')


            # if file_region.lower() == 'back':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(back_path,'back_'+x+'.jpg'),img_np)
            #     serve = back_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     back_images_host.append(serve+'/back_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/back_'+x+'.jpg')


            # if file_region.lower() == 'label':
            #     x = str(bson.ObjectId())
            #     cv2.imwrite(os.path.join(label_data_path,'label_'+x+'.jpg'),img_np)
            #     serve = label_data_path.replace(datadrive_path,f'http://{IP_ADDRESS}:8001')
            #     label_data__images_host.append(serve+'/label_'+x+'.jpg')
            #     orientation_files_host.append(serve+'/label_'+x+'.jpg')

    
    # data = {'part_name':part_name,'part_type':part_type,'operator':operator,'serial_number':serial_number,'orientation':orientation,'top':top_images_host,'left':left_images_host,'right':right_images_host,'front':front_images_host,'back':back_images_host,'label_data':label_data__images_host}

    data = {'part_name':part_name,'operator':operator,'images':orientation_files_host}

    data['created_at'] = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    mp_col = MongoHelper().getCollection('data_capture')
    mp_col.insert_one(data)
    print(data)

    return data, 200







def get_captured_data_util(data):
    part_name = data.get('part_name')
    part_type = data.get('part_type')
    orientation = data.get('orientation')
    serial_number = data.get('serial_no')
    print(part_name,part_type,'*****************')
    query = []

    if part_name:
        query.append({'part_name':part_name})
    if part_type:
        query.append({'part_type':part_type})
    if orientation:
        query.append({'orientation':orientation})
    if serial_number:
        query.append({'serial_number':serial_number})

    print(query)
    mp_col = MongoHelper().getCollection('data_capture')
    mp_data = [i for i in mp_col.find({"$and":query}).sort([( '$natural', -1)])]

    print(mp_data,'mp dataaaaaaaaaa')
    images = []

    delete_empty_image_data()

    for i in mp_data:
        images.extend(i.get('images'))


    response = {'images':images}
    print(response,len(images))
    
    return response, 200


def delete_empty_image_data():
    mp = MongoHelper().getCollection('data_capture')
    mp_data = mp.find()
    data = []

    for i in data:
        if len(i.get('images')) == 0:
            mp.remove(i)

            mp.update({'_id': i['_id']}, {'$set': {}})





def delete_captured_image_util(data):

    image = data.get('image')
    part_name = data.get('part_name')
    part_type = data.get('part_type')
    orientation = data.get('orientation')
    serial_number = data.get('serial_no')
    
    query = []
    if part_name:
        query.append({'part_name':part_name})
    if part_type:
        query.append({'part_type':part_type})
    if orientation:
        query.append({'orientation':orientation})
    if serial_number:
        query.append({'serial_number':serial_number})

    print(query)
    mp_col = MongoHelper().getCollection('data_capture')
    mp_data = [i for i in mp_col.find({"$and":query}).sort([( '$natural', -1)])]


    try:
        mp_col.update(
            {'serial_number':serial_number,'part_name':part_name,'part_type':part_type,'orientation':orientation},
            {
                '$pull':{'images':image}
            },
            upsert=False
        )

        images = []
        c = 0
        for i in mp_data:
            c += 1
            print(i,'iiiiiiiiiiii')
            images.extend(i.get('images'))
            images_url = i.get('images')
            for img_url in images_url:
                if image != img_url:
                    images.append(img_url)
                else:
                    img_urls = img_url.replace(f'http://{IP_ADDRESS}:8001/',datadrive_path)
                    img_urls = os.path.join(img_urls)
                    os.remove(img_urls)

    except Exception as e:
        print(e)




    mp_data_ = [i for i in mp_col.find({"$and":query}).sort([( '$natural', -1)])]
    images_ = []
    for ii in mp_data_:
        images_.extend(ii.get('images'))
    response = {'images':images_}
  
    return response, 200

  




