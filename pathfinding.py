#!/usr/bin/python
import cv2
import cv2.cv as cv
import numpy as np
import math
import fractions

# define colors
d_red = cv.RGB(150, 55, 65)
d_green = cv.RGB(55, 150, 65)
d_blue = cv.RGB(55, 65, 150)
l_red = cv.RGB(250, 200, 200)
black = cv.RGB(100, 100, 100)
d_purple = cv.RGB(150, 55, 150)
# a list of ranges of x & y to indicate previously travelled paths
travelled_paths = []
# define radii
# make the obstacle_radius + rover_width 2/sqrt(2) times larger than it needs to be 
ball_radius = 18
obstacle_radius = 33
rover_width = 50
TRAV_UNIT = 40
TURN_ANGLE = 5

image = cv2.imread('empty.jpg')

# will fix this later
class Point:
	def __init__(self,x,y):
		self.x = x
		self.y = y

def draw_grid(image):
    x=0;
    while x < image.shape[1]:
        cv2.line(image, (x,0), (x,image.shape[0]), l_red, thickness=1, lineType=8, shift=0)
        x = x  + 15;

    x=0;
    while x < image.shape[0]:
        cv2.line(image, (0,x), (image.shape[1],x), l_red, thickness=1, lineType=8, shift=0)
        x = x  + 15;    

def draw_line(start, end, color):
    cv2.line(image, start, end, color, thickness = 1, lineType=8, shift=0)

def draw_line_polar(start, angle, distance):
	# convert angle to radians
	angle = float(angle)/180 * math.pi
	
	print "angle in radians: ", angle
	# x = rcos(theta)
	# y = rsin(theta)
	x = distance * math.cos(angle)
	y = distance * math.sin(angle)

	end = (int(start[0] + x), int(start[1] + y))

	#draw_line(start, end, d_purple)
	cv2.line(image, start, end, d_purple, thickness = 2, lineType=8, shift=0)

def draw_circle(radius, x, y, color):
    cv2.circle(image, (x, y), 1, black, -1, 8, 0)
    cv2.circle(image, (x, y), radius, color, 3, 8, 0)

# Angle system:
#        (270)
#          |
#          |
# (180)---------> x (0)
#          |
#          |
#          v
#        y(90)

def line_angle(startPoint, endPoint):
	x1 = float(startPoint[0])
	y1 = float(startPoint[1])
	x2 = float(endPoint[0])
	y2 = float(endPoint[1])

	angle = math.atan((y2 - y1)/(x2 - x1)) #angle in radians
	angle = angle * 180 / math.pi #convert to degrees

	if (y2 - y1) <= 0:
		if (x2 - x1) <= 0: #angle is in the 3rd quadrant (180-270)
			angle = angle + 180
		else: #angle is in the 4th quadrant (270-360)
			angle = angle + 360
	else: 
		if (x2 - x1) <= 0: #angle is in the 2nd quadrant (90-180)
			angle = angle + 180
		#else angle is in the 1st quadrant (90-180)

	return angle

# returns the distance between two inputted points
def distance_between_points(pt1, pt2):
	return math.sqrt(math.pow((pt1[0]-pt2[0]),2) + math.pow((pt1[1]-pt2[1]),2))

# returns the index of the closest ball in balls to the current bot_loc
def find_closest_ball(balls, bot_loc):
	min_index = 0
	dist = 0
	shortest_dist = distance_between_points(balls[0], bot_loc)
	for index, ball in enumerate(balls):
		dist = distance_between_points(ball, bot_loc)
		#print "distance index: ", index, "distance: ", dist
		if dist < shortest_dist:
			shortest_dist = dist
			min_index = index

	return min_index

# returns true if the line segment from ln1_start to ln1_end
# intersects with the line segment from ln2_start to ln2_end
def intersect(ln1_start, ln1_end, ln2_start, ln2_end):
	def ccw(A,B,C): # returns true if ABC are in ccw order, false otherwise
		return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
	
	return ccw(ln1_start,ln2_start,ln2_end) != ccw(ln1_end,ln2_start,ln2_end) and \
		ccw(ln1_start,ln1_end,ln2_start) != ccw(ln1_start,ln1_end,ln2_end)

def checkIntersections(bot_loc, bot_dest, obstacles, intersections):

	def findConstants(bot_loc, bot_dest, distance):
		# (ax)/(ay) find a s.t. (ax)^2 + (ay)^2 = distance^2
		# ax and ay will be the x and y displacement
		x_dspl = 0
		y_dspl = 0

		diff_y = bot_dest[0] - bot_loc[0]
		diff_x = - bot_dest[1] + bot_loc[1]

		#we're done! close enough, don't do anything more
		if diff_x <= 10 and diff_x >= -10 and diff_y <= 10 and diff_y >= -10: 
			pass
		elif diff_x == 0:
			x_dspl = 0
			y_dspl = distance
		elif diff_y == 0:
			x_dspl = distance
			y_dspl = 0
		else: 
			a = math.sqrt(pow(distance, 2)/float(pow(diff_x,2) + pow(diff_y,2)))
			x_dspl = a * diff_x
			y_dspl = a * diff_y
		return x_dspl, y_dspl


	# returns the two end points of a parallel line segment (@distance) away from the original line
	def getParallelLine(ln1_start, ln1_end, distance, dir):
		ln2_start = (0,0)
		ln2_end = (0,0)

		x_dspl, y_dspl = findConstants(bot_loc, bot_dest, distance)
		
		if dir == "bottom":
			x_dspl = -1 * x_dspl
			y_dspl = -1 * y_dspl
		ln2_start = (int(ln1_start[0] + x_dspl), int(ln1_start[1] + y_dspl))
		ln2_end = (int(ln1_end[0] + x_dspl), int(ln1_end[1] + y_dspl))

		return ln2_start, ln2_end

	def checkObstacles(bot_loc, bot_dest, obstacles, intersections):
		#slope = getSlope(bot_loc, bot_dest)
		#if slope == None:
		#	return intersections
		#perpSlope = -1/slope
		
		ln2_start_top, ln2_end_top = getParallelLine(bot_loc, bot_dest, 50, "top")
		ln2_start_bot, ln2_end_bot = getParallelLine(bot_loc, bot_dest, 50, "bottom")
		
		#draw_line(ln2_start_top, ln2_end_top, d_red)
		#draw_line(ln2_start_bot, ln2_end_bot, d_red)
		x_dspl, y_dspl = findConstants(bot_loc, bot_dest, obstacle_radius + rover_width)
		for index, obstacle in enumerate(obstacles):
			obs_proj1 = (int(obstacle[0] + x_dspl), int(obstacle[1] + y_dspl))
			obs_proj2 = (int(obstacle[0] + -1*x_dspl), int(obstacle[1] + -1*y_dspl))
			draw_line(obs_proj1, obs_proj2, d_blue)
			if intersect(bot_loc, bot_dest, obs_proj1, obs_proj2) or distance_between_points(bot_dest, obstacle) < obstacle_radius + rover_width:
			#	print "intersection found at", obs_proj1
			#	intersections.append(index)
			#elif intersect(bot_loc, bot_dest, obs_proj2, obstacle):
			#	print "intersection found at", obs_proj2
				intersections.append(index)
		#print intersections
		return intersections
	
	return checkObstacles(bot_loc, bot_dest, obstacles, intersections)

def getPOI(bot_loc, bot_dest, obstacle, POI):
	# theta is in radians
	def getSlope(theta):
		slope = math.sin(theta)/math.cos(theta)
		return slope

	def getEndPt(startPoint, secondPoint, distance):
		ratio = (distance + 10)/distance_between_points(startPoint, secondPoint)
		diffx = secondPoint[0] - startPoint[0]
		diffy = secondPoint[1] - startPoint[1]

		return (secondPoint[0] + diffx * ratio, secondPoint[1] + diffy * ratio)

	def getTangent(bot_loc, obstacle):
		hypotenuse = distance_between_points(bot_loc, obstacle)
		side = obstacle_radius + rover_width
		diff_theta = math.asin(side/float(hypotenuse))
		theta = math.atan((obstacle[1] - float(bot_loc[1]))/(obstacle[0] - float(bot_loc[0])))
		slope1 = getSlope(theta + diff_theta)
		print "slope 1: ", slope1

		#y = (slope)x + (displacement)
		displacement1 = bot_loc[1] - slope1 * bot_loc[0]
		bot_dest = (100, int(slope1 * (100) + displacement1))
		bot_dest2 = (500, int(slope1 * 500 + displacement1))
		draw_line(bot_dest, bot_dest2, d_green)

		slope2 = getSlope(theta - diff_theta)
		print "slope 2: ", slope2
		#y = (slope)x + (displacement)
		displacement2 = bot_loc[1] - slope2 * bot_loc[0]

		bot_dest = (100, int(slope2 * (100) + displacement2))
		bot_dest2 = (800, int(slope2 * 800 + displacement2))
		draw_line(bot_dest, bot_dest2, d_blue)

		draw_circle(side, obstacle[0], obstacle[1], d_red)
		return slope1, displacement1, slope2, displacement2 

	aslope1, adispl1, aslope2, adispl2 = getTangent(bot_loc, obstacle)
	
	# slope of tangent line coming out of the center of the circle
	bslope1 = -1 / float(aslope1)
	bslope2 = -1 / float(aslope2)

	bdispl1 = obstacle[1] - bslope1 * obstacle[0]
	bdispl2 = obstacle[1] - bslope2 * obstacle[0]

	x1 = (bdispl1 - adispl1)/(aslope1 - bslope1)
	y1 = bslope1 * x1 + bdispl1
	if int(distance_between_points((x1, y1), obstacle)) - obstacle_radius - rover_width <= 2 and x1 > rover_width and y1 > rover_width:
		draw_circle(4, int(x1), int(y1), black)
		(x1, y1) = getEndPt(bot_loc, (x1, y1), obstacle_radius + rover_width)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x1), int(y1)))

	x2 = (bdispl2 - adispl2)/(aslope2 - bslope2)
	y2 = bslope2 * x2 + bdispl2
	if int(distance_between_points((x2, y2), obstacle)) - obstacle_radius - rover_width <=2 and x2 > rover_width and y2 > rover_width:
		draw_circle(4, int(x2), int(y2), black)
		(x2, y2) = getEndPt(bot_loc, (x2, y2), obstacle_radius + rover_width)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x2), int(y2)))

	x3 = (bdispl1 - adispl2)/(aslope2 - bslope1)
	y3 = bslope1 * x3 + bdispl1
	if int(distance_between_points((x3, y3), obstacle)) - obstacle_radius - rover_width <=2 and x3 > rover_width and y3 > rover_width:
		draw_circle(4, int(x3), int(y3), black)
		(x3, y3) = getEndPt(bot_loc, (x3, y3), obstacle_radius + rover_width)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x3), int(y3)))

	x4 = (bdispl2 - adispl1)/(aslope1 - bslope2)
	y4 = bslope2 * x4 + bdispl2
	if int(distance_between_points((x4, y4), obstacle)) - obstacle_radius - rover_width <=2 and x4 > rover_width and y4 > rover_width:
		draw_circle(4, int(x4), int(y4), black)
		(x4, y4) = getEndPt(bot_loc, (x4, y4), obstacle_radius + rover_width)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x4), int(y4)))

	return POI

# expected vs actual travel
def robotTravel(bot_dir, bot_loc, next_pt):
	angle = line_angle(bot_loc, next_pt)
	# want turn to be between -180 to 180 degrees,
	# neg degrees are ccw
	# pos degrees are cw
	turn = angle - bot_dir
	print turn
	turn = int(turn/TURN_ANGLE) * TURN_ANGLE
	print turn
	distance = distance_between_points(bot_loc, next_pt)
	print distance
	distance = int(distance/TRAV_UNIT + 0.50) * TRAV_UNIT
	print distance

	angle = int(bot_dir + turn)

	print "bot_loc: ", bot_loc, "angle: ", angle, "distance: ", distance
	draw_line_polar(bot_loc, angle, distance)

# Initialize Coordinates
bot_loc = (image.shape[1]/2, rover_width)
bot_dir = 90
balls = [(449, 620), (600, 200), (250, 500), (159, 100)]
obstacles = [(400, 453), (274, 114), (290, 190), (588, 621)]

# Draw the balls and obstacles
for ball in balls:
	draw_circle(ball_radius, ball[0], ball[1], d_red)

for obstacle in obstacles:
	draw_circle(obstacle_radius, obstacle[0], obstacle[1], d_green)


index = find_closest_ball(balls, bot_loc)

# FOR TESTING PURPOSES, MODIFY THIS INDEX TO CHANGE WHICH BALL TO SEARCH FOR
index = 2
draw_line(bot_loc, balls[index], d_red)
angle = line_angle(bot_loc, balls[index])

print "The angle is: ", angle

def findPath(last_pt, bot_loc, next_pt, obstacles):
	intersections = []
	POI = []
	checked_obs = {0: False, 1: False, 2: False, 3: False}
	

	intersections = checkIntersections(bot_loc, balls[index], obstacles, intersections)
	print intersections

	if len(intersections) == 0:
		next_pt = balls[index]

	for intersection in intersections:
		checked_obs[intersection] = True
		POI = getPOI(bot_loc, balls[index], obstacles[intersection], POI)

	print "POI: ", POI

	while next_pt == (0,0) and len(POI) > 0:
		print "popped again"
		test_pt = POI.pop(0)
		for path in travelled_paths:
			if test_pt[0] > path[0][0] and test_pt[0] < path[0][1] and test_pt[1] > path[1][0] and test_pt[1] < path[1][1]:
				print "THIS POINT HAS ALREADY BEEN VISITED"
				test_pt = (0,0)
				break # this point has already been visited, try another one
		if test_pt == (0,0):
			continue
		intersections = []
		intersections = checkIntersections(bot_loc, test_pt, obstacles, intersections)
		if len(intersections) == 0:
			next_pt = test_pt
			print "We're done! The next point is: ", next_pt
		else:
			for intersection in intersections:
			    if checked_obs[intersection] == False:
					print "another obstacle was encountered, adding more POIs"
					checked_obs[intersection] == False
					POI = getPOI(bot_loc, balls[index], obstacles[intersection], POI)

	draw_circle(4, next_pt[0], next_pt[1], d_red)
	robotTravel(bot_dir, bot_loc, next_pt)
	return next_pt

# returns a boolean indicating whether or not the robot has reached it's destination
def check_dest(bot_loc, bot_dest):
	return distance_between_points(bot_loc, bot_dest) < rover_width


next_pt = (0,0)
last_pt = (0,0)

while not check_dest(bot_loc,balls[index]):
	next_pt = findPath(last_pt, bot_loc, next_pt, obstacles)
	travelled_paths.append(((min(bot_loc[0],next_pt[0])-rover_width/2, max(bot_loc[0],next_pt[0]) + rover_width/2), \
		(min(bot_loc[1],next_pt[1]) - rover_width/2, max(bot_loc[1],next_pt[1]) + rover_width/2)))
	last_pt = bot_loc
	bot_loc = next_pt
	next_pt = (0, 0)



#print intersections
#while len(intersections) > 0:
#	intersection = intersections.pop()
#	draw_line(bot_loc, intersection, black)

#	bot_loc = intersection
#	intersections = checkIntersections(bot_loc, balls[index], obstacles, intersections)
#	print intersections

#draw_line(bot_loc, balls[index], black)
#draw_grid(image)
cv2.imshow('Image', image)

cv.WaitKey()