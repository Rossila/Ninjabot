import cv2.cv as cv
import cv2
import sys
import numpy as np

capture = cv.CaptureFromCAM(0)

# some random colors to draw circles and their center points with
d_red = cv.RGB(150, 55, 65)
l_red = cv.RGB(250, 200, 200)

def colorFilter(img, color):

    imgHSV = cv.CreateImage(cv.GetSize(img),8,3)
    cv.CvtColor(img, imgHSV, cv.CV_BGR2HSV)

    if color == "yellow":
        minColor = cv.Scalar(20, 70, 70)
        maxColor = cv.Scalar(60, 255, 255)
    elif color == "blue":
        minColor = cv.Scalar(100,100,100)
        maxColor = cv.Scalar(120,255,255)
    elif color == "red":
        minColor = cv.Scalar(160, 70,70)
        maxColor = cv.Scalar(180, 255, 255)
    elif color == "green":
        minColor = cv.Scalar(70, 70, 70)
        maxColor = cv.Scalar(80, 255, 255)    
    elif color == "calibrate":
         minColor = cv.Scalar(calibrate[0],calibrate[1],calibrate[2])
         maxColor = minColor

    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)

    cv.InRangeS(imgHSV, minColor, maxColor, imgFiltered)

    return imgFiltered

def colorFilterCombine(img, color1, color2):
    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor1 = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor2 = cv.CreateImage(cv.GetSize(img),8,1)   
    
    imgColor1 = colorFilter(img, color1)
    imgColor2 = colorFilter(img, color2)

    cv.Add(imgColor1, imgColor2, imgFiltered)

    return imgFiltered 

'''def channel_processing(channel):
    pass
    cv.AdaptiveThreshold(channel, channel, 255, adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C, thresholdType=cv.CV_THRESH_BINARY, blockSize=55, param1=7)
    #mop up the dirt
    cv.Dilate(channel, channel, None, 1)
    cv.Erode(channel, channel, None, 1)'''

def find_circles(processed, storage, LOW):
    print "Finding circles" 

    # Use Hough Circles algorithm to find circles
    # Parameters:
    # @ image is the 8-bit single channel image you want to search for circles in. 
    # @ circle_storage is where the function puts its results. You can pass a CvMemoryStorage structure here.
    # @ method is always CV_HOUGH_GRADIENT
    # @ dp lets you set the resolution of the accumulator. dp is a kind of scaling down factor. 
    #       The greater its value, the lower the resolution of the accumulator. dp must always be more than or equal to 1.
    # @ min_dist is the minimum distance between circle to be considered different circles.
    # @ param1 is used for the (internally called) canny edge detector. The first parameter of the canny is set to param1, and the second is set to param1/2.
    # @ param2 sets the minimum number of votes that an accumulator cell needs to qualify as a possible circle.
    # @ min_radius and max_radius do exactly what to mean. They set the minimum and maximum radii the function searches for.
    
    try:
        cv.HoughCircles(processed, storage, cv.CV_HOUGH_GRADIENT, 2, 30.0, 70, 70, 25, 70) #great to add circle constraint sizes.
    except:
        pass

    if storage.rows == 0:
        print "no circles found"

    return storage

def draw_circles(storage, output):
    # if there are more than 30 circles something went wrong, don't draw anything
    if storage.rows <= 0:
        return
    if storage.rows >= 30:
        return

    circles = np.asarray(storage)
    print 'drawing: ' + str(len(circles)) + ' circles'

    for circle in circles:
        Radius, x, y = int(circle[0][2]), int(circle[0][0]), int(circle[0][1])
        cv.Circle(output, (x, y), 1, l_red, -1, 8, 0)
        cv.Circle(output, (x, y), Radius, d_red, 3, 8, 0)


orig = cv.QueryFrame(capture)
processed = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)

red = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
green = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
squares = []

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

while True:
    orig = cv.QueryFrame(capture)

    # filter for all yellow and blue - everything else is black
    red = colorFilterCombine(orig, "red", "red")
    
    # Some processing and smoothing for easier circle detection
    #cv.Canny(red, red, 5, 70, 3)
    cv.Smooth(red, red, cv.CV_GAUSSIAN, 7, 7)
    
    #cv.ShowImage('red2', red)
    
    red_np = np.asarray(red[:,:])
    contours_red, hierarchy = cv2.findContours(red_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    green = colorFilterCombine(orig, "green", "green")
    
    # Some processing and smoothing for easier circle detection
    #cv.Canny(green, green, 5, 70, 3)
    cv.Smooth(green, green, cv.CV_GAUSSIAN, 7, 7)
    
    #cv.ShowImage('green2', green)
    
    green_np = np.asarray(green[:,:])
    contours_green, hierarchy = cv2.findContours(green_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_red:
        try:
            if cv2.contourArea(cnt) >= 3000:

                moments = cv2.moments(cnt)

                massCenterModel = (moments['m10']/moments['m00'],  
                                      moments['m01']/moments['m00']); 
                
                #if massCenterModel
                squares.append((massCenterModel,"red"))
        except TypeError:
            pass

    for cnt in contours_green:
        try:
            if cv2.contourArea(cnt) >= 3000:

                moments = cv2.moments(cnt)

                massCenterModel = (moments['m10']/moments['m00'],  
                                      moments['m01']/moments['m00']); 
                
                #if massCenterModel
                squares.append((massCenterModel,"green"))

        except TypeError:
            pass


    # Find&Draw circles
    #find_circles(processed, storage, 100)
    #draw_circles(storage, orig)

    # Delete and recreate the storage so it has the correct width
    ##del(squares)
    #squares = []
    #for lista in squares:
    while squares:
        head = squares.pop()

        if (head[1] == "red"):
            tail_coord = (int(head[0][0]),int(head[0][1]) )
            cv.Circle(orig, (int(head[0][0]),int(head[0][1]) ), 1, l_red, -1, 8, 0)
            if (squares != []):
                tail = squares.pop()
                if(tail[1]== "green"):
                    head_coord = (int(tail[0][0]),int(tail[0][1]))
                    cv.Circle(orig, (int(tail[0][0]),int(tail[0][1]) ), 1, l_red, -1, 8, 0)
                    cv.Line(orig, (int(head[0][0]),int(head[0][1])), (int(tail[0][0]),int(tail[0][1])), d_red, thickness=2, lineType=8, shift=0)

        if (head[1] == "green"):
            head_coord = (int(head[0][0]),int(head[0][1]))
            cv.Circle(orig, (int(head[0][0]),int(head[0][1]) ), 1, l_red, -1, 8, 0)
            if (squares != []):
                tail = squares.pop()
                if(tail[1]== "red"):
                    tail_coord = (int(tail[0][0]),int(tail[0][1]) )
                    cv.Circle(orig, (int(tail[0][0]),int(tail[0][1]) ), 1, l_red, -1, 8, 0)
                    cv.Line(orig, (int(head[0][0]),int(head[0][1])), (int(tail[0][0]),int(tail[0][1])), d_red, thickness=2, lineType=8, shift=0)

        try:
            cv.Circle(orig, head_coord, 5, l_red, -1, 8, 0)

        except NameError:
            pass

        try:
            cv.Circle(orig, tail_coord, 5, d_red, -1, 8, 0)

        except NameError:
            pass
    #    print lista
    #   orig_np = np.asarray(orig[:,:])
    #cv2.drawContours( orig_np, squares, -1, (0, 255, 0), 3 )

    #print squares
    #orig = cv.fromarray(orig_np)
    cv.ShowImage('output', orig)
    squares = []
    if cv.WaitKey(10) == 27:
        break
