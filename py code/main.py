#!user/bin/env python3

import cv2
import os
import sys,getopt
import signal
import time
from edge_impulse_linux import ImageImpulseRunner
import json
import time
import pyrebase

PB_Count = 0
Corn_Count = 0
Yogurt_Count = 0

flag = 0 

count_data = {"PB" : PB_Count,"Corn":Corn_Count, "Yogurt":Yogurt_Count}


runner = None

show_camera = True 

if(sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

def now()
    b = round(time.time() * 1000)
    print("NOW", b)
    return b

def get_webcams():  
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" % port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s" % (backendName, w, h, port))
                port_ids.append(port)
            camera.release()
    return port_ids


def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required if multiple cameras are connected>')

def main(argv):
    global PB_Count, Corn_Count,flag
    if flag == 0:
        firebaseConfig = {
        "apiKey": "AIzaSyCI4gw424j1-yZGRUvOCpaSXsWgpzZrokc",
        "authDomain": "invm-engineering.firebaseapp.com",
        "databaseURL": "https://invm-engineering-default-rtdb.firebaseio.com",
        projectId: "invm-engineering",
        storageBucket: "invm-engineering.appspot.com",
        messagingSenderId: "736003090433",
        appId: "1:736003090433:web:e80a0232adc1184bd17800",
        "measurementId: "G-XBHGN2SRWR"
}
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        db.child("Count").set(count_data)
        flag = 1


