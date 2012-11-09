#!/usr/bin/python
import cv2
import cv2.cv as cv
import numpy as np
import math
import fractions

# locations of balls and obstacles
balls = [(449, 620), (600, 200), (250, 500), (159, 100)]
obstacles = [(400, 453), (286, 114), (290, 190), (588, 621)]

# define colors
d_red = cv.RGB(150, 55, 65)
d_green = cv.RGB(55, 150, 65)
d_blue = cv.RGB(55, 65, 150)
l_red = cv.RGB(250, 200, 200)
black = cv.RGB(100, 100, 100)
d_purple = cv.RGB(150, 55, 150)

# a list of ranges of x & y to indicate previously travelled paths
travelled_paths = []

ball_radius = 18
obstacle_radius = 33
rover_width = 50

# the radius to avoid is the sum of the obstacle_radius and rover_width.
# though it should be rover_width/2, we'll use rover_width to be on the safe side
avoid_radius = obstacle_radius + rover_width

TRAV_UNIT = 40
TURN_ANGLE = 5

FIELD_WIDTH = 794
FIELD_HEIGHT = 794

image = cv2.imread('empty.jpg')

# will fix this later
class Point:
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self[0] = x
		self[1] = y

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

# draw the line
# return the end coordinates
def draw_line_polar(start, angle, distance):
	# convert angle to radians
	angle = float(angle)/180 * math.pi
	
	print "angle in radians: ", angle
	# x = rcos(theta)
	# y = rsin(theta)
	x = distance * math.cos(angle)
	y = distance * math.sin(angle)

	end = (int(start[0] + x), int(start[1] + y))

	# draw_line(start, end, d_purple)
	cv2.line(image, start, end, d_purple, thickness = 2, lineType=8, shift=0)

	return end # return the end point

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

# checks if the path bot_loc to bot_dest intersects with any obstacles
# Returns: appends the index of intersecting obstacles in intersections list
def checkIntersections(bot_loc, bot_dest, obstacles, intersections):
	def findConstants(bot_loc, bot_dest, distance):
		# find x_dspl & y_dspl s.t.
		# y_dspl/x_dspl = slope and x_dspl^2 + y_dspl^2 = distance^2
		# x_dspl and y_dspl are perpendicular to the line segment formed by bot_loc and bot_dest
		x_dspl = 0
		y_dspl = 0

		# x and y are swapped and y is negated to account for the perpendicular line
		diff_y = bot_dest[0] - bot_loc[0]
		diff_x = - bot_dest[1] + bot_loc[1]

		#we're done! close enough, don't do anything more
		if diff_x <= 10 and diff_x >= -10 and diff_y <= 10 and diff_y >= -5: 
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

	x_dspl, y_dspl = findConstants(bot_loc, bot_dest, avoid_radius - 20) # since the avoid_radius is exaggerated, can make it slightly more lenient when checking for intersections
	for index, obstacle in enumerate(obstacles):
		obs_proj1 = (int(obstacle[0] + x_dspl), int(obstacle[1] + y_dspl)) # there are two projections coming out of the obstacle
		obs_proj2 = (int(obstacle[0] + -1*x_dspl), int(obstacle[1] + -1*y_dspl)) # one in each direction
		draw_line(obs_proj1, obs_proj2, d_blue)
		# if the obs_proj intersects with the path or the distance between the destination and the obstacle center is less than the radius
		# of the obstacle - there is a collision and we need to record this obstacle index
		if intersect(bot_loc, bot_dest, obs_proj1, obs_proj2) or distance_between_points(bot_dest, obstacle) < avoid_radius:
			intersections.append(index) #append the index of the intersecting obstacle to intersections list
	return intersections

# get the point of interests around the inputted obstacle
# these points will be possible destinations from the rovers current location
# all of these paths will be tangent to the obstacle and within the boundaries of the field
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
		side = avoid_radius
		diff_theta = math.asin(side/float(hypotenuse))
		theta = math.atan((obstacle[1] - float(bot_loc[1]))/(obstacle[0] - float(bot_loc[0])))
		slope1 = getSlope(theta + diff_theta)
		print "slope 1: ", slope1

		#y = (slope)x + (displacement)
		displacement1 = bot_loc[1] - slope1 * bot_loc[0]

		slope2 = getSlope(theta - diff_theta)
		print "slope 2: ", slope2
		#y = (slope)x + (displacement)
		displacement2 = bot_loc[1] - slope2 * bot_loc[0]

		draw_circle(side, obstacle[0], obstacle[1], d_red)
		return slope1, displacement1, slope2, displacement2 

	def checkValidPOI(x, y, obstacle):
		# check that the distance between the tangent point and the cent of the obstacle is approximately the radius
		return int(distance_between_points((x, y), obstacle)) - obstacle_radius - rover_width <= 2 \
			and x > rover_width and y > rover_width and x < FIELD_WIDTH - rover_width and y < FIELD_HEIGHT - rover_width 
			# check that x and y are within the field boundaries

	# first find the tangent point on the circle

	# find slope and displacement (y = ax + b) of the two possible tangent lines
	aslope1, adispl1, aslope2, adispl2 = getTangent(bot_loc, obstacle)
	
	# find the slope and displacement of the radii perpendicular to the tangent lines
	bslope1 = -1 / float(aslope1)
	bslope2 = -1 / float(aslope2)

	bdispl1 = obstacle[1] - bslope1 * obstacle[0]
	bdispl2 = obstacle[1] - bslope2 * obstacle[0]

	x1 = (bdispl1 - adispl1)/(aslope1 - bslope1)
	y1 = bslope1 * x1 + bdispl1
	if checkValidPOI(x1, y1, obstacle):
		draw_circle(4, int(x1), int(y1), black)
		# the point of interest is a distance avoid_radius away from the tangent point
		# this way the next point of interest could be a 90 degree turn, avoiding this obstacle
		(x1, y1) = getEndPt(bot_loc, (x1, y1), avoid_radius)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x1), int(y1)))

	x2 = (bdispl2 - adispl2)/(aslope2 - bslope2)
	y2 = bslope2 * x2 + bdispl2
	if checkValidPOI(x2, y2, obstacle):
		draw_circle(4, int(x2), int(y2), black)
		(x2, y2) = getEndPt(bot_loc, (x2, y2), avoid_radius)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x2), int(y2)))

	x3 = (bdispl1 - adispl2)/(aslope2 - bslope1)
	y3 = bslope1 * x3 + bdispl1
	if checkValidPOI(x3, y3, obstacle):
		draw_circle(4, int(x3), int(y3), black)
		(x3, y3) = getEndPt(bot_loc, (x3, y3), avoid_radius)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x3), int(y3)))

	x4 = (bdispl2 - adispl1)/(aslope1 - bslope2)
	y4 = bslope2 * x4 + bdispl2
	if checkValidPOI(x4, y4, obstacle):
		draw_circle(4, int(x4), int(y4), black)
		(x4, y4) = getEndPt(bot_loc, (x4, y4), avoid_radius)
		#draw_circle(4, int(x1), int(y1), d_purple)
		POI.append((int(x4), int(y4)))

	return POI

# Since the robot won't be able to make exact angle turns,
# this function draws a purple line to estimate where the robot would be
# if it could only turn TURN_ANGLE and travel TRAV_UNIT
def robotTravel(bot_dir, bot_loc, next_pt):
	angle = line_angle(bot_loc, next_pt)
	# want turn to be between -180 to 180 degrees,
	# neg degrees are ccw
	# pos degrees are cw
	turn = angle - bot_dir
	# get the closest value divisible by TURN_ANGLE
	turn = int(turn/TURN_ANGLE) * TURN_ANGLE
	distance = distance_between_points(bot_loc, next_pt)
	# get the closest value divisible by TRAV_UNIT
	distance = int(distance/TRAV_UNIT + 0.50) * TRAV_UNIT

	angle = int(bot_dir + turn)

	print "bot_loc: ", bot_loc, "angle: ", angle, "distance: ", distance
	print "ROBOT DIRECTIONS: turn", turn, "move forward", distance
	return draw_line_polar(bot_loc, angle, distance) # return the end point

# Finds the next point that the robot should travel to
# Creates a list of Point of interests and finds one that is possible
def findPath(bot_loc, next_pt, obstacles, bot_dest):
	intersections = [] # will hold the indexes of obstacles that the path intersects with
	POI = [] # the list of point of interests, the next point will be chosen from here
	checked_obs = {0: False, 1: False, 2: False, 3: False} # to prevent us from checking for POI on the same obstacle, use a boolean dictionary
	
	# populate the list of intersections with obstacles in the way of a direct path from the robots current location to the destination
	intersections = checkIntersections(bot_loc, bot_dest, obstacles, intersections)
	print intersections

	# if there are no intersections, this path is fine and the next_pt is the robot's destination
	if len(intersections) == 0:
		next_pt = bot_dest

	# if there are intersections, populate the POI list with POI's around that obstacle
	for intersection in intersections:
		checked_obs[intersection] = True # update the boolean dictionary so we don't check this obstacle again
		POI = getPOI(bot_loc, balls[index], obstacles[intersection], POI)

	print "POI: ", POI

	# iterate until a next point is found or there are no more possible POI's
	while next_pt == (0,0) and len(POI) > 0:
		test_pt = POI.pop(0)
		# check to make sure we haven't travelled along this path already (avoid the robot going in loops)
		for path in travelled_paths:
			if test_pt[0] > path[0][0] and test_pt[0] < path[0][1] and test_pt[1] > path[1][0] and test_pt[1] < path[1][1]:
				print "This point:", test_pt, "has already been visited"
				test_pt = (0,0)
				break
		if test_pt == (0,0): # this point has already been visited, try another one
			continue

		# repopulate the intersections list with respect to the new path from current location to next point
		intersections = []
		intersections = checkIntersections(bot_loc, test_pt, obstacles, intersections)
		print "intersections: ", intersections, "for travel path to: ", test_pt
		draw_circle(2, test_pt[0], test_pt[1], d_red)
		if len(intersections) == 0: # if there are no intersections, this next point is a winner!
			next_pt = test_pt
			print "We're done! The next point is: ", next_pt
		else:
			for intersection in intersections:
			    if checked_obs[intersection] == False: # we don't want to check POI's twice
					print "Another obstacle with index:", intersection," was encountered, adding more POIs"
					checked_obs[intersection] = True
					POI = getPOI(bot_loc, bot_dest, obstacles[intersection], POI)
					print "POI updated: ", POI

	draw_circle(4, next_pt[0], next_pt[1], d_red)

	# estimates where the robot will actually go
	next_pt = robotTravel(bot_dir, bot_loc, next_pt) # adjust the path
	return next_pt

# returns a boolean indicating whether or not the robot has reached it's destination
def check_dest(bot_loc, bot_dest):
	return distance_between_points(bot_loc, bot_dest) < rover_width


# Initialize Coordinates
bot_loc = (image.shape[1]/2, rover_width)
bot_dir = 90
next_pt = (0,0)

# Draw the balls and obstacles
for ball in balls:
	draw_circle(ball_radius, ball[0], ball[1], d_red)

for obstacle in obstacles:
	draw_circle(obstacle_radius, obstacle[0], obstacle[1], d_green)


index = find_closest_ball(balls, bot_loc)
# FOR TESTING PURPOSES, MODIFY THIS INDEX TO CHANGE WHICH BALL TO SEARCH FOR
index = 2

# rinse and repeat until the robot reaches its destination
while not check_dest(bot_loc,balls[index]):
	next_pt = findPath(bot_loc, next_pt, obstacles, balls[index])

	if next_pt == (0,0): # a next point wasn't found
		print "No next_pt was found, debug time"
		break;

	# append this path to travelled_paths list so we don't ever go in a loop
	travelled_paths.append(((min(bot_loc[0],next_pt[0])-rover_width/2, max(bot_loc[0],next_pt[0]) + rover_width/2), \
		(min(bot_loc[1],next_pt[1]) - rover_width/2, max(bot_loc[1],next_pt[1]) + rover_width/2)))

	bot_loc = next_pt
	next_pt = (0, 0)

#draw_grid(image)
cv2.imshow('Image', image)

cv.WaitKey()