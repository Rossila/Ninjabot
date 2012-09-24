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
        maxColor = cv.Scalar(30, 255, 255)
    elif color == "blue":
        minColor = cv.Scalar(100,100,100)
        maxColor = cv.Scalar(120,255,255)

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
storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)


while True:
    orig = cv.QueryFrame(capture)

    # filter for all yellow and blue - everything else is black
    processed = colorFilterCombine(orig, "yellow", "blue")
    
    # Some processing and smoothing for easier circle detection
    cv.Canny(processed, processed, 5, 70, 3)
    cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)
    
    cv.ShowImage('processed2', processed)
    
    # Find&Draw circles
    find_circles(processed, storage, 100)
    draw_circles(storage, orig)

    # Delete and recreate the storage so it has the correct width
    del(storage)
    storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
    
    cv.ShowImage('output', orig)

    if cv.WaitKey(10) == 27:
        break
