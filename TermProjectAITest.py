
rows = 200
cols = 200

gameMap = [[0]*cols for i in range(rows)]
#print(gameMap)

def findShortestPath(startRow, startCol, endRow, endCol, rows, cols, walls):
    found = False
    cellMap = {}
    visitedCells = set()
    unvisitedNeighborsQueue = [(startRow, startCol)]
    while len(unvisitedNeighborsQueue) != 0:
        row, col = unvisitedNeighborsQueue[0]
        unvisitedNeighborsQueue.pop(0)
        if (row, col) in visitedCells:
            continue
        else:
            visitedCells.add((row, col))
        if row == endRow and col == endCol:
            found = True
            break
        #for dRow in [-1, 0, 1]:
            #for dCol in [-1, 0, 1]:
            #(-1, -1),(1, 1),(-1, 1),(1, -1),
            #[(-1, 0),(-1, -1),(0, -1),(1,-1),(1, 0),(1, 1),(0, 1), (-1, 1)]
        for dCol, dRow in [(-1, 0),(0, 1),(1, 0), (0, -1),(-1, -1),(1, 1),(-1, 1),(1, -1)]:
            newRow = row - dRow
            newCol = col - dCol
            if 0 <= newRow < rows and 0 <= newCol < cols and (newRow, newCol) not in visitedCells and not walls[newRow][newCol]:
                unvisitedNeighborsQueue.append((newRow, newCol))
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
            

#print(findShortestPath(0, 0, 18, 10, rows, cols, walls))

#[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
# (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10),
# (10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (15, 10), (16, 10), (17, 10), (18, 10)]


# [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
# (0, 11), (0, 12), (0, 13), (0, 14), (0, 15), (0, 16), (0, 17), (0, 18), (0, 19),
# (1, 19), (2, 19), (3, 19), (4, 19), (5, 19), (6, 19), (7, 19), (8, 19), (9, 19),
# (10, 19), (11, 19), (11, 18), (11, 17), (11, 16), (11, 15), (11, 14), (11, 13),
# (11, 12), (11, 11), (11, 10), (12, 10), (13, 10), (14, 10), (15, 10), (16, 10), (17, 10), (18, 10)]

from cmu_112_graphics import *
import random

def appStarted(app):
    app.addWalls = False
    app.rows = 45
    app.cols = 60
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
        app.path = findShortestPath(0, 0, row, col, app.rows, app.cols, app.walls)
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
            if app.walls[row][col]:
                fill = "black"
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill)

runApp(width=640, height=480)