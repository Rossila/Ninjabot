import cv2.cv as cv
import cv2
import sys
import numpy as np
import colorfilter
import math

d_red = cv.RGB(150, 55, 65)
l_red = cv.RGB(250, 200, 200)
d_green = cv.RGB(55, 150, 65)
d_purple = cv.RGB(150, 55, 150)

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
    imgmin = cv.CreateImage(cv.GetSize(img),8,1)
    imgmax = cv.CreateImage(cv.GetSize(img),8,1)

    """
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
    """

    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)

    if color[0][0] < color[1][0]:
        cv.InRangeS(imgHSV, color[0], color[1], imgFiltered)
    else:
        cv.InRangeS(imgHSV, (0,color[0][1],color[0][2]), (color[0][0], color[1][1], color[1][2]), imgmin)
        cv.InRangeS(imgHSV, (color[1][0], color[0][1], color[0][2]), (255,color[1][1],color[1][2]), imgmax)
        cv.Add(imgmin, imgmax, imgFiltered)

    return imgFiltered

def colorFilterCombine(img, color1, color2, s):
    imgFiltered = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor1 = cv.CreateImage(cv.GetSize(img),8,1)
    imgColor2 = cv.CreateImage(cv.GetSize(img),8,1)  
    imgCalibrate = cv.CreateImage(cv.GetSize(img),8,1)   
    
    imgColor1 = colorFilter(img, color1 ,s)
    imgColor2 = colorFilter(img, color2 ,s)

    cv.Add(imgColor1, imgColor2, imgFiltered)

    """
    if s != []:
        for value in s:
            imgCalibrate = colorFilter(img, "calibrate" , value)
            cv.Add(imgFiltered, imgCalibrate, imgFiltered)
            print value[0],value[1],value[2], "added"
    """

    return imgFiltered 

'''def channel_processing(channel):
    pass
    cv.AdaptiveThreshold(channel, channel, 255, adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C, thresholdType=cv.CV_THRESH_BINARY, blockSize=55, param1=7)
    #mop up the dirt
    cv.Dilate(channel, channel, None, 1)
    cv.Erode(channel, channel, None, 1)'''

def find_circles(processed, storage, LOW):
    #print "Finding circles" 

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
        cv.HoughCircles(processed, storage, cv.CV_HOUGH_GRADIENT, 2, 40.0, 200, 40, 5, 40) #great to add circle constraint sizes.
    except:
        pass

    if storage.rows == 0:
        print "no circles found"

    return storage

def sort_circles(storage):
    balls = []
    obstacles = []

    if storage.rows <= 0 or storage.rows >= 30 or storage == None:
        return balls, obstacles

    circles = np.asarray(storage)

    for circle in circles:
        Radius, x, y = int(circle[0][2]), int(circle[0][0]), int(circle[0][1])
        if Radius < 14:
            #print "ball found at:", (x,y), "with radius", Radius
            balls.append((x,y))
        else: 
            #print "obstacle found at:", (x,y), "with radius", Radius
            obstacles.append((x,y))

    return balls, obstacles

def draw_circles(balls, obstacles, output):
    # if there are more than 30 circles something went wrong, don't draw anything
    BALL_RADIUS = 13
    OBSTACLE_RADIUS = 20

    for ball in balls:
        cv.Circle(output, (ball[0], ball[1]), BALL_RADIUS, d_red, 3, 8, 0)
    
    for obstacle in obstacles:
        cv.Circle(output, (obstacle[0], obstacle[1]), OBSTACLE_RADIUS, d_green, 3, 8, 0)

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
    

def update_grid(output, warp_coord ):
    #grid = cv.CreateImage((orig.width*2,orig.height), cv.IPL_DEPTH_8U, 3)
    output = perspective_transform(output,warp_coord)
    #draw_grid(output)
    #draw_circles(storage , output)
    return output


def perspective_transform(image_in,warp_coord):
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
    src = np.array([warp_coord[0],warp_coord[1], warp_coord[2], warp_coord[3]],np.float32)
    dst = np.array([[0,0],[image_in.width, 0],[0, image_in.height],[image_in.width, image_in.height]],np.float32)
    retval = cv2.getPerspectiveTransform(src,dst)
    warp = cv2.warpPerspective(image, retval, (cv.GetSize(image_in)))

    output = cv.fromarray(warp)

    return output



def robot_tracking(orig, squares):
    # returns the distance between two inputted points
    def distance_between_points(pt1, pt2):
        return math.sqrt(math.pow((pt1[0]-pt2[0]),2) + math.pow((pt1[1]-pt2[1]),2))
    
    red = colorfilter.red
    blue = colorfilter.blue
    green = colorfilter.green
    yellow = colorfilter.yellow
    head = []
    tail = []
    other_head = []
    other_tail = []
    enemy_robot = []
    head_coord = (0,0)
    tail_coord = (0,0)
    bot_found = False

    robo_tail = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
    robo_head = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)

    enemy_body = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
    # filter for all yellow and blue - everything else is black
    enemy_body = colorFilterCombine(orig, red, red,1)
    

    cv.Smooth(enemy_body, enemy_body, cv.CV_GAUSSIAN, 7, 7)
    
    
    enemy_body_np = np.asarray(enemy_body[:,:])
    contours_enemy_body, hierarchy = cv2.findContours(enemy_body_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    robo_tail = colorFilterCombine(orig, blue, blue,1)
    

    cv.Smooth(robo_tail, robo_tail, cv.CV_GAUSSIAN, 7, 7)
    
    
    robo_tail_np = np.asarray(robo_tail[:,:])
    contours_robo_tail, hierarchy = cv2.findContours(robo_tail_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    robo_head = colorFilterCombine(orig, green, green,1)
    
    cv.Smooth(robo_head, robo_head, cv.CV_GAUSSIAN, 7, 7)
    

    
    robo_head_np = np.asarray(robo_head[:,:])
    contours_robo_head, hierarchy = cv2.findContours(robo_head_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_robo_tail:
        #print "tail: cv2.contourArea(cnt): ", cv2.contourArea(cnt)
        if cv2.contourArea(cnt) >= 1700:

            moments = cv2.moments(cnt)

            massCenterModel = (moments['m10']/moments['m00'],  
                                  moments['m01']/moments['m00']); 
            
            #if massCenterModel
            tail.append(massCenterModel)
        elif cv2.contourArea(cnt) >= 300:
            moments = cv2.moments(cnt)

            massCenterModel = (moments['m10']/moments['m00'],  
                                  moments['m01']/moments['m00']); 
            
            #if massCenterModel
            enemy_robot.append(massCenterModel)


    for cnt in contours_robo_head:
        #print "head: cv2.contourArea(cnt): ", cv2.contourArea(cnt)
        if cv2.contourArea(cnt) >= 1700:

            moments = cv2.moments(cnt)

            massCenterModel = (moments['m10']/moments['m00'],  
                                  moments['m01']/moments['m00']); 
            

            head.append(massCenterModel)
        elif cv2.contourArea(cnt) >= 300:

            moments = cv2.moments(cnt)

            massCenterModel = (moments['m10']/moments['m00'],  
                                  moments['m01']/moments['m00']); 
            
            enemy_robot.append(massCenterModel)

    for cnt in contours_enemy_body:
        #print "head: cv2.contourArea(cnt): ", cv2.contourArea(cnt)
        if cv2.contourArea(cnt) >= 300:

            moments = cv2.moments(cnt)

            massCenterModel = (moments['m10']/moments['m00'],  
                                  moments['m01']/moments['m00']); 


            enemy_robot.append(massCenterModel)
        else:
            pass
    
    #print "enemy_robot", enemy_robot
    #print "head: ", head
    #print "tail: ", tail
    for bot in enemy_robot:
        cv.Circle(orig, (int(bot[0]), int(bot[1])), 4, d_purple, -1, 8, 0)

    if len(head) > 0:
        h = head[0]
    if len(head) > 1:
        h2 = head[1]
    for t in tail:
        if len(head) > 0 and distance_between_points(h, t) < 55:
            #print "distance beteen h and t: ", distance_between_points(h, t)
            head_pt = h
            tail_pt = t
            bot_found = True
            break
        if len(head) > 1 and distance_between_points(h2, t) < 55:
            #print "distance between h2 and t: ", distance_between_points(h2, t)
            head_pt = h2
            tail_pt = t
            bot_found = True
            break

    if not bot_found:
        try:
            #print "distance_between_points(head[0], tail[0])", distance_between_points(head[0], tail[0])
            cv.Circle(orig, (int(head[0][0]),int(head[0][1]) ), 1, l_red, -1, 8, 0)
            cv.Circle(orig, (int(tail[0][0]),int(tail[0][1]) ), 1, d_red, -1, 8, 0)
        except:
            print "haven't found anything"

        #print "enemy_robot", enemy_robot
        return tail_coord, head_coord, enemy_robot

    try:
        head_coord = (int(head_pt[0]),int(head_pt[1]))
        cv.Circle(orig, (int(head_pt[0]),int(head_pt[1]) ), 4, l_red, -1, 8, 0)
        tail_coord = (int(tail_pt[0]),int(tail_pt[1]) )
        cv.Circle(orig, (int(tail_pt[0]),int(tail_pt[1]) ), 4, l_red, -1, 8, 0)
        cv.Line(orig, (int(head_pt[0]),int(head_pt[1])), (int(tail_pt[0]),int(tail_pt[1])), d_red, thickness=2, lineType=8, shift=0)
    except:
        print "failed"
    #print "enemy_robot", enemy_robot
    return tail_coord, head_coord, enemy_robot
