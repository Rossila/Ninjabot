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
		print "distance index: ", index, "distance: ", dist
		if dist < shortest_dist:
			shortest_dist = dist
			min_index = index

	return min_index

# returns true if the line segment from ln1_start to ln1_end
# intersects with the line segment from ln2_start to ln2_end
def intersect(ln1_start, ln1_end, ln2_start, ln2_end):
	def ccw(A,B,C): # returns true if ABC are in ccw order, false otherwise
		return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
	
	return ccw(ln1_start,ln2_start,ln2_end) == ccw(ln1_end,ln2_start,ln2_end) or \
		ccw(ln1_start,ln1_end,ln2_start) == ccw(ln1_start,ln1_end,ln2_end)

def checkIntersections(bot_loc, bot_dest, obstacles):
	# find the slope of the robot's current tragectory
	def getSlope(bot_loc, bot_dest):
		slope = fractions.Fraction(bot_dest[1] - bot_loc[1],bot_dest[0] - bot_loc[0])
		#print slope
		return slope

	def findConstant(slope, distance):
		# (ax)/(ay) find c s.t. (ax)^2 + (ay)^2 = distance^2
		# ax and ay will be the x and y displacement

		a = math.sqrt(pow(distance, 2)/float(pow(slope.numerator,2) + pow(slope.denominator,2)))
		#print a
		return a


	# returns the two end points of a parallel line segment (@distance) away from the original line
	def getParallelLine(ln1_start, ln1_end, distance, dir):
		ln2_start = (0,0)
		ln2_end = (0,0)

		perpSlope = -1/(getSlope(bot_loc, bot_dest))
		#print perpSlope

		a = findConstant(perpSlope, distance)
		
		if dir == "bottom":
			a = a * -1
		ln2_start = (int(ln1_start[0] + a*perpSlope.denominator), int(ln1_start[1] + a*perpSlope.numerator))
		ln2_end = (int(ln1_end[0] + a*perpSlope.denominator), int(ln1_end[1] + a*perpSlope.numerator))

		return ln2_start, ln2_end

	def checkObstacles(bot_loc, bot_dest, obstacles):
		perpSlope = -1/(getSlope(bot_loc, bot_dest))
		intersections = []
		
		ln2_start_top, ln2_end_top = getParallelLine(bot_loc, bot_dest, 50, "top")
		ln2_start_bot, ln2_end_bot = getParallelLine(bot_loc, bot_dest, 50, "bottom")
		
		draw_line(ln2_start_top, ln2_end_top, d_red)
		draw_line(ln2_start_bot, ln2_end_bot, d_red)

		a = findConstant(perpSlope, obstacle_radius + rover_width)
		for obstacle in obstacles:
			obs_proj1 = (obstacle[0] + int(a*perpSlope.denominator), obstacle[1] + int(a*perpSlope.numerator))
			obs_proj2 = (obstacle[0] + int(-1*a*perpSlope.denominator), obstacle[1] + int(-1*a*perpSlope.numerator))
			draw_line(obs_proj1, obs_proj2, d_blue)

			if not intersect(bot_loc, bot_dest, obs_proj1, obs_proj2):
				intersections.append((obs_proj1, obs_proj2))
		print intersections
		return intersections


	
	return checkObstacles(bot_loc, bot_dest, obstacles)






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

draw_line(bot_loc, balls[index], d_red)
angle = line_angle(bot_loc, balls[index])

print angle

intersections = checkIntersections(bot_loc, balls[index], obstacles)
print len(intersections)
while len(intersections) > 0:
	intersection = intersections.pop()
	draw_line(bot_loc, intersection[0], l_red)
	#intersections = checkIntersections(bot_loc, intersection[0], l_red)

	draw_line(intersection[0], balls[index], l_red)
	draw_line(bot_loc, intersection[1], l_red)
	draw_line(intersection[1], balls[index], l_red)

draw_grid(image)
cv2.imshow('Image', image)

cv.WaitKey()