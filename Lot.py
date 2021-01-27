import cv2
import numpy as np
import os
import time

class Lot:
    def __init__(self,x1,y1,x2,y2,time_stamp = time.time()):
        self.id = None
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2 
        self.isParking = False
        self.time_stamp = time_stamp

    def setId(self,id):
        self.id = id

    def getId(self):
        return self.id

    def getTimeStamp(self):
        return self.time_stamp
    
    def setTimeStamp(self,time_stamp):
        self.time_stamp = time_stamp

    def isParking(self):
        return self.isParking

    def update(self,status, time):
        self.isParking = status
        self.time_stamp = time

    def getPositionList(self):
        return [(self.x1,self.y1),(self.x2,self.y2)]


    
