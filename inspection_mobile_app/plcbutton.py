# USAGE
# python detect_aruco_video.py

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import requests
import threading
from common.utils import singleton
import json
import redis
#import services for plc Integration
from common.toyoda_io import *

@singleton
class VirtualPLC():
    def __init__(self):
        # define names of each possible ArUco tag OpenCV supports
        #self.vs = self.warmup(self.type)
        ## Need to add inspection url here / or pass as param.
        self.url = "http://localhost:8000/livis/v1/inspection/get_plc_button/"
        self.inspection_id = None
        self.thread = None
        self.killed = False
        self.workstation_id = None
        self.r = redis.Redis(host='13.235.133.102', port=5051, db=0)

    def make_api_call(self,url, params):
        r = requests.post(url, data=params)
        if r.status_code == 200:
            return True
        return False
    
    def start_button_service(self):
        if self.thread:
            self.stop_button_service()
        self.thread = threading.Thread(target=self.detect_button)
        self.thread.start()
        self.killed = False

    def stop_button_service(self):
        self.killed = True
        self.thread.join()
        time.sleep(0.2)
        self.killed = False
        self.thread = None


    def detect_button(self):
        # loop over the frames from the video stream
        while not self.killed:
            if self.r.get('trigger') == b'1': #whwn its pressed
                #yellow light
                #self.r.write(6,1)
                #red
                #self.r.write(8,1)
                #green
                #self.r.write(9,1)
                #light on 
                #self.r.write(7,1)
                #light off
                #self.plc_trigger.write(7,0)
                
                print("Making API call!!")
                x = {'inspection_id' : self.inspection_id , 'workstation_id' : self.workstation_id}
                y = json.dumps(x)
                self.make_api_call(self.url , y )

        
