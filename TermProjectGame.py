# Game inspired by https://www.google.com/doodles/halloween-2020
import imutils
import cv2
import numpy as np
# Source: File from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
from cmu_112_graphics import *
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from pickle import load
import random
import time

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
    
    #hMin = 90
    #hMax = 162
    #sMin = 45
    #sMax = 251
    #vMin = 133
    #vMax = 255

    # Adjust the min and max color range based on the hsv values
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
                    app.cx = app.width - cx*2.9375
                    app.cy = cy*2
                    color = (0, 0, 255)
                elif i == 1:
                    app.cx2 = app.width - cx*2.9375
                    app.cy2 = cy*2
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
    gestures = ["—", "|", "u", "n"]
    def __init__(self, health, speed, radius, x, y, heart, direction):
        self.health = health
        self.speed = speed
        self.radius = radius
        self.x = x
        self.y = y
        self.direction = direction
        self.color = random.choice(Enemy.colors)
        self.gestures = []
        if heart:
            self.gestures = ["♥"]
            self.health = 1
        else:
            for i in range(health):
                gesture = random.choice(Enemy.gestures)
                self.gestures.append(gesture)
            if random.randint(0, 4) == 1:
                self.gestures[0] = "⚡"
    def __repr__(self):
        return f"{self.color} enemy at ({self.x}, {self.y}) with {self.health} health and {self.speed} speed"
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def damageEnemy(self, damage):
        self.health -= damage
        for i in range(damage):
            self.gestures.pop(0)
    def dir(self, dir):
        self.direction = dir

# Player class
class Player(object):
    def __init__(self, health, radius, color, x, y, direction):
        self.health = health
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        self.direction = direction
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def teleport(self, x, y):
        self.x = x
        self.y = y
    def damagePlayer(self, damage):
        self.health -= damage
    def healPlayer(self, health):
        self.health += health
    def dir(self, dir):
        self.direction = dir

# Returns distance between two points
def distance(x1, y1, x2, y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5


# Source: Pseudocode for BFS algorithm from 15-112 Graphs/AI lesson slides
# Finds shortest path between two cells
def findShortestPath(app, startRow, startCol, endRow, endCol, rows, cols, walls, dists):
    found = False
    cellMap = {}
    visitedCells = set()
    unvisitedNeighborsQueue = [(startRow, startCol)]
    cellDistance = [[0]*app.cols for i in range(app.rows)]
    cellDistance[startRow][startCol] = -99
    found = False
    foundDist = 0
    while len(unvisitedNeighborsQueue) != 0:
        row, col = unvisitedNeighborsQueue[0]
        unvisitedNeighborsQueue.pop(0)
        visitedCells.add((row, col))
        if row == endRow and col == endCol:
            found = True
            foundDist = cellDistance[row][col]
        if found and cellDistance[row][col] - foundDist == 8:
            break
        for dCol, dRow in [(-1, 0),(0, 1),(1, 0),(0, -1),(-1, -1),(1, 1),(-1, 1),(1, -1)]:
            newRow = row - dRow
            newCol = col - dCol
            if 0 <= newRow < rows and 0 <= newCol < cols and (newRow, newCol) not in visitedCells and (newRow, newCol) not in unvisitedNeighborsQueue and not walls[newRow][newCol]:
                if dists:
                    if cellDistance[row][col] == -89:
                        cellDistance[newRow][newCol] = cellDistance[row][col] + 101
                    else:
                        cellDistance[newRow][newCol] = cellDistance[row][col] + 1
                    app.cellDistances[newRow][newCol] += cellDistance[newRow][newCol]
                unvisitedNeighborsQueue.append((newRow, newCol))
                if not found:
                    cellMap[(newRow, newCol)] = cellMap.get((newRow, newCol), (row, col))
    if found:
        result = (endRow, endCol)
        path = []
        while result != (startRow, startCol):
            path.append(result)
            result = cellMap[result]
        path.append((startRow, startCol))
        path.reverse()
        return path
    else:
        return []

# Get the cell at a given x,y coord
def getCell(app, x, y):
    cellWidth = (app.width-app.spellSize) / app.cols
    cellHeight = (app.height) / app.rows
    row = int(y // cellHeight)
    col = int(x // cellWidth)
    return row, col

# Gets the top left and bottom right coords for a cell
def getCellBounds(app, row, col):
    cellWidth = (app.width-app.spellSize) / app.cols
    cellHeight = app.height / app.rows
    x1 = col * cellWidth
    x2 = x1 + cellWidth
    y1 = row * cellHeight
    y2 = y1 + cellHeight
    return x1, y1, x2, y2

# Returns the shortest path around walls to the player from an x,y coord
def shortestPathToPlayer(app, x, y):
    startRow, startCol = getCell(app, x, y)
    endRow, endCol = getCell(app, app.player.x, app.player.y)
    return findShortestPath(app, startRow, startCol, endRow, endCol, app.rows, app.cols, app.walls, True)

# Moves the enemy away or towards the player and checks for collision
def moveEnemy(app, enemy):
    cellWidth = (app.width-app.spellSize) / app.cols
    cellHeight = app.height / app.rows
    path = shortestPathToPlayer(app, enemy.x, enemy.y)
    app.enemiesPath += path
    if len(path) > 1:
        row1, col1 = path[0]
        row2, col2 = path[1]
        dy = (row2 - row1) * cellWidth * enemy.speed/7
        dx = (col2 - col1) * cellHeight* enemy.speed/7
        enemy.move(dx, dy)
        if dx > 0:
            enemy.dir(1)
        else:
            enemy.dir(-1)
        if distance(enemy.x, enemy.y, app.player.x, app.player.y) < enemy.radius + app.player.radius:
            app.enemies.remove(enemy)
            app.player.damagePlayer(1)
            app.score -= 100
            app.curMotion = app.damagedMotion
            app.dmCounter = app.motionCounter
            if app.player.health <= 0:
                app.gameOver = True

# Moves the player towards hand, avoiding walls
# In auto mode, moves away from enemies while maintaining line of sight
def movePlayer(app, x, y):
    cellWidth = (app.width-app.spellSize) / app.cols
    cellHeight = app.height / app.rows
    startRow, startCol = getCell(app, app.player.x, app.player.y)
    if app.autoMode:
        #if app.curMoveRow == startRow and app.curMoveCol == startCol:
        maxDist = -1
        maxRow = -1
        maxCol = -1
        for dRow in range(-10, 11, 2):
            for dCol in range(-10, 11, 2):
                #if dRow == 0 and dCol == 0:
                #    continue
                totalDist = 0
                endRow = startRow + dRow
                endCol = startCol + dCol
                if not 2 <= endRow < app.rows - 2 or not 2 <= endCol < app.cols - 2 or app.walls[endRow][endCol]:
                    continue
                for enemy in app.enemies:
                    cy = app.player.y + dRow*cellHeight
                    cx = app.player.x + dCol*cellWidth
                    if isThroughWall(app, cx, cy, enemy.x, enemy.y) == (-1, -1) and app.cellDistances[endRow][endCol] > 0:
                        app.cellDistances[endRow][endCol] *= 2
                totalDist += app.cellDistances[endRow][endCol]
                if totalDist > maxDist:
                    maxDist = totalDist
                    maxRow = endRow
                    maxCol = endCol
        app.curMoveRow = maxRow
        app.curMoveCol = maxCol
        path = findShortestPath(app, startRow, startCol, app.curMoveRow, app.curMoveCol, app.rows, app.cols, app.walls, False)
    else:
        endRow, endCol = getCell(app, x, y)
        path = findShortestPath(app, startRow, startCol, endRow, endCol, app.rows, app.cols, app.walls, False)
    app.playerPath += path
    if len(path) > 1:
        row1, col1 = path[0]
        row2, col2 = path[1]
        dy = (row2 - row1) * cellHeight
        dx = (col2 - col1) * cellWidth
        if dx >= 0:
            app.player.dir(1)
        else:
            app.player.dir(-1)
        app.player.move(dx, dy)

# Creates a new Enemy object with randomized stats and start loc
def makeEnemy(app):
    if random.randint(0,1) == 0:
        x = random.randint(10, app.width-app.spellSize-10)
        y = random.choice([10, app.height-10])
    else:
        x = random.choice([10, app.width-app.spellSize-10])
        y = random.randint(10, app.height-10)
    if x > (app.width-app.spellSize)/2:
        dir = 1
    else:
        dir = 0
    level = app.timer // 200 + 3
    health = random.randint(1, min(10, level))
    speed = (min(10, level) - health + 1)
    radius = min(health * 2.5 + 15, 30)
    app.enemies.append(Enemy(health, speed, radius, x, y, random.randint(app.player.health, 8) < 5, dir))

# Counts number of neighboring cells with walls
def countNeighbors(app, row, col):
    neighbors = 0
    for dRow in [-1, 0, 1]:
        for dCol in [-1, 0, 1]:
            newRow = row + dRow
            newCol = col + dCol
            if 0 <= newRow < app.rows and 0 <= newCol < app.cols and app.walls[newRow][newCol]:
                neighbors += 1
    neighbors -= 1
    return neighbors

# Source: Concept (description) for random cave generation from http://pixelenvy.ca/wa/ca_cave.html (4-5 rule) modified for wall generation
# Makes natural looking walls with cellular automata model
def makeWalls(app, empty, passes):
    app.walls = [[False]*app.cols for i in range(app.rows)]
    for row in range(3, app.rows-3):
        for col in range(3, app.cols-3):
            if random.randint(1, 100) >= empty:
                app.walls[row][col] = True
    for i in range(passes):
        newWalls = [[None]*app.cols for i in range(app.rows)]
        for row in range(app.rows):
            for col in range(app.cols):
                if app.walls[row][col] and countNeighbors(app, row, col) <= 3:
                    newWalls[row][col] = False
                elif countNeighbors(app, row, col) > 5:
                    newWalls[row][col] = True
                else:
                    newWalls[row][col] = app.walls[row][col]
        app.walls = newWalls

# Initilizes game
def appStarted(app):
    app.rows = 45
    app.cols = 60
    app.autoMode = False
    app.testingMode = False
    app.enemiesPath = []
    app.playerPath = []
    app.gestureToTrain = "—"
    app.score = 0
    app.spellSize = 600
    app.spellColor = {"—":"DeepPink2", "|":"cyan", "u":"spring green", "n":"magenta3", "none":"pink", "⚡":"yellow", "♥":"red"}
    makeWalls(app,45, 20)
    app.countdown = False
    app.gameStarted = False
    app.gameOver = False
    # Hand locations
    app.cx = app.width/2 - app.spellSize/2
    app.cy = app.height/2
    app.cx2 = app.width/2 - app.spellSize/2
    app.cy2 = app.height/2
    timerDelay = 0
    # Sprites and images
    # Image Source: https://wallpapersafari.com/w/qofi3X
    app.background = app.loadImage("underwaterBackground.jpg")
    app.background = app.scaleImage(app.background, 1.25)
    # Image credits: canva.com
    app.cover = app.loadImage("cover.png")
    # Image Source: https://spelunky.fyi/mods/m/axolotl-spelunker/
    axolotlSpriteSheet = app.loadImage("axolotlSprite.png")
    app.deadAxolotl = axolotlSpriteSheet.crop((1150, 0, 1290, 150))
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
    # Image Source: https://www.seekpng.com/ipng/u2q8q8i1u2t4q8i1_animation-sprite-electric-blue-lightning-game-lightning-animation/
    lightningSpriteSheet = app.loadImage("lightningSprite.png")
    app.lightningMotion = []
    app.lightningMotion.append(lightningSpriteSheet.crop((15, 0, 335, 675)))
    app.lightningMotion.append(lightningSpriteSheet.crop((745, 0, 1010, 675)))
    app.lightningMotion.append(lightningSpriteSheet.crop((15, 695, 335, 1370)))
    app.lightningMotion.append(lightningSpriteSheet.crop((745, 695, 1010, 1370)))
    resized = []
    for image in app.lightningMotion:
        resized.append(app.scaleImage(image, 0.2))
    app.lightningMotion = resized
    app.lightning = False
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
    app.addWalls = False
    app.player = Player(5, 45, "brown",(app.width-app.spellSize)/2, app.height/2, 1)
    app.cellDistances = [[-1]*app.cols for i in range(app.rows)]
    while shortestPathToPlayer(app, 0, 0) == []:
        app.player = Player(5, 45, "brown", random.randint(0, app.width-app.spellSize), random.randint(0, app.height), 1)
    # Model and scaler for gesture recognition
    # Source for loading model: https://keras.io/api/models/model_saving_apis/#save_model-function
    app.model = load_model("gestureRecognizer.h5")
    # Source for loading scaler: https://machinelearningmastery.com/how-to-save-and-load-models-and-data-preparation-in-scikit-learn-for-later-use/
    app.scaler = load(open('scaler.pkl', 'rb'))

# Records data for training when f key pressed
# Pauses game with p and steps with s for debugging
def keyPressed(app ,event):
    if event.key == 'r':
        appStarted(app)
    if event.key == 's':
        if app.gameStarted and app.paused and not app.gameOver:
            doGameStep(app)
        elif not app.gameStarted and not app.gameOver:
            app.countdown = True
            app.time = time.time()
    elif event.key == 'f':
        app.record = not app.record
    elif not app.gameStarted or app.gameOver:
        return
    elif event.key == 'p':
        app.paused = not app.paused
    elif event.key == 'w':
        app.addWalls = not app.addWalls
    elif event.key == 't':
        app.testingMode = not app.testingMode
    elif event.key == 'a':
        app.autoMode = not app.autoMode
        app.curMoveRow, app.curMoveCol = getCell(app, app.player.x, app.player.y)

# Temp function to manually add walls to the game for testing
def mousePressed(app, event):
    (row, col) = getCell(app, event.x, event.y)
    if app.addWalls:
     app.walls[row][col] = not app.walls[row][col]

# Creates list of slopes in hand pos list and inputs into model to predict gesture
# Decides action based on gesture prediction
def predictGesture(app):
    X = [[]]
    numPoints = (len(app.data)-1) * 8
    newPoints = [app.data[0]]
    startX, startY = app.data[0]
    for i in range(len(app.data)-1):
        x, y = app.data[i]
        x2, y2 = app.data[i+1]
        if (x2-x) == 0:
            x2 += 0.1
        slope = (y2-y)/(x2-x)
        
        midPoints = int(numPoints/(len(app.data)-1))
        for j in range(midPoints):
            dx = ((x2-x)/midPoints)*j
            dy = (dx*slope)*j
            newPoints.append((int(x+dx), int(y+dy)))
    for i in range(numPoints+1):
        valX, valY = newPoints[i]
        if i % (numPoints/8) == 0:
            X[0].append(valX-int(startX))
            X[0].append(valY-int(startY))
    X = app.scaler.transform(X)
    pred = app.model.predict(X)
    if pred[0][4] > 0.8:
        gesture = "—"
        print("—")
    elif pred[0][3] > 0.8:
        gesture = "|"
        print("|")
    elif pred[0][2] > 0.8:
        gesture = "u"
        print("u")
    elif pred[0][0] > 0.8:
        gesture = "n"
        print("n")
    elif pred[0][1] > 0.8:
        gesture = "none"
        print("none1")
    elif pred[0][6] > 0.8:
        gesture = "⚡"
        print("⚡")
    elif pred[0][5] > 0.8:
        gesture = "♥"
        print("♥")
    else:
        gesture = "none"
        print("none2")
    app.color = app.spellColor[gesture]
    return gesture

# Function for testing line of sight
def isThroughWall(app, x1, y1, x2, y2):
    dx = int(x2-x1)
    dy = int(y2-y1)
    if dx == 0:
        dx += 1
    if dy == 0:
        dy += 1
    slope = dy/dx
    for x in range(0, dx, int(abs(dx)/dx)):
        y = x*slope + y1
        row, col = getCell(app, x+x1, y)
        if 0 <= row < app.rows and 0 <= col < app.cols and app.walls[row][col]:
            return x+x1, y
    for y in range(0, dy, int(abs(dy)/dy)):
        x = y*(1/slope) + x1
        row, col = getCell(app, x, y+y1)
        if 0 <= row < app.rows and 0 <= col < app.cols and app.walls[row][col]:
            return x, y+y1
    return -1, -1

# Makes enemies take damage, heals player, or starts game based on the gesture
def performSpells(app, gesture):
    app.lightning = False
    if not app.countdown and not app.gameStarted and gesture == "⚡":
        app.countdown = True
        app.time = time.time()
    for enemy in app.enemies:
        if enemy.gestures[0] == gesture and gesture == "⚡":
            app.score += 50
            app.lightning = True
            app.smCounter = 0
    for enemy in app.enemies:
        if enemy.gestures[0] == gesture or app.lightning:
            if gesture == "♥":
                app.player.healPlayer(1)
            if gesture != "⚡" and isThroughWall(app, app.player.x, app.player.y, enemy.x, enemy.y) != (-1, -1):
                continue
            enemy.damageEnemy(1)
            app.score += 50
            if enemy.health <= 0:
                app.enemies.remove(enemy)
                app.score += 100

# Creates scaled list of coords from hand pos list and saves
# to line in txt file with the gesture name
def recordData(app, gesture):
    file = open(f"{gesture}.txt", "a")
    numPoints = (len(app.data)-1) * 8
    newPoints = [app.data[0]]
    startX, startY = app.data[0]
    for i in range(len(app.data)-1):
        x, y = app.data[i]
        x2, y2 = app.data[i+1]
        if (x2-x) == 0:
            x2 += 0.1
        slope = (y2-y)/(x2-x)
        
        midPoints = int(numPoints/(len(app.data)-1))
        for j in range(midPoints):
            dx = ((x2-x)/midPoints)*j
            dy = (dx*slope)*j
            newPoints.append((int(x+dx), int(y+dy)))
    for i in range(numPoints+1):
        valX, valY = newPoints[i]
        if i % (numPoints/8) == 0:
            file.write(f"{valX-int(startX)},{valY-int(startY)},")
    file.write(gesture)
    file.write("\n")
    app.data = [] 

# Perform a step of the game to move enemies, make enemies,
# update animation counters, keep track of hand locations,
# and perfrom gesture recognition
def doGameStep(app):
    app.motionCounter += 1
    app.smCounter += 1
    if not app.record:
        app.enemiesPath = []
        app.cellDistances = [[-1]*app.cols for i in range(app.rows)]
        for enemy in app.enemies:
            moveEnemy(app, enemy)
        if app.timer % 40 == 0:
            makeEnemy(app)
        if app.curMotion == app.damagedMotion and app.motionCounter - app.dmCounter == len(app.damagedMotion)-1:
            app.curMotion = app.generalMotion
        if app.lightning and app.smCounter >= 4:
            app.lightning = False
    getCoodinates(app)
    app.playerPath = []
    if app.width-app.spellSize < app.cx < app.width and 0 < app.cy < app.height:
        app.data.append((app.cx, app.cy))
        if 0 < app.player.x <= app.width - app.spellSize and 0 < app.player.y <= app.height:
            movePlayer(app, app.cx2, app.cy2)
        else:
            app.player.teleport(app.cx2, app.cy2)
    elif app.width-app.spellSize < app.cx2 < app.width and 0 < app.cy2 < app.height:
        app.data.append((app.cx2, app.cy2))
        if 0 < app.player.x <= app.width - app.spellSize and 0 < app.player.y <= app.height:
            movePlayer(app, app.cx, app.cy)
        else:
            app.player.teleport(app.cx, app.cy)
    else:
        if 0 < app.player.x <= app.width - app.spellSize and 0 < app.player.y <= app.height:
            movePlayer(app, app.cx2, app.cy2)
        else:
            app.player.teleport(app.cx2, app.cy2)
        app.data = []
    if len(app.data) >= 5: 
        x1, y1 = app.data[-1]
        x2, y2 = app.data[-2]
        if distance(x1, y1, x2, y2) < 5:
            if app.record:
                recordData(app, app.gestureToTrain)
            else:
                gesture = predictGesture(app)
                performSpells(app, gesture)
                app.data = []
    elif len(app.data) >= 20:
        app.data = []
    elif len(app.data) == 2:
        x1, y1 = app.data[0]
        x2, y2 = app.data[1]
        if distance(x1, y1, x2, y2) < 10:
            app.data = []

    app.timer += 1

# Perform a step of the main menu to keep track of hand locations, and perfrom
# gesture recognition to see if the game has started/collect data for training
def doMenuStep(app):
    getCoodinates(app)
    if app.width-app.spellSize < app.cx < app.width and 0 < app.cy < app.height:
        app.data.append((app.cx, app.cy))
    elif app.width-app.spellSize < app.cx2 < app.width and 0 < app.cy2 < app.height:
        app.data.append((app.cx2, app.cy2))
    else:
        app.data = []
    if len(app.data) >= 5: 
        x1, y1 = app.data[-1]
        x2, y2 = app.data[-2]
        if distance(x1, y1, x2, y2) < 5:
            if app.record:
                recordData(app, app.gestureToTrain)
            else:
                gesture = predictGesture(app)
                performSpells(app, gesture)
                app.data = []
    elif len(app.data) >= 20:
        app.data = []
    elif len(app.data) == 2:
        x1, y1 = app.data[0]
        x2, y2 = app.data[1]
        if distance(x1, y1, x2, y2) < 10:
            app.data = []

# Perform step of the game when timer is fired
def timerFired(app):
    if app.paused or app.gameOver:
        return
    if app.countdown and time.time()-app.time >= 4:
        app.countdown = False
        app.gameStarted = True
    elif app.gameStarted:
        doGameStep(app)
    else:
        doMenuStep(app)

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
        if enemy.direction == -1:
            sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
        #canvas.create_oval(enemy.x-enemy.radius, enemy.y-enemy.radius, enemy.x+enemy.radius, enemy.y+enemy.radius, fill = enemy.color)
        canvas.create_image(enemy.x, enemy.y, image=ImageTk.PhotoImage(sprite))
        #canvas.create_text(enemy.x, enemy.y, text = str(enemy.health))
        gesturesString = ""
        for gesture in enemy.gestures:
            gesturesString += gesture[0] + " "
        gesturesString = gesturesString[:-1]
        canvas.create_text(enemy.x, enemy.y-enemy.radius-15, text = gesturesString, fill = app.spellColor[gesturesString[0]], font = "Arial 20 bold")
        if app.lightning:
            sprite = app.lightningMotion[app.smCounter % len(app.lightningMotion)]
            canvas.create_image(enemy.x, enemy.y-75, image=ImageTk.PhotoImage(sprite))
        if app.testingMode:
            blockingX, blockingY = isThroughWall(app, app.player.x, app.player.y, enemy.x, enemy.y)
            if blockingX == -1 and blockingY == -1:
                canvas.create_line(app.player.x, app.player.y, enemy.x, enemy.y, fill = "green", width = 4)
            else:
                canvas.create_line(app.player.x, app.player.y, blockingX, blockingY, fill = "red", width = 4)
                canvas.create_line(blockingX, blockingY, enemy.x, enemy.y, fill = "red", width = 1)
                canvas.create_oval(blockingX - 10, blockingY - 10, blockingX + 10, blockingY + 10, fill = "red")

# Draws the player (axolotl)
def drawPlayer(app, canvas):
    if app.gameOver:
        sprite = app.deadAxolotl
    else:
        sprite = app.curMotion[app.motionCounter % len(app.curMotion)]
    if app.player.direction == -1:
            sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
    #canvas.create_oval(app.player.x-app.player.radius, app.player.y-app.player.radius, app.player.x+app.player.radius, app.player.y+app.player.radius, fill = "")#app.player.color)
    canvas.create_image(app.player.x-5, app.player.y, image=ImageTk.PhotoImage(sprite))

# Draws the main menu
def drawCover(app, canvas):
    canvas.create_image((app.width-app.spellSize)/2, app.height/2, image=ImageTk.PhotoImage(app.cover))
    canvas.create_text((app.width-app.spellSize)/2, 10, text = "Magic Axolotl Academy", anchor = "n", font = "Arial 40 bold")
    howToPlay = """
——————————————————————————
Left hand to move axolotl or press a to move automatically
Right hand to cast spells (—, |, u, n, ⚡, and ♥)
Lighting damages all smog monsters in view
Casting a heart earns a life
To start playing the game, cast a lightning bolt
Press p to pause the game
Press s to step when paused
Press t for testing mode
Press r to restart the game
"""
    howToPlay = howToPlay.splitlines()   
    canvas.create_text((app.width-app.spellSize)/2, 95, text = "How To Play", anchor = "n", font = "Arial 16 bold")       
    for i in range(len(howToPlay)):
        canvas.create_text((app.width-app.spellSize)/2, 105+i*25, text = howToPlay[i], anchor = "n", font = "Arial 14")

# Draws the score and health
def drawGameInfo(app, canvas):
    canvas.create_text(10, 10, anchor = "nw", text = f"Score: {max(0, app.score)}", fill = "orange", font = "Arial 20 bold")
    canvas.create_text(app.width-app.spellSize-10, 10, anchor = "ne", text = "♥ "*app.player.health, fill = "red", font = "Arial 20 bold")
    #canvas.create_text(app.width/2, 10, text = f"({app.cx}, {app.cy}) ({app.cx2}, {app.cy2})")

# Draws the cells/walls in the game
def drawCells(app, canvas):
    for row in range(app.rows):
            for col in range(app.cols):
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                fill = ""
                if app.testingMode:
                    if (row, col) in app.enemiesPath:
                        fill = "orange"
                    elif (row, col) in app.playerPath:
                        fill = "blue"
                if app.walls[row][col]:
                    fill = "black"
                if app.testingMode:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=fill)
                    if fill != "black":
                        canvas.create_text((x1-x0)/2+x0, (y1-y0)/2+y0, text = str(app.cellDistances[row][col]), font = "Arial 8")
                else:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline = "")

# Draws the game starting countdown
def drawCountdown(app, canvas):
    if app.countdown:
        if int(4 - (time.time()-app.time)) == 0:
            canvas.create_text((app.width-app.spellSize)/2, app.height/2, text = "Cast!", fill = "orange", font = "Arial 60 bold")
        else:
            canvas.create_text((app.width-app.spellSize)/2, app.height/2, text = str(int(4 - (time.time()-app.time))), fill = "orange", font = "Arial 60 bold")

# Draws the area to cast spells
def drawSpellZone(app, canvas):
    canvas.create_rectangle(app.width-app.spellSize, 0, app.width, app.height, fill = app.color)
    canvas.create_text(app.width-app.spellSize/2, 10, anchor = "n", text = f"Cast Your Spells Here", fill = "black", font = "Arial 20 bold")

# Draws the cursor for each hand
def drawHands(app, canvas):
    canvas.create_oval(app.cx-10, app.cy-10, app.cx+10, app.cy+10, outline = "orange", width = 3)
    canvas.create_oval(app.cx2-10, app.cy2-10, app.cx2+10, app.cy2+10, outline = "orange", width = 3)

# Redraws all
def redrawAll(app, canvas):
    canvas.create_image((app.width-app.spellSize)/2, app.height/2, image=ImageTk.PhotoImage(app.background))
    drawSpellZone(app, canvas)
    drawHands(app, canvas)
    drawTrail(app, canvas)
    drawCountdown(app, canvas)
    if app.gameStarted:
        drawCells(app, canvas)
        drawPlayer(app, canvas)
        drawEnemies(app, canvas)
        drawGameInfo(app, canvas)
        if app.gameOver:
            canvas.create_text((app.width-app.spellSize)/2, app.height/2, text = "Game Over", fill = "orange", font = "Arial 60 bold")
    elif not app.countdown:
        drawCover(app, canvas)

runApp(width=1280+600, height=960)