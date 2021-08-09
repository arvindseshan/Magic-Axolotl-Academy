import imutils
import cv2
import numpy as np
from cmu_112_graphics import *
from keras import models
from keras.models import load_model

from pickle import load

""" def mouseRGB(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        colorsB = frame[y,x,0]
        colorsG = frame[y,x,1]
        colorsR = frame[y,x,2]
        colors = frame[y,x]
        print("Red: ",colorsR)
        print("Green: ",colorsG)
        print("Blue: ",colorsB)
        print("BRG Format: ",colors)
        print("Coordinates of pixel: X: ",x,"Y: ",y) """

model = load_model("gestureRecognizer.h5")
scaler = load(open('scaler.pkl', 'rb'))


def whenTrackerbarChanged(value):
    pass

# Gets video from the camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Creates a window called frame to display frames of the video
cv2.namedWindow('vid')

# Create sliders for HSV min and max for adjusting to object color
cv2.createTrackbar('hMin', 'vid', 90, 179, whenTrackerbarChanged)
cv2.createTrackbar('hMax', 'vid', 162, 179, whenTrackerbarChanged)
cv2.createTrackbar('sMin', 'vid', 45, 255, whenTrackerbarChanged)
cv2.createTrackbar('sMax', 'vid', 251, 255, whenTrackerbarChanged)
cv2.createTrackbar('vMin', 'vid', 133, 255, whenTrackerbarChanged)
cv2.createTrackbar('vMax', 'vid', 255, 255, whenTrackerbarChanged)

#cv2.setMouseCallback('frame',mouseRGB)

def getCoodinates(app):       
    worked, vid = cap.read()
    if not worked:
        return
    # Convert from BGR to HSV color
    hsv = cv2.cvtColor(vid, cv2.COLOR_BGR2HSV)

    hMin = cv2.getTrackbarPos('hMin', 'vid')
    hMax = cv2.getTrackbarPos('hMax', 'vid')
    sMin = cv2.getTrackbarPos('sMin', 'vid')
    sMax = cv2.getTrackbarPos('sMax', 'vid')
    vMin = cv2.getTrackbarPos('vMin', 'vid')
    vMax = cv2.getTrackbarPos('vMax', 'vid')

    # Adjust the min and max color range based on the hsv sliders
    colorMin = np.array([hMin, sMin, vMin])
    colorMax = np.array([hMax, sMax, vMax])

    mask = cv2.inRange(hsv, colorMin, colorMax)

    #cv2.imshow('mask',mask)

    # Source: docs.opencv.org | https://docs.opencv.org/4.5.2/dd/d49/tutorial_py_contour_features.html
    #           https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts.sort(reverse=True, key=cv2.contourArea)
    for i in range(len(cnts)):
        cnt = cnts[i]
        if cv2.contourArea(cnt) > 5000:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                if i == 0:
                    app.cx = app.width - cx
                    app.cy = cy
                    color = (0, 0, 255)
                elif i == 1:
                    app.cx2 = app.width - cx
                    app.cy2 = cy
                    color = (0, 255, 0)
            cv2.circle(vid, (cx, cy), 10, color, -1)
            cv2.drawContours(vid, cnts, i, color, maxLevel=0)
  
            
    cv2.imshow("vid", vid)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        return

def appStarted(app):
    app.cx = -100
    app.cy = -100
    app.cx2 = -100
    app.cy2 = -100
    timerDelay = 0
    app.data = []
    app.record = False
    app.buttonActive = False
    app.color = "pink"
    app.paused = False

def keyPressed(app ,event):
    if event.key == 'f':
        app.record = not app.record
    if event.key == 'p':
        app.paused = not app.paused

def timerFired(app):
    getCoodinates(app)
    if app.paused:
        return
    if 0 < app.cx < 200 and 200 < app.cy < 400:
        app.data.append((app.cx2, app.cy2))
    elif 0 < app.cx2 < 200 and 200 < app.cy2 < 400:
        app.data.append((app.cx, app.cy))
    else:
        app.data = []
    if len(app.data) == 15:
        if app.record:
            gesture = "circle"
            file = open(f"{gesture}.txt", "a")
            for i in range(len(app.data)-1):
                x, y = app.data[i]
                x2, y2 = app.data[i+1]
                if (x2-x) == 0:
                    x2 += 0.1
                slope = (y2-y)/(x2-x)
                file.write(f"{slope},")
            file.write(gesture)
            file.write("\n")
            app.data = []
        else:
            X = [[]]
            for i in range(len(app.data)-1):
                x, y = app.data[i]
                x2, y2 = app.data[i+1]
                if (x2-x) == 0:
                    x2 += 0.1
                slope = (y2-y)/(x2-x)
                X[0].append(slope)
            X = scaler.transform(X)
            pred = model.predict(X)
            print(pred)
            if pred[0][0] > 0.8:
                print("horizontal")
                app.color = "blue"
            elif pred[0][1] > 0.8:
                print("vertical")
                app.color = "red"
            else:
                print("none")
                app.color = "pink"
            app.data = []
            #app.data.pop(0)

def drawTrail(app, canvas):
    for i in range(len(app.data)-1):
        x, y = app.data[i]
        x2, y2 = app.data[i+1]
        canvas.create_line(x, y, x2, y2)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 200, 200, 400, fill = app.color)
    canvas.create_oval(app.cx-10, app.cy-10, app.cx+10, app.cy+10)
    canvas.create_oval(app.cx2-10, app.cy2-10, app.cx2+10, app.cy2+10)
    drawTrail(app, canvas)
    canvas.create_text(app.width/2, 10, text = f"({app.cx}, {app.cy}) ({app.cx2}, {app.cy2})")
    #canvas.create_oval(app.cx, app.cy, app.cx2, app.cy2, fill = '', outline="black", width=5)
runApp(width=640, height=480)