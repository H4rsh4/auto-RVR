import cv2, imagezmq
import numpy as np
import time
from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

#future
# _host = '192.168.1.74'
# _port = 6666


image_hub = imagezmq.ImageHub()
stop_sign_classifier = "road-sign-cascades\Stop Signs\StopSign_HAAR\Stopsign_HAAR_19Stages.xml"
stop_sign_classifier = cv2.CascadeClassifier(stop_sign_classifier)

def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def detect_stop_sign(classifier, img, draw=False):
    img = np.array(img)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    stop_signs = classifier.detectMultiScale(gray, 1.02, 10)
    print(stop_signs)
    #if draw:
    for (x,y,w,h) in stop_signs:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    return img, False if stop_signs == () else True

def draw_lines(img,lines):
    try:
        for line in lines:
            coords = line[0]
            cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)
    except TypeError:
        print('No lines Found')

def draw_lanes(img, lines, color=[0, 255, 255], thickness=3):
    
    # if this fails, go with some default line
    try:

        # finds the maximum y value for a lane marker 
        # (since we cannot assume the horizon will always be at the same point.)

        ys = []  
        for i in lines:
            for ii in i:
                ys += [ii[1],ii[3]]
        min_y = min(ys)
        max_y = 600
        new_lines = []
        line_dict = {}

        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                m, b = lstsq(A, y_coords)[0]

                # Calculating our new, and improved, xs
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])

        final_lanes = {}

        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]
            
            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s)) 

        l1_x1, l1_y1, l1_x2, l1_y2 = average_lane(final_lanes[lane1_id])
        l2_x1, l2_y1, l2_x2, l2_y2 = average_lane(final_lanes[lane2_id])

        return [l1_x1, l1_y1, l1_x2, l1_y2], [l2_x1, l2_y1, l2_x2, l2_y2]
    except Exception as e:
        print(str(e))

def process_img(img):
    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    processed_img = cv2.GaussianBlur(processed_img,(5,5),0)
    vertices = np.array([[0,240],[0,160],[80,80],[240,80],[320,160],[320,240],
                         ], np.int32)
    processed_img = roi(processed_img, [vertices])


    # more info: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    #                          edges       rho   theta   thresh         # min length, max gap:        
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180,      20,         15)
    draw_lines(processed_img,lines)
    return processed_img

while True:
    rpi_name, image = image_hub.recv_image()
    image = np.rot90(image, 2)
    new_screen = process_img(image)
    image,stop_sign_presence = detect_stop_sign(stop_sign_classifier, image, draw=True)
    #print(f'Took this long : {round(time.time()-int(rpi_name))}')
    if stop_sign_presence:
            print("STOP!!!")
    else: print("GO!!!")
    cv2.imshow('stop', image)
    cv2.imshow('line', new_screen)
    if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    image_hub.send_reply(b'OK')