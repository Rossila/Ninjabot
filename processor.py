import cv2.cv as cv
import cv2
import sys
import numpy as np

d_red = cv.RGB(150, 55, 65)
l_red = cv.RGB(250, 200, 200)

def autocalibrate(orig, storage):
    
    circles = np.asarray(storage)
    #print 'drawing: ' + str(len(circles)) + ' circles'

    min_value = 255
    max_value = 0
    s = []
    for circle in circles:
        Radius, x, y = int(circle[0][2]), int(circle[0][0]), int(circle[0][1])
        processed =  cv.CreateImage(cv.GetSize(orig),8,3)
        cv.CvtColor(orig,processed, cv.CV_BGR2HSV)
        s.append(cv.Get2D(processed,y,x))

    return s
        
    #cropped  = cv.CreateImage((Radius/2,Radius/2),8,3)
    #sub = cv.GetSubRect(orig,(x,y,Radius/2,Radius/2))
    #cv.Copy(sub,cropped)
    #cv.ShowImage('cropped',cropped)
    #hist = cv.CreateHist([180], cv.CV_HIST_ARRAY, [(0,180)], 1 )
    """cv.CalcHist(cropped,hist)
    (min_tmp,max_tmp, _, _) = cv.GetMinMaxHistValue(hist)
    if min_tmp <= min_value:
        min_value = min_tmp
    if max_tmp >= max_value:
        max_value = max_tmp"""
    #return cropped


def colorFilter(img, color, calibrate):

    imgHSV = cv.CreateImage(cv.GetSize(img),8,3)
    cv.CvtColor(img, imgHSV, cv.CV_BGR2HSV)

    if color == "yellow":
        minColor = cv.Scalar(20, 70, 70)
        maxColor = cv.Scalar(60, 255, 255)
    elif color == "blue":
        minColor = cv.Scalar(100,100,100)
        maxColor = cv.Scalar(120,255,255)
    elif color == "calibrate":
         minColor = cv.Scalar(calibrate[0],calibrate[1],calibrate[2])
         maxColor = minColor

    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)

    cv.InRangeS(imgHSV, minColor, maxColor, imgFiltered)

    return imgFiltered

def colorFilterCombine(img, color1, color2, s):
    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor1 = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor2 = cv.CreateImage(cv.GetSize(img),8,1)  
    imgCalibrate = cv.CreateImage(cv.GetSize(img),8,1)   
    
    imgColor1 = colorFilter(img, color1 ,s)
    imgColor2 = colorFilter(img, color2 ,s)

    cv.Add(imgColor1, imgColor2, imgFiltered)

    if s != []:
        for value in s:
            imgCalibrate = colorFilter(img, "calibrate" , value)
            cv.Add(imgFiltered, imgCalibrate, imgFiltered)
            print value[0],value[1],value[2], "added"

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


def draw_grid(grid):
    #bg = cv.Scalar(255, 255, 255)
    #cv.Rectangle(grid,(0,0),(grid.width,grid.width),bg, cv.CV_FILLED )

    color = cv.Scalar(20, 70, 70)
    x=0;
    while x < grid.width:
        #cv.Point
        cv.Line(grid, (x,0), (x,grid.width), color, thickness=1, lineType=8, shift=0)
        x = x  + 20;

    x=0;
    while x < grid.height:
        #cv.Point
        cv.Line(grid, (0,x), (grid.width,x), color, thickness=1, lineType=8, shift=0)
        x = x  + 20;    
        #for y in range(0 , grid.height):
         #   cv.Line(grid, (x,x), (x,y), color, thickness=1, lineType=8, shift=5)
    #for
     #   Line(img, pt1, pt2, color, thickness=1, lineType=8, shift=0)    
    

def update_grid(storage, output, grid ):
    #grid = cv.CreateImage((orig.width*2,orig.height), cv.IPL_DEPTH_8U, 3)
    warp = perspective_transform(output)
    draw_grid(warp)
    
    #draw_circles(storage , warp)
    return warp


def perspective_transform(image_in):
    #gray = cv.CreateImage(cv.GetSize(image_in),8,1)
    #cv.CvtColor(image_in,gray, cv.CV_BGR2GRAY)
    image = np.asarray(image_in[:,:])
    #img = cv2.GaussianBlur(image,(5,5),0)
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #eig_image = cv.CreateImage(cv.GetSize(image_in),8,1)
    #temp_image= cv.CreateImage(cv.GetSize(image_in),8,1)
    #cornerMap = cv.CreateMat(image_in.height, image_in.width, cv.CV_32FC1)
    #cornerMap =cv.GoodFeaturesToTrack(gray, eig_image, temp_image, 4, 0.04, 1, useHarris = True)
    #print cornerMap #[(491.0, 461.0), (203.0, 38.0), (195.0, 58.0), (201.0, 56.0)]
    src = np.array([[225,0],[545,44],[0,398],[450,480]],np.float32)
    dst = np.array([[0,0],[image_in.width,image_in.height],[0,image_in.height],[image_in.width,0]],np.float32)
    retval = cv2.getPerspectiveTransform(src,dst)
    warp = cv2.warpPerspective(image, retval, (cv.GetSize(image_in)))

    output = cv.fromarray(warp)

    return output


