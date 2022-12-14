#!user/bin/env python3

import cv2
import os
import sys,getopt
import signal
import time
from edge_impulse_linux import ImageImpulseRunner
import pyrebase 
import json
import time

PB_Count = 0
Corn_Count = 0
Yogurt_Count = 0

flag = 0 

