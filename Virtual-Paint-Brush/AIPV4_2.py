import cv2
import numpy as np
import time
import os
import math
import Handtrackingmodule as htm

###################################
# SETTINGS
brushThickness = 15
eraserThickness = 80
shapeThickness = 10
smoothing_factor = 3  
folderPath = "Header" 
###################################

# --- HEADER LOADING LOGIC ---
overlayList = []
header = None
use_virtual_header = False

if os.path.exists(folderPath):
    myList = os.listdir(folderPath)
    myList.sort() 
    print(f"Found header images: {myList}")
    
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
    
    if len(overlayList) > 0:
        header = overlayList[0]
        use_virtual_header = False
    else:
        print("Folder exists but is empty.")
        use_virtual_header = True
else:
    print(f"Folder '{folderPath}' not found. Using Virtual UI.")
    use_virtual_header = True

# Define Variables
drawColor = (0, 0, 255) 
paintColor = (0, 0, 255) 
tool = "draw" 

# Shape drawing variables
shape_start_x, shape_start_y = 0, 0
drawing_active = False 
last_x, last_y = 0, 0

# --- Camera Setup ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85, maxHands=1)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)
img_x, img_y = 0, 0 

def draw_virtual_header(img):
    cv2.rectangle(img, (0, 0), (1280, 125), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, "Header Images Not Found", (400, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

def stamp_shape(canvas, start_pt, end_pt, shape_tool, color, thickness):
    if shape_tool == "rect":
        cv2.rectangle(canvas, start_pt, end_pt, color, thickness)
    elif shape_tool == "circle":
        dist = int(math.hypot(end_pt[0] - start_pt[0], end_pt[1] - start_pt[1]))
        cv2.circle(canvas, start_pt, dist, color, thickness)

print("AI Painter Started...")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1) 
    
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # Index Tip
        x2, y2 = lmList[12][1:] # Middle Tip
        
        last_x, last_y = x1, y1

        fingers = detector.fingersUp()
        
        if len(fingers) >= 5:
            # --- SELECTION MODE (Index + Middle Up) ---
            if fingers[1] and fingers[2]:
                
                # If we were drawing a shape, finish it
                if drawing_active:
                    stamp_shape(imgCanvas, (shape_start_x, shape_start_y), (last_x, last_y), tool, drawColor, shapeThickness)
                    drawing_active = False

                xp, yp = 0, 0 
                
                # --- CHECK CLICKS (EXPLICIT RANGES) ---
                if y1 < 125:
                    
                    # 1. RED BUTTON
                    if 40 < x1 < 200: 
                        drawColor = (0, 0, 255) 
                        paintColor = drawColor
                        tool = "draw"
                        if not use_virtual_header and len(overlayList) > 0: header = overlayList[0]
                    
                    # 2. BLUE BUTTON
                    elif 280 < x1 < 400: 
                        drawColor = (255, 0, 0) 
                        paintColor = drawColor
                        tool = "draw"
                        if not use_virtual_header and len(overlayList) > 1: header = overlayList[1]
                    
                    # 3. GREEN BUTTON
                    elif 510 < x1 < 640: 
                        drawColor = (0, 255, 0) 
                        paintColor = drawColor
                        tool = "draw"
                        if not use_virtual_header and len(overlayList) > 2: header = overlayList[2]
                    
                    # 4. ERASER BUTTON
                    elif 730 < x1 < 810: 
                        drawColor = (0, 0, 0) 
                        tool = "draw"
                        if not use_virtual_header and len(overlayList) > 3: header = overlayList[3]
                    
                    # 5. RECTANGLE BUTTON
                    elif 910 < x1 < 1020:
                        drawColor = paintColor
                        tool = "rect"
                        if not use_virtual_header and len(overlayList) > 4: header = overlayList[4]

                    # 6. CIRCLE BUTTON
                    elif 1080 < x1 < 1230:
                        drawColor = paintColor
                        tool = "circle"
                        if not use_virtual_header and len(overlayList) > 5: header = overlayList[5]

                # Visual feedback for selection
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            # --- DRAWING MODE (Index Only) ---
            elif fingers[1] and fingers[2] == False:
                
                if tool == "draw":
                    drawing_active = False 

                    if xp == 0 and yp == 0: 
                        xp, yp = x1, y1
                        img_x, img_y = x1, y1
                    
                    # Smoothing
                    img_x = img_x + (x1 - img_x) / smoothing_factor
                    img_y = img_y + (y1 - img_y) / smoothing_factor
                    curr_x, curr_y = int(img_x), int(img_y)

                    if drawColor == (0, 0, 0):
                        cv2.line(img, (xp, yp), (curr_x, curr_y), drawColor, eraserThickness)
                        cv2.line(imgCanvas, (xp, yp), (curr_x, curr_y), drawColor, eraserThickness)
                    else:
                        cv2.line(img, (xp, yp), (curr_x, curr_y), drawColor, brushThickness)
                        cv2.line(imgCanvas, (xp, yp), (curr_x, curr_y), drawColor, brushThickness)
                    
                    xp, yp = curr_x, curr_y 
                
                # Shape Preview
                elif tool == "rect" or tool == "circle":
                    if not drawing_active:
                        shape_start_x, shape_start_y = x1, y1
                        drawing_active = True
                    
                    if tool == "rect":
                        cv2.rectangle(img, (shape_start_x, shape_start_y), (x1, y1), drawColor, shapeThickness)
                    elif tool == "circle":
                        dist = int(math.hypot(x1 - shape_start_x, y1 - shape_start_y))
                        cv2.circle(img, (shape_start_x, shape_start_y), dist, drawColor, shapeThickness)

            else:
                if drawing_active:
                    stamp_shape(imgCanvas, (shape_start_x, shape_start_y), (last_x, last_y), tool, drawColor, shapeThickness)
                    drawing_active = False
                xp, yp = 0, 0 
    else:
        if drawing_active:
            stamp_shape(imgCanvas, (shape_start_x, shape_start_y), (last_x, last_y), tool, drawColor, shapeThickness)
            drawing_active = False
        xp, yp = 0, 0 

    # Blending
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 20, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    
    if img.shape == imgCanvas.shape:
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)

    # --- DRAW HEADER ---
    if use_virtual_header:
        draw_virtual_header(img)
    else:
        headerResized = cv2.resize(header, (1280, 125))
        img[0:125, 0:1280] = headerResized

    cv2.imshow("AI Painter", img)
    key = cv2.waitKey(1)
    if key == ord('q'): break
    elif key == ord('c'): imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    elif key == ord('s'): cv2.imwrite(f'Art_{time.time()}.jpg', imgCanvas)

cap.release()
cv2.destroyAllWindows()