
rows = 20
cols = 20
gameMap = [[0]*cols for i in range(rows)]

def isNeighbor(maze, row, col, rows, cols):
    if (rows, cols) in maze:
        return False
    count = 0
    for dRow, dCol in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
        newRow = row + dRow
        newCol = col + dCol
        if (newRow, newCol) in maze:
            count += 1
    
    if count == 1:
        return True
    return False  

def makeMaze(startX, startY, rows, cols):
    maze = {(startX, startY)}
    for i in range(rows*cols-1):
        newX = random.randint(0, cols)
        newY = random.randint(0, rows)
        while not isNeighbor(maze, newX, newY, rows, cols):
            newX = random.randint(0, cols)
            newY = random.randint(0, rows)
        maze.add((newX, newY))
    return maze

from cmu_112_graphics import *
import random
# 45, 60
def appStarted(app):
    app.addWalls = False
    app.rows = 20
    app.cols = 20
    app.margin = 5 # margin around grid
    app.selections = [] # (row, col) of selection, (-1,-1) for none
    app.walls = [[False]*cols for i in range(rows)]
    for i in range(10):
        randX = random.randint(0, app.cols-1)
        randY = random.randint(0, app.rows-1)
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        randLength = random.randint(7, 20)
        for i in range(randLength):
            curX = randX + i*dx
            curY = randY + i*dy
            if 0 <= curX < app.cols and 0 <= curY < app.rows:
                app.walls[curX][curY] = True
    app.walls = makeMaze(0, 0, app.rows, app.cols)
    print(app.walls)
    app.path = []

def pointInGrid(app, x, y):
    # return True if (x, y) is inside the grid defined by app.
    return ((app.margin <= x <= app.width-app.margin) and
            (app.margin <= y <= app.height-app.margin))

def getCell(app, x, y):
    cellWidth  = (app.width - 2*app.margin) / app.cols
    cellHeight = (app.height - 2*app.margin) / app.rows
    row = int((y - app.margin) // cellHeight)
    col = int((x - app.margin) // cellWidth)
    return (row, col)

def getCellBounds(app, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)

def mousePressed(app, event):
    (row, col) = getCell(app, event.x, event.y)
    if app.addWalls:
     app.walls[row][col] = not app.walls[row][col]
    else:
        app.selections = []

def keyPressed(app, event):
    if event.key == 'w':
        app.addWalls = not app.addWalls

def redrawAll(app, canvas):
    # draw grid of cells
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            if ((row, col) in app.path):
                fill = "orange"
            else:
                fill = "cyan"
            if (row, col) in app.walls:
                fill = "black"
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill)

runApp(width=640, height=480)