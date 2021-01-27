import cv2
import numpy as np
import os
import time
import datetime
from os.path import isfile, join
from Lot import Lot
from edge_detect import edge_detect

#Variables for mouse event (select/remove parking area)
click_x1 = 0
click_y1 = 0
click_x2 = 0
click_y2 = 0
startPoint = False
endPoint = False
    
      
#Function to handle mouse event (click)
def on_mouse(event,x,y,flags,params):
    global lots,click_x1,click_y1,click_x2,click_y2,startPoint,endPoint
    #get mouse click start slection
    if event == cv2.EVENT_LBUTTONDOWN:
        if startPoint == False:
            click_x1 = x
            click_y1 = y
            click_x2 = 0
            click_y2 = 0
            startPoint = True 
    #get mouse release and mark selection area (create parking object)
    elif(event == cv2.EVENT_LBUTTONUP):
        if startPoint == True and endPoint == False:
            click_x2 = x
            click_y2 = y
            startPoint = False
            endPoint = False
        
            #Prevent Dragging direcitions bug - to make it support dragging for all directions
            if(click_x1 < click_x2 and click_y1 < click_y2):
                #normal case
                pass
            elif(click_x2 > click_x1 and click_y1 > click_y2):
                #drag bottom left to top right
                click_y1, click_y2 = click_y2, click_y1
                
            elif(click_x1 > click_x2 and click_y2 > click_y1):
                click_x1, click_x2 = click_x2, click_x1
                
            elif(click_x2 < click_x1 and click_y2 < click_y1):
                click_x1, click_x2 = click_x2, click_x1
                click_y1, click_y2 = click_y2, click_y1

            #check size of input (not allow too small area)
            size = (click_x2 - click_x1) * (click_y2 - click_y1)
            if(size > 25):
                #create object lot and all to lots list
                lot_obj = Lot(click_x1,click_y1,click_x2,click_y2)
                lots.append(lot_obj)

    #get right mouse to remove parking area (remove lot object)
    elif(event == cv2.EVENT_RBUTTONUP):
        for lot in lots:
            lot_pos = lot.getPositionList()
            #check clicking point is in parking area or not? - if yes then remove
            if((x > lot_pos[0][0] and y > lot_pos[0][1]) and (x < lot_pos[1][0] and y < lot_pos[1][1])):
                lots.remove(lot)
                break
            
'''
lot is the region of interest (ROI)
The ROI is divided into FOUR quadrants (q1-q4)
Means of all quadrants are calculated (u1-u4)
Then find the distance betwee .n each quadrant and the entired lot (u0)
'''
#Set variable for video
#VIDEO =  'parkinglot.avi'
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(0) #for video streaming from main Web Cam
cap.set(cv2.CAP_PROP_FPS, 30)
currentFrame = 0
lots = []
lot_count = 1
start_time = time.time()
total = 0


#keep parking data (log)
logs = []

#time frame to fetch and check parking area
interleave = 10

#Start main loop - run video until terminate
while cap.isOpened():
    car = 0
    space = len(lots)
    ret, frame = cap.read()

    #avoid force terminate after reaching end of video
    if(frame is None):
        continue

    #set mouse event in loop
    cv2.setMouseCallback('Processed', on_mouse)

    if (currentFrame % interleave == 0):
        lot_count = 1
        for lot in lots:
            #mark lot label
            lot.setId(lot_count)
            lot_count += 1
            #mark position
            position = lot.getPositionList()
            p0, p1 = position
            x0,y0 = p0
            x1,y1 = p1
            rect = [(x0,y0),(x0,y1),(x1,y1),(x1,y0)]
            crop = frame[y0:y1, x0:x1]

            #Mark parking and set trigger to set log
            previous_status = lot.isParking
            if edge_detect(crop, 150):
                #check time span to avoid people walking by
                if(time.time() - lot.getTimeStamp() > 10):
                    lot.update(True,time.time())
            else:
                #check time span to avoid people walking by
                if(time.time() - lot.getTimeStamp() > 5):
                    lot.update(False,time.time())
                    
            if(previous_status != lot.isParking):
                log = ""
                if(lot.isParking):
                    log = "P" + str(lot.getId()) + " - is Unavailable at " + str(datetime.datetime.now())
                    total+=1
                    
                else:
                    log = "P" + str(lot.getId()) + " - is Available at " + str(datetime.datetime.now())
                logs.insert(0, log)

            #Draw Polylines around parking area(s)
            if(lot.isParking):
                cv2.putText(frame, "P" + str(lot.getId()) ,(x0, y0-2), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.polylines(frame, [np.int32(rect)], True, (0, 0, 255), thickness=2)
                car += 1
            else:
                cv2.putText(frame, "P" + str(lot.getId()) , (x0, y0-2),font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.polylines(frame, [np.int32(rect)], True, (0, 255, 0), thickness=2)
                
        #show monitor window
        monitor_panel = np.zeros((800,600,3), np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(monitor_panel, "Total parking area : " + str(space), (20, 40),font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(monitor_panel, "Unavailable lot(s) : " + str(car), (20, 80),font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(monitor_panel, "Available lot(s) : " + str(space-car), (20, 120),font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.line(monitor_panel, (0,160), (600,160), (255, 255, 255), 1)
        lot_count = 1

        
        #show real time monitoring data
        if(len(lots) == 0):
            cv2.imshow("Monitor", monitor_panel)
        for lot in lots:
            lot_count += 1
            if(lot.isParking):
                cv2.putText(monitor_panel, "P" + str(lot.getId()) + " - Unavailable",(20, 160 + (20 * lot_count)), font, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(monitor_panel, "P" + str(lot.getId()) + " - Available" , (20, 160 + (20 * lot_count)),font, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
                
        #show real time log 
        cv2.line(monitor_panel, (0,200 + (20 * len(lots))), (600,200 + (20 * len(lots))), (255, 255, 255), 1)
        log_count = 1
        for log in logs:
            log_count += 1
            if(log_count == 20):
                break
            cv2.putText(monitor_panel, log , (20, 200 + (20 * len(lots)) + (20 * log_count + 3)),font, 0.4, (255, 255, 255), 1, cv2.LINE_AA)


        #show title in infomation panel
        cv2.putText(monitor_panel, "Summary Infomation" , (400, 40) ,font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(monitor_panel, "Current Status of Lots" , (400, 180) ,font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(monitor_panel, "Status logs infomation" , (400, 220 + (20 * len(lots))) ,font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("Monitor", monitor_panel)
        
        # frame_array.append(frame)
        lot = cv2.Canny(frame,150,210)
        cv2.imshow("Processed", frame)
        cv2.imshow("Canny", lot)

        #define time to store data on Firebase
        a = datetime.datetime.now()
        if(a.second == 0):
         from firebase import firebase
         firebase = firebase.FirebaseApplication('https://carpark-database.firebaseio.com/')
         result = firebase.post('/Car Parking Database',{'Total Parking Area':space,'Available lots':(space-car),'DateTime':datetime.datetime.now(),'Total Car':total,'Unavailable lots':car})
         print(result)
         total = 0
    
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    #goto next frame with delay to test video dataset
    time.sleep(0.01)
    currentFrame += 1

cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()
