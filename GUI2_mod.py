'''How to integrate openCV and wxpython.

This program loads an image file using openCV, converts it to a format
which wxpython can handle and displays the resulting image in a
wx.Frame.'''


import wx
import cv2.cv as cv
import cv2
import win32api 
import win32con 
import processor
import numpy as np
import serial
import path_tools
import time
import math
#The panel containing the webcam video
class CvDisplayPanel(wx.Panel):
    TIMER_PLAY_ID = 101 
    CHECK_INDEX = 0

    balls = []
    obstacles = []
    veriBalls = []
    veriObstacles = []

    next_pt = (0,0)
    bot_loc = (0,0)
    bot_dir = 90

    mask = None

    sync = 0

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.capture1 = cv.CaptureFromCAM(0)
        self.capture2 = cv.CaptureFromCAM(1)

        # reduce flickering
        self.SetCompositeMode(True)

        self.mask = self.CombineCaptures()
        
        # display image
        self.bmp = wx.BitmapFromBuffer(self.mask.width, self.mask.height, self.mask.tostring())
        sbmp = wx.StaticBitmap(self, -1, bitmap=self.bmp) # Display the resulting image

        # set up event timer to update image
        self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID) 
        wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onNextFrame) 
        fps = cv.GetCaptureProperty(capture1, cv.CV_CAP_PROP_FPS) 

        if fps!=0: 
            self.playTimer.Start(1000/fps) # every X ms 
        else: 
            self.playTimer.Start(1000/15) # assuming 15 fps 

    #combine webcam images
    def CombineCaptures(self):
        # loaded the two images from the webcams
        orig1 = self.ImagePro(self.capture1)
        orig2 = self.ImagePro(self.capture2)

        # try to warp if possible, otherwise use default images from webcam
        try:
            warp1 = processor.perspective_transform(orig1, warp_coord)
        except:
            warp1 = orig1

        try:
            warp2 = processor.perspective_transform(orig2, warp_coord2)
        except:
            warp2 = orig2

        # We will combine the two webcam images into a 800x800 image
        mask = cv.CreateImage((800,800), cv.IPL_DEPTH_8U, 3)

        cv.SetImageROI(mask, (0, 0, 800, 400))

        # resize warp1 to be 800 x 400 (half of the complete image) copy resized
        # image into temp1
        temp1 = cv.CreateImage((800,400), cv.IPL_DEPTH_8U, 3)
        cv.Resize(warp1, temp1)

        # copy image temp1 to the bottom half of mask
        cv.Copy(temp1, mask)
        cv.ResetImageROI(mask)

        cv.SetImageROI(mask, (0, 400, 800, 400))
        
        temp2 = cv.CreateImage((800,400), cv.IPL_DEPTH_8U, 3)
        cv.Resize(warp2, temp2)
        
        # copy image temp2 to the upper half of mask
        cv.Copy(temp2, mask)
        cv.ResetImageROI(mask) # reset image ROI

        
        #cv.ShowImage("added together!", mask)
        #cv.CvtColor(mask, mask, cv.CV_BGR2RGB)

        return mask

    #magic to stop the flickering
    def SetCompositeMode(self, on=True): 
        exstyle = win32api.GetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE) 
        if on: 
            exstyle |= win32con.WS_EX_COMPOSITED 
        else: 
            exstyle &= ~win32con.WS_EX_COMPOSITED 
        win32api.SetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE, exstyle) 
    
    def verify_circles(self, unsorted_list):
        def key(x, y):
            return x/10 * 100 + y/10

        exist_nodes = {}
        counted_list = []
        sorted_list = []

        for node in unsorted_list:
            try:
                exist_nodes[key(node[0], node[1])] = exist_nodes[key(node[0], node[1])] + 1
                if exist_nodes[key(node[0], node[1])] >= 3:
                    sorted_list.append(node)
                    exist_nodes[key(node[0], node[1])] = -10
                    for x in range(1,5):
                        exist_nodes[key(node[0] - x*10, node[1] - x*10)] = -10
                        exist_nodes[key(node[0] - x*10, node[1] + x*10)] = -10
                        exist_nodes[key(node[0] + x*10, node[1] - x*10)] = -10
                        exist_nodes[key(node[0] + x*10, node[1] + x*10)] = -10
            except:
                exist_nodes[key(node[0], node[1])] = 1
                for x in range(1,4):
                    exist_nodes[key(node[0] - x*10, node[1] - x*10)] = 1
                    exist_nodes[key(node[0] - x*10, node[1] + x*10)] = 1
                    exist_nodes[key(node[0] + x*10, node[1] - x*10)] = 1
                    exist_nodes[key(node[0] + x*10, node[1] + x*10)] = 1

        #print "exist_nodes: ", exist_nodes
        #print "sorted_list: ", sorted_list

        return sorted_list
    
    def findCircles(self, mask):
        # filter for all yellow and blue - everything else is black
        processed = processor.colorFilterCombine(mask, "yellow", "yellow" ,s)
        
        # Some processing and smoothing for easier circle detection
        cv.Canny(processed, processed, 5, 70, 3)
        cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)

        cv.ShowImage("processed", processed)
        
        storage = cv.CreateMat(mask.width, 1, cv.CV_32FC3)

        # Find&Draw circles
        processor.find_circles(processed, storage, 100)
        # robot location detection
        tail_coord, head_coord = processor.robot_tracking(mask, squares)
        #print "HEAD AND TAIL: ", head_coord, tail_coord
        self.bot_loc = ((head_coord[0] + tail_coord[0])/2,(head_coord[1] + tail_coord[1])/2)
        self.bot_dir = path_tools.line_angle(head_coord, tail_coord)
        cur_balls, cur_obstacles = processor.sort_circles(storage)

        if cur_balls == None or cur_obstacles == None:
            return mask

        for ball in cur_balls:
            self.balls.append(ball)

        for obstacle in cur_obstacles:
            self.obstacles.append(obstacle)
        
        #cv.ShowImage("did it find circles?", mask)

        if self.CHECK_INDEX == 10: # circle finding is compared over the last 5 frames
            self.CHECK_INDEX = 0

            self.veriBalls = self.verify_circles(self.balls)
            self.veriObstacles = self.verify_circles(self.obstacles)

            processor.draw_circles(self.veriBalls, self.veriObstacles, mask)

            self.next_pt, turn, distance, ball_loc = path_tools.PathFind(self.bot_dir, self.bot_loc, self.veriBalls, self.veriObstacles)
            print "next_pt: ", self.next_pt

            cv.Circle(mask, (self.next_pt[0], self.next_pt[1]), 13,cv.RGB(150, 55, 150), 3, 8, 0)
            
            self.sync = self.sync + 1 # sync is a variable between 0 and 50 used to ensure path finding waits for the image processing
            if self.sync > 50:
                self.sync = 0
            
            self.balls = []
            self.obstacles = []
        else:
            self.CHECK_INDEX = self.CHECK_INDEX + 1
            processor.draw_circles(self.veriBalls, self.veriObstacles, mask)

            #bot_loc = (800/2, 25)
            cv.Line(mask, (self.bot_loc[0], self.bot_loc[1]),(self.next_pt[0], self.next_pt[1]), cv.RGB(150, 55, 150), thickness=2, lineType=8, shift=0)

            cv.Circle(mask, (self.next_pt[0], self.next_pt[1]), 13, cv.RGB(150, 55, 150), 3, 8, 0)

        return mask

    # get image
    def ImagePro(self,capture):
        orig = cv.QueryFrame(capture)

        return orig

    # update image each frame
    def onNextFrame(self, evt):
        self.mask = self.CombineCaptures() # get combined image from webcams

        self.mask = self.findCircles(self.mask) # find & draw circles using image processing

        if self.mask:
            cv.CvtColor(self.mask, self.mask, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(self.mask.tostring()) # update the bitmap to the current frame
            self.Refresh() # display the current frame
        evt.Skip()


class Cameras(wx.Frame):
    """ We simply derive a new class of Frame. """
    firstAngle = 0
    secondAngle = 0
    firstStraight = 0
    secondStraight = 0
    display1 = None
    next_pt = (0,0)
    sync = 0 # a variable between 0 and 50 used to ensure pathfinding waits for image processing
    state = -1 #-1: auto not started, 0: find next position, #1: move to next position, #2: catch ball
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1600,800))
        
        self.display = wx.TextCtrl(self, -1, "YOLO",  style=wx.TE_MULTILINE, size=(200,150))
        box = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.GridSizer(3, 3, 1, 1)
        buttons.AddMany([(wx.Button(self, 1, 'Stop') , 0, wx.EXPAND),
                        (wx.Button(self, 2, 'Up') , 0, wx.EXPAND),
                        (wx.Button(self, 3, 'Start') , 0, wx.EXPAND),
                        (wx.Button(self, 4, 'Left') , 0, wx.EXPAND),
                        (wx.Button(self, 5, 'Down') , 0, wx.EXPAND),
                        (wx.Button(self, 6, 'Right') , 0, wx.EXPAND),
                        (wx.Button(self, 7, 'Warp') , 0, wx.EXPAND),
                        (wx.Button(self, 8, 'Auto') , 0, wx.EXPAND)])
        box.Add(self.display, 1, wx.EXPAND)
        box.Add(buttons, 1, wx.EXPAND)

        right = wx.BoxSizer(wx.VERTICAL)
        self.display1 = CvDisplayPanel(self)

        right.Add(self.display1, 1, wx.ALL , 0)

        left = wx.BoxSizer(wx.HORIZONTAL)
        
        left.Add(right, 1, wx.ALL, 0)

        left.Add(box, 1, wx.ALL, 0)
        self.SetSizer(left)
       
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.OnStop, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnUp, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnStart, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnLeft, id=4)
        self.Bind(wx.EVT_BUTTON, self.OnDown, id=5)
        self.Bind(wx.EVT_BUTTON, self.OnRight, id=6)
        self.Bind(wx.EVT_BUTTON, self.OnWarp, id=7)
        self.Bind(wx.EVT_BUTTON, self.onAuto, id=8)

        self.CreateStatusBar() # A Statusbar in the bottom of the window

        filemenu= wx.Menu() # Setting up the menu.

        # wx.ID_EXIT is a standard ID provided by wxWidgets.
        filemenu.AppendSeparator()
        menuExit=filemenu.Append(wx.ID_EXIT,"Exit"," Terminate the program")

        # events for the menu bar
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        menuBar = wx.MenuBar() # Creating the menubar.
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        TIMER_ID = 100
        self.timer = wx.Timer(self, TIMER_ID) 
        wx.EVT_TIMER(self, TIMER_ID, self.onNextFrame2)
        self.timer.Start(1000)

    def OnExit(self,evt):
        self.Close(True)  # Close the frame.

    def OnStop(self, event):
        self.display.WriteText("Sending Command: Stop\n")
        #print('Com Port: ' + self.ser.portstr + ' closed')
        try: 
            self.ser.write('h')
            self.ser.close
            self.display.WriteText("Com Port: " + self.ser.portstr + " closed\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Stop Failed.\n")  

        quit()


    def OnStart(self, event):
        self.display.WriteText("Sending Command: Start\n")
        try: 

            self.ser = serial.Serial(
                port='COM16',
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            
            
            self.display.WriteText("Com Port: " + self.ser.portstr + " opened!\n")
            return self.ser

        except serial.SerialException:
            self.display.WriteText("Com Port Connection Failed.\n")
            self.ser = 0
            return self.ser

    def onAuto(self, event):
        self.state = 0 

    def onNextFrame2(self, evt):
        print "CURRENT STATE: ", self.state

        if self.sync == self.display1.sync: # image processing hasnt't been updated, do not send any commands
            return
        else:
            self.sync = self.display1.sync
        if self.state == 0: # state 0 is find and send the command to move towards the closest ball
            self.next_pt, angle, distance, ball_loc = path_tools.PathFind(self.display1.bot_dir, self.display1.bot_loc, self.display1.veriBalls, self.display1.veriObstacles)
            self.state = 1 # state 1 indicates the robot is currently travelling to its next point
            a = self.turn(angle)
            a = self.move(int(distance*16))     #16 is the correct value
            if path_tools.check_dest(self.display1.bot_loc, ball_loc): # check if robot has reached a ball
                self.state = 2
            else:
                self.state = 0

            
    def turnAndMove(self, angle, distance):
        self.turn(angle)

    def OnUp(self, event):
        self.move(1000)
        """
        self.display.WriteText("Sending Command: Forward\n")
        try: 
            self.ser.write('f')
            self.ser.flush()
            self.display.WriteText("Command: Forward Command Sent.\n")
            time.sleep(0.05)
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            self.ser.flush()
            self.ser.write('5')            

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")
        except AttributeError:
            self.display.WriteText("Command: Forward Command Failed.\n")"""

    def OnDown(self, event):
        self.move(-1000)
        """
        self.display.WriteText("Sending Command: Backward\n")
        try: 
            self.ser.write('b')
            self.ser.flush()
            self.display.WriteText("Command: Backward Command Sent.\n")
            time.sleep(0.05)
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            self.ser.flush()
            self.ser.write('5')

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Backward Failed.\n")"""

    #returns two variables corresponding to the arduinos turn inputs
    #only use between 0 and 360 degrees, responds in 5 degree increments
    def convertTurn(self, angle):
        if (angle > 180):
            angle = 180
        self.secondAngle = int(math.floor(angle/50))
        self.firstAngle = int(math.floor((angle-50*self.secondAngle)/5))

    def convertStraight(self, distance):
        if (distance > 9900):
            distance = 9900
        self.secondStraight = int(math.floor(distance/1000))
        self.firstStraight = int(math.floor((distance-1000*self.secondStraight)/100))

    def move(self,distance):

        self.display.WriteText("Sending Command: Move " + str(distance) + "\n")
        try: 
            if(distance<=0):
                self.ser.write('b')
                distance = distance * -1
            else:
                self.ser.write('f')
            self.convertStraight(distance)
            self.ser.flush()
            self.display.WriteText("Command: Forward. 100: " + str(self.firstStraight) + " 1000: " + str(self.secondStraight))
            time.sleep(0.05)
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            self.ser.flush()
            time.sleep(0.05)
            self.ser.write(self.firstStraight)  #100 increments
            self.display.WriteText(a + "\n")
            self.ser.flush()
            time.sleep(0.05)
            self.ser.write(self.secondStraight) #1000 increments
            self.ser.flush()
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            time.sleep(0.05)
            self.ser.flush()
            return a
            """self.ser.flush()
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            self.ser.flush()
            return a            """

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")
        except AttributeError:
            self.display.WriteText("Command: Forward Command Failed.\n")

    def turn(self,angle):
        self.display.WriteText("Sending Command: Turn " + str(angle) + "\n")
        #convertTurn()
        try: 
            if(angle<=0):
                self.ser.write('l')
                angle = angle * -1
            else:
                self.ser.write('r')
            self.convertTurn(angle)
            self.ser.flush()
            self.display.WriteText("Command:Turn sent.\n")
            time.sleep(0.05)
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            self.ser.flush()
            self.ser.write(self.firstAngle) #0-9 X5degrees
            self.ser.flush()
            self.display.WriteText(a + "\n")
            time.sleep(0.05)
            self.ser.write(self.secondAngle) #0-9 X50degrees
            self.ser.flush()
            a = self.ser.read(20)
            self.display.WriteText(a + "\n")
            time.sleep(0.05)
            self.ser.flush()
            return a
           
        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Turn Failed.\n")

    def OnLeft(self, event):
        self.turn(-90)

    def OnRight(self, event):
        self.turn(90)
        
    def OnWarp(self,event):
        self.display.WriteText("Reseting Warp Perspective\n")
        global warp_coord
        global warp_coord2

        warp_coord = np.array([], np.float32)
        warp_coord2 = np.array([], np.float32)


        while len(warp_coord) < 4:
            if len(warp_coord) == 0:
                cur_pos = "top left"
            elif len(warp_coord) == 1:
                cur_pos = "top right"
            elif len(warp_coord) == 2:
                cur_pos = "bottom left"
            else:
                cur_pos = "bottom right"

            orig = cv.QueryFrame(capture1)
            
            cv.SetMouseCallback("calibrate_image1",on_mouse, 0);
            print "trying.."

            cv.PutText(orig, cur_pos + " " + str(x_co) + "," + str(y_co),(x_co,y_co), font, (55, 25, 255))
            cv.ShowImage('calibrate_image1', orig)
            
            if cv.WaitKey(10) == 27:
                break


        print warp_coord
        cv.DestroyWindow("calibrate_image1")

        while len(warp_coord2) < 4:
            if len(warp_coord2) == 0:
                cur_pos = "top left"
            elif len(warp_coord2) == 1:
                cur_pos = "top right"
            elif len(warp_coord2) == 2:
                cur_pos = "bottom left"
            else:
                cur_pos = "bottom right"

            orig2 = cv.QueryFrame(capture2)
            
            cv.SetMouseCallback("calibrate_image2",on_mouse2, 0);
            print "trying.."

            cv.PutText(orig2, cur_pos + " " + str(x_co) + "," + str(y_co),(x_co,y_co), font, (55, 25, 255))
            cv.ShowImage('calibrate_image2', orig2)
            
            if cv.WaitKey(10) == 27:
                break

        print warp_coord2
        cv.DestroyWindow("calibrate_image2")

capture1 = cv.CaptureFromCAM(0)
capture2 = cv.CaptureFromCAM(1)

orig = cv.QueryFrame(capture1)
orig2 = cv.QueryFrame(capture2)

processed = cv.CreateImage((orig.width,orig.height), cv.IPL_DEPTH_8U, 1)
processed2 = cv.CreateImage((orig2.width,orig2.height), cv.IPL_DEPTH_8U, 1)

grid = cv.CreateImage((orig.width*2,orig.height), cv.IPL_DEPTH_8U, 3)

warp = cv.CreateImage((orig.width*2,orig.height), cv.IPL_DEPTH_8U, 3)
storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
storage2 = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
s = []
squares = []

y_co = 0
x_co = 0
warp_coord = np.array([], np.float32)
warp_coord2 = np.array([], np.float32)

warp_coord = [[0,0],[orig.width, 0],[0, orig.height],[orig.width, orig.height]]

warp_coord2 = [[0,0],[orig2.width, 0],[0, orig2.height],[orig2.width, orig2.height]]

font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 1, 0, 2, 8)


def on_mouse(event,x,y,flag,param):
    global x_co
    global y_co
    global warp_coord


    if event == cv.CV_EVENT_LBUTTONDOWN:
        warp_coord = np.append(warp_coord, [x,y])
        warp_coord = np.reshape(warp_coord, [-1, 2])
    if(event==cv.CV_EVENT_MOUSEMOVE):
        x_co=x
        y_co=y
        #print "X: " + str(x)
        #print "Y: " + str(y)



def on_mouse2(event,x,y,flag,param):
    global x_co
    global y_co
    global warp_coord2
    

    if event == cv.CV_EVENT_LBUTTONDOWN:
        warp_coord2 = np.append(warp_coord2, [x,y])
        warp_coord2 = np.reshape(warp_coord2, [-1, 2])
    if(event==cv.CV_EVENT_MOUSEMOVE):
        x_co=x
        y_co=y
        #print "X: " + str(x)
        #print "Y: " + str(y)

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = Cameras(None, "Cameras") # A Frame is a top-level window.

frame.Show(True)     # Show the frame.

#frame2 = Control(None, "Control") # A Frame is a top-level window.
#frame2.Show(True) 
app.MainLoop()
