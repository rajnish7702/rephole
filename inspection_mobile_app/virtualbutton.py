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
@singleton
class VirtualButton():
    def __init__(self):
        # define names of each possible ArUco tag OpenCV supports
        self.ARUCO_DICT = {
        	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
        	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
        	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
        	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
        	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
        	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
        	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
        	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
        	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
        	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
        	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
        	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
        	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
        	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
        	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
        	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
        	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
        	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
        	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
        	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
        	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
        }
        self.type = "DICT_5X5_100"
        self.vs = self.warmup(self.type)
        ## Need to add inspection url here / or pass as param.
        self.url = "http://localhost:8000/livis/v1/inspection/get_virtual_button/"
        self.inspection_id = None
        self.thread = None
        self.killed = False
        self.workstation_id = None

    def make_api_call(self,url, params):
        r = requests.post(url, data=params)
        if r.status_code == 200:
            return True
        return False

    def warmup(self, type):
    # load the ArUCo dictionary and grab the ArUCo parameters
        print("[INFO] detecting '{}' tags...".format(type))
        self.arucoDict = cv2.aruco.Dictionary_get(self.ARUCO_DICT[type])
        self.arucoParams = cv2.aruco.DetectorParameters_create()
        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src=3).start()
        time.sleep(2.0)
        return vs
    
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
        button_pressed = False
        c = 0
        d = 0
        # loop over the frames from the video stream
        while not self.killed:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 600 pixels
            frame = self.vs.read()
            if frame is None:
                print("none frame received from vitual camera")
                continue
            else:
                pass
            frame = imutils.resize(frame, width=1000)
            # detect ArUco markers in the input frame
            (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
            	self.arucoDict, parameters=self.arucoParams)
            #print("Found corners : : : : ", corners)
            # verify *at least* one ArUco marker was detected
            if len(corners) > 0:
                # flatten the ArUco IDs list
                ids = ids.flatten()
        		# loop over the detected ArUCo corners
                for (markerCorner, markerID) in zip(corners, ids):
                    # extract the marker corners (which are always returned
                    # in top-left, top-right, bottom-right, and bottom-left
                    # order)
                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))
                    # draw the bounding box of the ArUCo detection
                    #cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    #cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    #cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    #cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    # compute and draw the center (x, y)-coordinates of the
                    # ArUco marker
                    #cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    #cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    #cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                    # draw the ArUco marker ID on the frame
                    #cv2.putText(frame, str(markerID),
                    #	(topLeft[0], topLeft[1] - 15),
                    #	cv2.FONT_HERSHEY_SIMPLEX,
                    #	0.5, (0, 255, 0), 2)
                    #cv2.putText(frame, "BUTTON NOT PRESSED",
                    #	(10, 100),
                    #	cv2.FONT_HERSHEY_SIMPLEX,
                    #	0.5, (0, 255, 0), 2)
                    button_pressed = False
                    c=0
            else:
                button_pressed = True
        		#cv2.putText(frame, "BUTTON PRESSED : " + str(d),
        		#		(10, 100),
        		#		cv2.FONT_HERSHEY_SIMPLEX,
        		#		0.5, (0, 255, 0), 2)
                if button_pressed and c == 0:
                    print("Making API call!!")
                    x = {'inspection_id' : self.inspection_id , 'workstation_id' : self.workstation_id}
                    y = json.dumps(x)
                    self.make_api_call(self.url , y )
                    c+=1
                    button_pressed = False
                    d+=1
        	# show the output frame
        
