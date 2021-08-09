import imutils
import cv2
import numpy as np
# Source: File from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
from cmu_112_graphics import *
from keras import models
from keras.models import load_model
from pickle import load
import random

def whenTrackerbarChanged(value):
    pass

# Gets video from the camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Creates a window called vid to display the video and slider bars defined below
cv2.namedWindow('vid')

# Inspiration for trackerbars: https://www.tutscode.net/2020/04/color-detection-with-python-and-opencv.html
# Create sliders for HSV min and max for adjusting to object color
cv2.createTrackbar('hMin', 'vid', 90, 179, whenTrackerbarChanged)
cv2.createTrackbar('hMax', 'vid', 162, 179, whenTrackerbarChanged)
cv2.createTrackbar('sMin', 'vid', 45, 255, whenTrackerbarChanged)
cv2.createTrackbar('sMax', 'vid', 251, 255, whenTrackerbarChanged)
cv2.createTrackbar('vMin', 'vid', 133, 255, whenTrackerbarChanged)
cv2.createTrackbar('vMax', 'vid', 255, 255, whenTrackerbarChanged)

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

    # Creates and displays a video feed that is filtered to the color range
    filteredVid = cv2.inRange(hsv, colorMin, colorMax)
    cv2.imshow('filteredVid',filteredVid)

    # Source for available openCV functions: docs.opencv.org | https://docs.opencv.org/4.5.2/dd/d49/tutorial_py_contour_features.html
    # Learned contour detection from https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
    # Gets contours
    cnts = cv2.findContours(filteredVid, cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts.sort(reverse=True, key=cv2.contourArea)
    for i in range(len(cnts)):
        cnt = cnts[i]
        if cv2.contourArea(cnt) > 5000:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                # Gets center of contour
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
            # plots center and contours on vid window
            cv2.circle(vid, (cx, cy), 10, color, -1)
            cv2.drawContours(vid, cnts, i, color, maxLevel=0)
  

    cv2.imshow("vid", vid)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        return

######################################################

# Enemy Class
class Enemy(object):
    colors = ["orange", "yellow", "gray"]
    gestures = ["horizontalLine", "verticalLine"]
    def __init__(self, health, speed, radius, x, y):
        self.health = health
        self.speed = speed
        self.radius = radius
        self.x = x
        self.y = y
        self.color = random.choice(Enemy.colors)
        self.gestures = []
        for i in range(health):
            gesture = random.choice(Enemy.gestures)
            self.gestures.append(gesture)
    def __repr__(self):
        return f"{self.color} enemy at ({self.x}, {self.y}) with {self.health} health and {self.speed} speed"
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def damageEnemy(self, damage):
        self.health -= damage
        for i in range(damage):
            self.gestures.pop(0)

# Player class
class Player(object):
    def __init__(self, health, radius, color, x, y):
        self.health = health
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
    def move(self, x, y):
        self.x = x
        self.y = y
    def damagePlayer(self, damage):
        self.health -= damage

# Returns distance between two points
def distance(x1, y1, x2, y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

# Moves the enemy away or towards the player and checks for collision
def moveEnemyInDir(app, enemy, dir):
    dx = (app.player.x - enemy.x)/(60-enemy.speed) * dir
    dy = (app.player.y - enemy.y)/(60-enemy.speed) * dir
    enemy.move(dx, dy)
    if distance(enemy.x, enemy.y, app.player.x, app.player.y) < enemy.radius + app.player.radius:
        app.enemies.remove(enemy)
        app.player.damagePlayer(1)
        app.curMotion = app.damagedMotion
        app.dmCounter = app.motionCounter
        if app.player.health <= 0:
            app.gameOver = True

# Creates a new Enemy object with randomized stats and start loc
def makeEnemy(app):
    if random.randint(0,1) == 0:
        x = random.randint(0, app.width)
        y = random.choice([0, app.height])
    else:
        x = random.choice([0, app.width])
        y = random.randint(0, app.height)
    health = random.randint(1, 4)
    speed = (5 - health)
    radius = health * 2.5 + 15
    app.enemies.append(Enemy(health, speed, radius, x, y))

# Initilizes game
def appStarted(app):
    app.gameOver = False
    # Hand locations
    app.cx = app.width/2
    app.cy = app.height/2
    app.cx2 = app.width/2
    app.cy2 = app.height/2
    timerDelay = 0
    #Sprites
    # Image Source: https://wallpapersafari.com/w/qofi3X
    app.background = app.loadImage("underwaterBackground.jpg")
    app.background = app.scaleImage(app.background, 0.625)
    # Image Source: https://spelunky.fyi/mods/m/axolotl-spelunker/
    axolotlSpriteSheet = app.loadImage("axolotlSprite.png")
    app.generalMotion = []
    for i in range(5):
        sprite = axolotlSpriteSheet.crop((130*i, 170, 130*(i+1), 260))
        app.generalMotion.append(sprite)
    app.damagedMotion = []
    for i in range(11):
        sprite = axolotlSpriteSheet.crop((128*i, 520, 128*(i+1), 650))
        app.damagedMotion.append(sprite)
    # Image Source: https://www.pngjoy.com/preview/c9y7j3g3j2h7h0_sprite-2d-sprite-sheet-png-png-download/
    smogSpriteSheet = app.loadImage("smogSprite.png")
    app.smogMotion = []
    for j in range(2):
        for i in range(8):
            sprite = smogSpriteSheet.crop((128*i, 120*j, 128*(i+1), 120*(j+1)))
            app.smogMotion.append(sprite)
    app.motionCounter = 0
    app.dmCounter = 0
    app.smCounter = 0
    app.curMotion = app.generalMotion
    app.data = []
    app.record = False
    app.buttonActive = False
    app.color = "pink"
    app.paused = False
    app.timer  = 0
    app.enemies = []
    app.player = Player(5, 45, "brown", app.width/2, app.height/2)
    # Model and scaler for gesture recognition
    # Source for loading model: https://keras.io/api/models/model_saving_apis/#save_model-function
    app.model = load_model("gestureRecognizer.h5")
    # Source for loading scaler: https://machinelearningmastery.com/how-to-save-and-load-models-and-data-preparation-in-scikit-learn-for-later-use/
    app.scaler = load(open('scaler.pkl', 'rb'))

# Records data from training when f key pressed
# Pauses game with p and steps with s for debugging
def keyPressed(app ,event):
    if event.key == 'f':
        app.record = not app.record
    if event.key == 'p':
        app.paused = not app.paused
    if app.paused and not app.gameOver and event.key == 's':
        doStep(app)

# Creates list of slopes in hand pos list and inputs into model to predict gesture
# Decides action based on gesture prediction
def predictGesture(app):
    X = [[]]
    for i in range(len(app.data)-1):
        x, y = app.data[i]
        x2, y2 = app.data[i+1]
        if (x2-x) == 0:
            x2 += 0.1
        slope = (y2-y)/(x2-x)
        X[0].append(slope)
    X = app.scaler.transform(X)
    pred = app.model.predict(X)
    print(pred)
    if pred[0][0] > 0.8:
        gesture = "horizontalLine"
        print("horizontalLine")
        app.color = "blue"
    elif pred[0][1] > 0.8:
        gesture = "verticalLine"
        print("verticalLine")
        app.color = "red"
    else:
        gesture = "none"
        print("none")
        app.color = "pink"
    for enemy in app.enemies:
        if enemy.gestures[0] == gesture:
            enemy.damageEnemy(1)
            if enemy.health <= 0:
                app.enemies.remove(enemy)
            else:
                for i in range(random.randint(2, 6)):
                    moveEnemyInDir(app, enemy, -1)

# Creates list of slopes in hand pos list and saves
# to line in txt file with the gesture name
def recordData(app, gesture):
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

# Perform a step of the game to move enemies, make enemies,
# update animation counters, keep track of hand locations,
# and perfrom gesture recognition
def doStep(app):
    app.motionCounter = (1 + app.motionCounter)
    app.smCounter = (1 + app.smCounter)
    if not app.record:
        for enemy in app.enemies:
            moveEnemyInDir(app, enemy, 1)
        if app.timer % 40 == 0:
            makeEnemy(app)
        if app.curMotion == app.damagedMotion and app.motionCounter - app.dmCounter == len(app.damagedMotion)-1:
            app.curMotion = app.generalMotion
    getCoodinates(app)
    if app.width-300 < app.cx < app.width and 0 < app.cy < app.height:
        app.data.append((app.cx, app.cy))
        app.player.move(app.cx2, app.cy2)
    elif app.width-300 < app.cx2 < app.width and 0 < app.cy2 < app.height:
        app.data.append((app.cx2, app.cy2))
        app.player.move(app.cx, app.cy)
    else:
        app.player.move(app.cx2, app.cy2)
        app.data = []
    if len(app.data) == 15:
        if app.record:
            recordData(app, "circle")
        else:
            x1, y1 = app.data[-1]
            x2, y2 = app.data[-2]
            if distance(x1, y1, x2, y2) < 5:
                predictGesture(app)
                app.data = []
            else:
                app.data.pop(0)
    app.timer += 1

# Perform step of the game when timer is fired
def timerFired(app):
    if app.paused or app.gameOver:
        return
    doStep(app)

# Draws a trail behind the hand cursor by connecting lines between previous hand locs
def drawTrail(app, canvas):
    for i in range(len(app.data)-1):
        x, y = app.data[i]
        x2, y2 = app.data[i+1]
        canvas.create_line(x, y, x2, y2, width = 5, fill = "orange")

# Draws all of the enemies (smog monsters)
def drawEnemies(app, canvas):
    for enemy in app.enemies:
        sprite = app.smogMotion[app.smCounter % len(app.smogMotion)]
        sprite = app.scaleImage(sprite, enemy.radius*0.017)
        if enemy.x > app.width/2:
            sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
        #canvas.create_oval(enemy.x-enemy.radius, enemy.y-enemy.radius, enemy.x+enemy.radius, enemy.y+enemy.radius, fill = enemy.color)
        canvas.create_image(enemy.x, enemy.y, image=ImageTk.PhotoImage(sprite))
        #canvas.create_text(enemy.x, enemy.y, text = str(enemy.health))
        gesturesString = ""
        for gesture in enemy.gestures:
            #gesturesString += gesture[0]
            if gesture == "horizontalLine":
                gesturesString += "— "
            elif gesture == "verticalLine":
                gesturesString += "| "
        gesturesString = gesturesString[:-1]
        canvas.create_text(enemy.x, enemy.y-enemy.radius-15, text = gesturesString, fill = "orange", font = "Arial 16 bold")

# Draws the player (axolotl)
def drawPlayer(app, canvas):
    sprite = app.curMotion[app.motionCounter % len(app.curMotion)]
    #canvas.create_oval(app.player.x-app.player.radius, app.player.y-app.player.radius, app.player.x+app.player.radius, app.player.y+app.player.radius, fill = app.player.color)
    canvas.create_image(app.player.x-5, app.player.y, image=ImageTk.PhotoImage(sprite))
    canvas.create_text(app.player.x, app.player.y-app.player.radius-10, text = str(app.player.health))

# Redraws all
def redrawAll(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.background))
    #canvas.create_rectangle(app.width-200, 0, app.width, app.height, fill = app.color)
    canvas.create_oval(app.cx-10, app.cy-10, app.cx+10, app.cy+10)
    canvas.create_oval(app.cx2-10, app.cy2-10, app.cx2+10, app.cy2+10)
    drawPlayer(app, canvas)
    drawEnemies(app, canvas)
    drawTrail(app, canvas)
    canvas.create_text(app.width/2, 10, text = f"({app.cx}, {app.cy}) ({app.cx2}, {app.cy2})")
    if app.gameOver:
        canvas.create_text(app.width/2, app.height/2, text = "Game Over", font = "Arial 30 bold")
    #canvas.create_oval(app.cx, app.cy, app.cx2, app.cy2, fill = '', outline="black", width=5)
runApp(width=640, height=480)