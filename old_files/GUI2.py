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

    def ImagePro(self,capture,orig,processed,storage,grid,squares):
        orig = cv.QueryFrame(capture)
        #cv.Normalize(orig)
        # filter for all yellow and blue - everything else is black
        processed = processor.colorFilterCombine(orig, "yellow", "blue" ,s)
        #robot = processor.colorFilterCombine(orig, "red", "green" ,s)
        
        # Some processing and smoothing for easier circle detection
        cv.Canny(processed, processed, 5, 70, 3)
        cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)
        #cv.Canny(robot, robot, 5, 70, 3)
        #cv.Smooth(robot, robot, cv.CV_GAUSSIAN, 7, 7)
        
        #cv.ShowImage('processed2', processed)
        
        # Find&Draw circles
        processor.find_circles(processed, storage, 100)

        #processor.find_circles(robot, storage2, 100)
        #if it is in the range of 1 to 9, we can try and recalibrate our filter
        #if 1 <= storage.rows < 10:
        #    s = autocalibrate(orig, storage)
            
        #print storage2

        combined = processor.robot_tracking(orig, squares)

        processor.draw_circles(storage, orig)
        #processor.draw_circles(storage2, orig)

        mask = cv.CreateImage((400,300), cv.IPL_DEPTH_8U, 3)
        cv.Resize(orig,mask)
        return mask


    TIMER_PLAY_ID = 101 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #magic to stop the flickering
        def SetCompositeMode(self, on=True): 
            exstyle = win32api.GetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE) 
            if on: 
                exstyle |= win32con.WS_EX_COMPOSITED 
            else: 
                exstyle &= ~win32con.WS_EX_COMPOSITED 
            win32api.SetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE, exstyle) 

        SetCompositeMode(self, True)

        #self.capture = cv.CaptureFromCAM(0) # turn on the webcam
        #img = ImagePro # Convert the raw image data to something wxpython can handle.
        #cv.CvtColor(img, img, cv.CV_BGR2RGB) # fix color distortions
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        #storage2 = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        mask = self.ImagePro(capture,orig,processed,storage,grid,squares)
        cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(mask.width, mask.height, mask.tostring())
        sbmp = wx.StaticBitmap(self, -1, bitmap=self.bmp) # Display the resulting image

        
        self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID) 
        wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onNextFrame) 
        fps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS) 

        if fps!=0: self.playTimer.Start(1000/fps) # every X ms 
        else: self.playTimer.Start(1000/15) # assuming 15 fps 

        #del(storage)
        #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)


    def onNextFrame(self, evt):
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        #storage2 = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        mask = self.ImagePro(capture,orig,processed,storage,grid,squares)
        #img = processed
        if mask:
            cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(mask.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()

class CvDisplayPanel2(wx.Panel):

    def ImagePro(self,capture,orig,processed,storage,grid,squares):
        orig = cv.QueryFrame(capture)
        #cv.Normalize(orig)
        # filter for all yellow and blue - everything else is black
        processed = processor.colorFilterCombine(orig, "yellow", "blue" ,s)
        
        # Some processing and smoothing for easier circle detection
        cv.Canny(processed, processed, 5, 70, 3)
        cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)
        
        #cv.ShowImage('processed2', processed)
        
        # Find&Draw circles
        processor.find_circles(processed, storage, 100)

        #if it is in the range of 1 to 9, we can try and recalibrate our filter
        #if 1 <= storage.rows < 10:
        #    s = autocalibrate(orig, storage)
            

        combined = processor.robot_tracking(orig, squares)

        processor.draw_circles(storage, orig)

        #warp = processor.update_grid(storage, orig, grid)


        # Delete and recreate the storage so it has the correct width
        #del(storage)
        #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        
        #cv.ShowImage('output', orig)

        #return processed
        #cv.ShowImage('grid', warp)

        #warp = perspective_transform(orig)
        #cv.ShowImage('warped', warp)
        #combined = processor.robot_tracking(orig, squares)

        mask = cv.CreateImage((400,300), cv.IPL_DEPTH_8U, 3)
        cv.Resize(orig,mask)
        return mask

    TIMER_PLAY_ID = 101 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #magic to stop the flickering
        def SetCompositeMode(self, on=True): 
            exstyle = win32api.GetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE) 
            if on: 
                exstyle |= win32con.WS_EX_COMPOSITED 
            else: 
                exstyle &= ~win32con.WS_EX_COMPOSITED 
            win32api.SetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE, exstyle) 

        SetCompositeMode(self, True)

        #self.capture = cv.CaptureFromCAM(0) # turn on the webcam
        #img = ImagePro # Convert the raw image data to something wxpython can handle.
        #cv.CvtColor(img, img, cv.CV_BGR2RGB) # fix color distortions
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        mask = self.ImagePro(capture2,orig2,processed2,storage,grid,squares)
        cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(mask.width, mask.height, mask.tostring())
        sbmp = wx.StaticBitmap(self, -1, bitmap=self.bmp) # Display the resulting image

        
        self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID) 
        wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onNextFrame) 
        fps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS) 

        if fps!=0: self.playTimer.Start(1000/fps) # every X ms 
        else: self.playTimer.Start(1000/15) # assuming 15 fps 

        #del(storage)
        #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)

    def onNextFrame(self, evt):
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)

        mask = self.ImagePro(capture2,orig2,processed2,storage,grid,squares)
        #img = processed
        if mask:
            cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(mask.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()

class CvDisplayPanel3(wx.Panel):


    def merge(self,orig,orig2,storage,grid,warp):

        combined = cv.CreateImage((orig.width,orig.height*2), cv.IPL_DEPTH_8U, 3)
 
        orig = processor.update_grid(orig,warp_coord)
        orig2 = processor.update_grid(orig2,warp_coord2) 
        #processor.draw_grid(orig)
        #processor.draw_grid(orig2)


        orig_np = np.asarray(orig[:,:])
        orig2_np = np.asarray(orig2[:,:])
        combined_np = np.asarray(combined[:,:])
        
        combined_np = np.concatenate((orig_np, orig2_np),axis=0)
        #combined = processor.draw_grid(orig)
        combined = cv.fromarray(combined_np)
        cv.CvtColor(combined, combined, cv.CV_BGR2RGB)

        mask = cv.CreateImage((400,600), cv.IPL_DEPTH_8U, 3)
        cv.Resize(combined,mask)
        return mask



    TIMER_PLAY_ID = 101 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #magic to stop the flickering
        def SetCompositeMode(self, on=True): 
            exstyle = win32api.GetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE) 
            if on: 
                exstyle |= win32con.WS_EX_COMPOSITED 
            else: 
                exstyle &= ~win32con.WS_EX_COMPOSITED 
            win32api.SetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE, exstyle) 

        SetCompositeMode(self, True)

        #self.capture = cv.CaptureFromCAM(0) # turn on the webcam
        #img = ImagePro # Convert the raw image data to something wxpython can handle.
        #cv.CvtColor(img, img, cv.CV_BGR2RGB) # fix color distortions
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        mask = self.merge(orig,orig2,storage,grid,warp)
        #cv.CvtColor(grid, grid, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(mask.width, mask.height, mask.tostring())
        sbmp = wx.StaticBitmap(self, -1, bitmap=self.bmp) # Display the resulting image

        
        self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID) 
        wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onNextFrame) 
        fps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS) 

        if fps!=0: self.playTimer.Start(1000/fps) # every X ms 
        else: self.playTimer.Start(1000/15) # assuming 15 fps 

        #del(storage)
        #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)

    def onNextFrame(self, evt):
        storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)

        mask = self.merge(orig,orig2,storage,grid,warp)
        #img = processed
        if mask:
            #cv.CvtColor(mask, mask, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(mask.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()


class Cameras(wx.Frame):

        
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1230,700))

        #self.displayPanel = CvDisplayPanel(self) # display panel for video
        #displayPanel2 = CvDisplayPanel2(self)
        #displayPanel3 = CvDisplayPanel3(self)
        
        self.display = wx.TextCtrl(self, -1, "YOLO",  style=wx.TE_MULTILINE, size=(400,300))
        box = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.GridSizer(2, 3, 1, 1)
        buttons.AddMany([(wx.Button(self, 1, 'Stop') , 0, wx.EXPAND),
                        (wx.Button(self, 2, 'Up') , 0, wx.EXPAND),
                        (wx.Button(self, 3, 'Start') , 0, wx.EXPAND),
                        (wx.Button(self, 4, 'Left') , 0, wx.EXPAND),
                        (wx.Button(self, 5, 'Down') , 0, wx.EXPAND),
                        (wx.Button(self, 6, 'Right') , 0, wx.EXPAND)])
        #box.Add(left, 1, wx.EXPAND)
        box.Add(self.display, 1, wx.EXPAND)
        box.Add(buttons, 1, wx.EXPAND)

        right = wx.BoxSizer(wx.VERTICAL)
        right.Add(CvDisplayPanel(self), 1, wx.ALL , 0)
        right.Add(CvDisplayPanel2(self), 1, wx.ALL , 0)
        #right.Add(CvDisplayPanel3(self), 1, wx.EXPAND | wx.ALL, 0)
       # self.SetSizer(right)
        
        #self.SetSizer(right)
        #self.SetSizer(right)
        left = wx.BoxSizer(wx.HORIZONTAL)
        left.Add(CvDisplayPanel3(self), 1, wx.ALL, 0)
        #left = wx.BoxSizer(wx.HORIZONTAL)

        #left.Add(CvDisplayPanel3(self), 1, wx.EXPAND | wx.ALL, 0)
        left.Add(right, 1, wx.ALL, 0)
        #self.SetSizer(left) 



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


#ImageInit(0)
capture = cv.CaptureFromCAM(0)
capture2 = cv.CaptureFromCAM(1)

orig = cv.QueryFrame(capture)
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

    orig = cv.QueryFrame(capture)
    
    cv.SetMouseCallback("calibrate",on_mouse, 0);

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