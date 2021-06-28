import cv2
import numpy as np
from time import sleep

# setting minimum dimensions for rectangle bounding any vehicle
Min_rectangle_width = 80
Min_rectangle_height = 80

# Error allowed between pixel
offset = 6
# Counting line position
Line_pos = 550

delay = 45
detect = []
total_vehicles = 0
# function to find center of object bounding rectangle


def set_center(x, y, w, h):
    center_x = x + int(w / 2)
    center_y = y + int(h / 2)
    return center_x, center_y


# defining a video capture object and playing video saved in file
cap = cv2.VideoCapture(r'vehicle_detection.mp4')
# detecting object from a stable camera
detecting_object = cv2.bgsegm.createBackgroundSubtractorMOG(
    history=100)

while True:
    # capturing video frame by frame
    ret, frame = cap.read()
    sleep(float(1/(delay)))
    # changing the colorspace to grey
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # using gaussian smoothening to reduce noise
    blur = cv2.GaussianBlur(grey, (3, 3), 7)
    mask = detecting_object.apply(blur)
    # cleaning the mask by only keeping white pixels and removing grey pixels
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    # using dilation to increase object area and join any broken parts
    dilate = cv2.dilate(mask, np.ones((5, 5)))
    # getting structured element for dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilated = cv2.morphologyEx(dilate, cv2. MORPH_CLOSE, kernel)
    # getting contours of objects
    contour, h = cv2.findContours(
        dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # setting a region of interest for contour lines to be shown in the original video
    roi = frame[0: 360, 0: 1000]
    for cnt in contour:
        # calculating the area and not displaying contours of smaller elements in the video
        area = cv2.contourArea(cnt)
        if area > 2000:
            cv2.drawContours(roi, [cnt], -1, (0, 0, 255), 1)
    # creating the line used for counting
    cv2.line(frame, (0, Line_pos), (1300, Line_pos), (8, 243, 247), 1)

    font = cv2.FONT_HERSHEY_COMPLEX
    fontScale = 1.5
    fontColor = (6, 132, 231)
    lineType = 2

    for(index, contour) in enumerate(contour):
        (x, y, w, h) = cv2.boundingRect(contour)
        # checking if the rectangle has the minimum dimensions to possibly be a vehicle
        check_outline = (w >= Min_rectangle_width) and (
            h >= Min_rectangle_height)
        if not check_outline:
            continue
        # drawing rectangle around object
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        center = set_center(x, y, w, h)
        # adding the center coordinates to the list detect
        detect.append(center)
        cv2.circle(frame, center, 4, (0, 0, 255), -1)
        # classifying vehicles as car/bike/Heavy Motor Vehicle(HMV) by contour area
        area2 = cv2.contourArea(contour)
        if(area2 > 10000 and area2 < 20000):
            cv2.putText(frame, "CAR", (center[0], center[1]-int(h/2)-30),
                        font, 1, (255, 0, 0), lineType)
        elif(area2 < 3000):
            cv2.putText(frame, "BIKE", (center[0], center[1]-int(h/2)-30),
                        font, 1, (255, 0, 0), lineType)
        elif(area2 > 40000):
            cv2.putText(frame, "HMV", (center[0], center[1]-int(h/2)-30),
                        font, 1, (255, 0, 0), lineType)

        for (x, y) in detect:
            # checking if the center coordinates pass through the line with some offset/error allowed
            if y < (Line_pos+offset) and y > (Line_pos-offset):
                total_vehicles += 1
                # line changes color to indicate a vehicle has been counted
                cv2.line(frame, (0, y),
                         (1300, y), (0, 255, 0), 5)
                # displaying the individual vehicle count over each vehicle when it passes the line
                cv2.putText(frame, str(total_vehicles), (x, y),
                            font, fontScale, fontColor, lineType)

                sleep(0.1)
                detect.remove((x, y))
                print("Vehicle detected : "+str(total_vehicles))

    font = cv2.FONT_HERSHEY_COMPLEX
    Text_bottom_Left = (350, 100)
    fontScale = 2
    fontColor = (0, 0, 0)
    lineType = 2
    # displaying the overall vehicle count at the top of the video
    cv2.putText(frame, "VEHICLE COUNT : "+str(total_vehicles), Text_bottom_Left,
                font, fontScale, fontColor, lineType)
    # displaying the orignal video with the counter and the dilated video
    cv2.imshow("Original Video", frame)
    cv2.imshow("Detector", dilated)

    # used for setting roi
    # cv2.imshow("roi",roi)

    # checking functions
    #cv2.imshow("grey", grey)
    #cv2.imshow("blur", blur)

    # Setting the 'q' key as the escape button to stop running the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# destroying all windows
cv2.destroyAllWindows()
# releasing the cap object
cap.release()
