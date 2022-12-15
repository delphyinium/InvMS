#!user/bin/env python3

from pyexpat import model
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

def now():
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
        "projectId": "invm-engineering",
        "storageBucket": "invm-engineering.appspot.com",
        "messagingSenderId": "736003090433",
        "appId": "1:736003090433:web:e80a0232adc1184bd17800",
        "measurementId": "G-XBHGN2SRWR"
}
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        db.child("Count").set(count_data)
        flag = 1

    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model_path = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)


    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + '/' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('No camera found')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found, please specify the camera port ID as the second arg to use this script")
                videoCaptureDeviceId = port_ids[0]
            
            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s" % (backendName, w, h, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera. Logs.")

            next_frame = 0 # defines FPS, limit is best at 10 for RPi

            for res, img in runner.classifier(videoCaptureDeviceId):

                if "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['classification']))
                    count = len(res)["result"]["bounding_boxes"]

                    for bb in res["result"]["bounding_boxes"]:
                        img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (0, 255, 0), 2)
                        Label = bb['label']
                        score = bb['value']
                        print(Label, score)
                        if score > 0.70 :
                            if Label == "Peanut Butter":
                                PB_Count += 1
                            elif Label == "Corn":
                                Corn_Count += 1
                            elif Label == "Yogurt":
                                Yogurt_Count += 1
                        db.child("count").update({"PB":PB_Count,"Corn":Corn_Count,"Yogurt":Yogurt_Count})
                        PB_Count, Corn_Count, Yogurt_Count = 0,0,0
                    if (show_camera):
                        cv2.imshow('edgeimpulse', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    next_frame = now() + 10
        finally:
                if (runner):
                    runner.stop()

if __name__ == "__main__":
    main(sys.argv[1:])