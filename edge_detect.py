import cv2
import numpy as np

def edge_detect(img,threshold):
     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     lot = cv2.Canny(gray,120,200)
     w, h= lot.shape
     wh, hh = int(w/2), int(h/2)
     wwh, hhh = int(wh/2) ,int(hh/2)
     wx, hx = int(wh + wwh), int(hh + hhh)
    #print(w, h, wh, hh)
     q11 = lot[0:wwh,0:hhh]
     q12 = lot[wwh: wh,0:hhh]
     q13 = lot[wh:wx, 0:hhh]
     q14 = lot[wx:w, 0:hhh]
     
     q21 = lot[0:wwh, hhh:hh]
     q22 = lot[wwh:wh,hhh:hh]
     q23 = lot[wh:wx, hhh:hh]
     q24 = lot[wx:w , hhh:hh]

     q31 = lot[0:wwh, hh:hx]
     q32 = lot[wwh:wh, hh:hx]
     q33 = lot[wh:wx, hh:hx]
     q34 = lot[wx:w , hh: hx]
 
     q41 = lot[0:wwh, hx:h]
     q42 = lot[wwh:wh, hx:h]
     q43 = lot[wh:wx, hx:h]
     q44 = lot[wx:w,hx:h]
 
     u0 = np.average(lot)
 
     u11 = np.average(q11)
     u12 = np.average(q12)
     u13 = np.average(q13)
     u14 = np.average(q14)

     u21 = np.average(q21)
     u22 = np.average(q22)
     u23 = np.average(q23)
     u24 = np.average(q24)
 
     u31 = np.average(q31)
     u32 = np.average(q32)
     u33 = np.average(q33)
     u34 = np.average(q34)

     u41 = np.average(q41)
     u42 = np.average(q42)
     u43 = np.average(q43)
     u44 = np.average(q44)
 
     sum_of_distance_first = abs(u0-u11) + abs(u0-u12) + abs(u0-u13) + abs(u0-u14)
     sum_of_distance_second = abs(u0-u21) + abs(u0-u22) + abs(u0-u23) + abs(u0-u24)
     avg1 = np.average(sum_of_distance_first + sum_of_distance_second)
     sum_of_distance_third = abs(u0-u31) + abs(u0-u32) + abs(u0-u33) + abs(u0-u34)
     sum_of_distance_four = abs(u0-u41) + abs(u0-u42) + abs(u0-u43) + abs(u0-u44)
     avg2 = np.average(sum_of_distance_third + sum_of_distance_four)

     sum_all = np.average(avg1 + avg2)
     print('check')
    #print(u11, u12, u13, u14)
    #print(u21, u22, u23, u24)
    # print('u0',u0)
     print('sum_of_distance', sum_all)
     print('threshold', threshold)
    #print("Threshold = %.2f, Sum Of Distance = %.2f"%(threshold,sum_of_distance))
     return (threshold < sum_all)
     
