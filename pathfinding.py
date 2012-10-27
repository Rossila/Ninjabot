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

# define radii
# make the obstacle_radius + rover_width 2/sqrt(2) times larger than it needs to be 
ball_radius = 18
obstacle_radius = 28
rover_width = 50

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
		for obstacle in obstacles:
			obs_proj1 = (int(obstacle[0] + x_dspl), int(obstacle[1] + y_dspl))
			obs_proj2 = (int(obstacle[0] + -1*x_dspl), int(obstacle[1] + -1*y_dspl))
			draw_line(obs_proj1, obs_proj2, d_blue)
			print "obstacle", obstacle
			print "obs_proj1", obs_proj1
			if intersect(bot_loc, bot_dest, obs_proj1, obstacle):
				print "intersection found at", obs_proj1
				intersections.append(obs_proj1)
			elif intersect(bot_loc, bot_dest, obs_proj2, obstacle):
				print "intersection found at", obs_proj2
				intersections.append(obs_proj2)
		#print intersections
		return intersections


	
	return checkObstacles(bot_loc, bot_dest, obstacles, intersections)

# Initialize Coordinates
bot_loc = (image.shape[1]/2, 0)
bot_dir = 90
balls = [(449, 620), (600, 200), (250, 500), (199, 100)]
obstacles = [(400, 453), (274, 114), (588, 621)]

# Draw the balls and obstacles
for ball in balls:
	draw_circle(ball_radius, ball[0], ball[1], d_red)

for obstacle in obstacles:
	draw_circle(obstacle_radius, obstacle[0], obstacle[1], d_green)


index = find_closest_ball(balls, bot_loc)
#index = 2
draw_line(bot_loc, balls[index], d_red)
angle = line_angle(bot_loc, balls[index])

print "The angle is: ", angle

intersections = []

intersections = checkIntersections(bot_loc, balls[index], obstacles, intersections)

print intersections
while len(intersections) > 0:
	intersection = intersections.pop()
	draw_line(bot_loc, intersection, black)

	bot_loc = intersection
	intersections = checkIntersections(bot_loc, balls[index], obstacles, intersections)
	print intersections

draw_line(bot_loc, balls[index], black)
draw_grid(image)
cv2.imshow('Image', image)

cv.WaitKey()