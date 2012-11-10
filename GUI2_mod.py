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


#The panel containing the webcam video
class CvDisplayPanel(wx.Panel):
    TIMER_PLAY_ID = 101 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.capture1 = cv.CaptureFromCAM(0)
        self.capture2 = cv.CaptureFromCAM(1)

        # reduce flickering
        self.SetCompositeMode(True)

        mask = self.CombineCaptures()
        
        # display image
        self.bmp = wx.BitmapFromBuffer(mask.width, mask.height, mask.tostring())
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

        try:
            warp1 = processor.perspective_transform(orig1, warp_coord)
        except:
            warp1 = orig1

        try:
            warp2 = processor.perspective_transform(orig2, warp_coord2)
        except:
            warp2 = orig2

        mask = cv.CreateImage((800,800), cv.IPL_DEPTH_8U, 3)
        cv.SetImageROI(mask, (0, 0, 800, 400))

        test1 = cv.CreateImage((800,400), cv.IPL_DEPTH_8U, 3)
        cv.Resize(warp1, test1)

        cv.Copy(test1, mask)

        cv.ResetImageROI(mask)
        cv.SetImageROI(mask, (0, 400, 800, 400))
        test2 = cv.CreateImage((800,400), cv.IPL_DEPTH_8U, 3)
        cv.Resize(warp2, test2)
        cv.Copy(test2, mask)

        cv.ResetImageROI(mask)

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
    
    # get image
    def ImagePro(self,capture):
        orig = cv.QueryFrame(capture)
        
        # filter for all yellow and blue - everything else is black
        #processed = processor.colorFilterCombine(orig, "yellow", "blue" ,s)
        
        # Some processing and smoothing for easier circle detection
        #cv.Canny(processed, processed, 5, 70, 3)
        #cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)

        # Find&Draw circles
        #processor.find_circles(processed, storage, 100)
        # robot location detection
        #combined = processor.robot_tracking(orig, squares)

        #processor.draw_circles(storage, orig)
        
        #mask = cv.CreateImage((400,300), cv.IPL_DEPTH_8U, 3)
        #cv.Resize(orig,mask)
        #return mask
        return orig

    # update image each frame
    def onNextFrame(self, evt):
        mask = self.CombineCaptures()

        if mask:
            cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(mask.tostring()) # update the bitmap to the current frame
            self.Refresh() # display the current frame
        evt.Skip()


class Cameras(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1230,1000))
        
        self.display = wx.TextCtrl(self, -1, "YOLO",  style=wx.TE_MULTILINE, size=(400,300))
        box = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.GridSizer(2, 3, 1, 1)
        buttons.AddMany([(wx.Button(self, 1, 'Stop') , 0, wx.EXPAND),
                        (wx.Button(self, 2, 'Up') , 0, wx.EXPAND),
                        (wx.Button(self, 3, 'Start') , 0, wx.EXPAND),
                        (wx.Button(self, 4, 'Left') , 0, wx.EXPAND),
                        (wx.Button(self, 5, 'Down') , 0, wx.EXPAND),
                        (wx.Button(self, 6, 'Right') , 0, wx.EXPAND)])
        box.Add(self.display, 1, wx.EXPAND)
        box.Add(buttons, 1, wx.EXPAND)

        right = wx.BoxSizer(wx.VERTICAL)
        display1 = CvDisplayPanel(self)
        #display2 = CvDisplayPanel(self)
        right.Add(display1, 1, wx.ALL , 0)
        #right.Add(display2, 1, wx.ALL , 0)

        left = wx.BoxSizer(wx.HORIZONTAL)
        #left.Add(CvDisplayPanel(self, capture1), 1, wx.ALL, 0)

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

        self.CreateStatusBar() # A Statusbar in the bottom of the window

        filemenu= wx.Menu() # Setting up the menu.

        # wx.ID_EXIT is a standard ID provided by wxWidgets.
        filemenu.AppendSeparator()
        menuExit=filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # events for the menu bar
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        menuBar = wx.MenuBar() # Creating the menubar.
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    def OnExit(self,evt):
        self.Close(True)  # Close the frame.

    def OnStop(self, event):
        self.display.WriteText("Sending Command: Stop\n")
        #print('Com Port: ' + self.ser.portstr + ' closed')
        try: 
            self.ser.close
            self.display.WriteText("Com Port: " + self.ser.portstr + " closed\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Stop Failed.\n")   


    def OnUp(self, event):
        self.display.WriteText("Sending Command: Up\n")
        try: 
            self.ser.write('w')
            self.display.WriteText("Command: Up Sent.\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Up Failed.\n")

    def OnStart(self, event):
        self.display.WriteText("Sending Command: Start\n")
        try: 
            self.ser = serial.Serial(
                port='\\.\COM7',
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.display.WriteText("Com Port: " + self.ser.portstr + " opened!\n")
            return self.ser

        except serial.SerialException:
            self.display.WriteText("Com Port Connection Failed.\n")
            self.ser = 0
            return self.ser

    def OnLeft(self, event):
        self.display.WriteText("Sending Command: Left\n")
        try: 
            self.ser.write('a')
            self.display.WriteText("Command: Left Sent.\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Left Failed.\n")

    def OnDown(self, event):
        self.display.WriteText("Sending Command: Down\n")
        try: 
            self.ser.write('s')
            self.display.WriteText("Command: Down Sent.\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Down Failed.\n")

    def OnRight(self, event):
        self.display.WriteText("Sending Command: Right\n")
        try: 
            self.ser.write('d')
            self.display.WriteText("Command: Right Sent.\n")

        except serial.SerialException:
            self.display.WriteText("Com Port Error.")

        except AttributeError:
            self.display.WriteText("Command: Right Failed.\n")

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
    
    cv.SetMouseCallback("calibrate", on_mouse, 0);

    cv.PutText(orig, cur_pos + " " + str(x_co) + "," + str(y_co),(x_co,y_co), font, (55, 25, 255))
    cv.ShowImage('calibrate', orig)
    
    if cv.WaitKey(10) == 27:
        break

cv.DestroyWindow("calibrate")

def on_mouse(event,x,y,flag,param):
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
    
    cv.SetMouseCallback("calibrate",on_mouse, 0);

    cv.PutText(orig2, cur_pos + " " + str(x_co) + "," + str(y_co),(x_co,y_co), font, (55, 25, 255))
    cv.ShowImage('calibrate', orig2)
    
    if cv.WaitKey(10) == 27:
        break

cv.DestroyWindow("calibrate")
#processor.draw_grid(grid)

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = Cameras(None, "Cameras") # A Frame is a top-level window.
frame.Show(True)     # Show the frame.

#frame2 = Control(None, "Control") # A Frame is a top-level window.
#frame2.Show(True) 
app.MainLoop()