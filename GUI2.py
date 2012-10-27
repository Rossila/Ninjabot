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



#The panel containing the webcam video
class CvDisplayPanel(wx.Panel):

    def ImagePro(self,capture,orig,processed,storage,grid):
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
        mask = cv.CreateImage((640,480), cv.IPL_DEPTH_8U, 3)
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
        self.ImagePro(capture,orig,processed,storage,grid)
        cv.CvtColor(orig, orig, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(640, 300, orig.tostring())
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
        self.ImagePro(capture,orig,processed,storage,grid)
        #img = processed
        if orig:
            cv.CvtColor(orig, orig, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(orig.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()

class CvDisplayPanel2(wx.Panel):

    def ImagePro(self,capture,orig,processed,storage,grid):
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
        mask = cv.CreateImage((640,480), cv.IPL_DEPTH_8U, 3)
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
        self.ImagePro(capture2,orig2,processed2,storage,grid)
        cv.CvtColor(orig, orig, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(640, 300, orig.tostring())
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

        self.ImagePro(capture2,orig2,processed2,storage,grid)
        #img = processed
        if orig2:
            cv.CvtColor(orig2, orig2, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(orig2.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()

class CvDisplayPanel3(wx.Panel):

    def merge(self,orig,orig2,storage,grid,warp):
        #orig = cv.QueryFrame(capture)
        #cv.Normalze(orig)
        # filter for all yellow and blue - everything else is black
        #processed = processor.colorFilterCombine(orig, "yellow", "blue" ,s)
        
        # Some processing and smoothing for easier circle detection
        #cv.Canny(processed, processed, 5, 70, 3)
        #cv.Smooth(processed, processed, cv.CV_GAUSSIAN, 7, 7)
        
        #cv.ShowImage('processed2', processed)
        
        # Find&Draw circles
        #processor.find_circles(processed, storage, 100)

        #if it is in the range of 1 to 9, we can try and recalibrate our filter
        #if 1 <= storage.rows < 10:
        #    s = autocalibrate(orig, storage)
        combined = cv.CreateImage((orig.width,orig.height*2), cv.IPL_DEPTH_8U, 3)
        processor.draw_grid(orig)
        processor.draw_grid(orig2) 

        orig_np = np.asarray(orig[:,:])
        orig2_np = np.asarray(orig2[:,:])
        combined_np = np.asarray(combined[:,:])
        
        combined_np = np.concatenate((orig_np, orig2_np),axis=0)
        #combined = processor.draw_grid(orig)
        combined = cv.fromarray(combined_np)

        #print orig_np
        #print orig2_np
        #print combined.height
        #print combined.width
        #print combined_np
        """
        cv.SetImageROI(orig,(100,100,orig2.width,orig2.height))
        cv.Add(combined,orig,combined)
        #cv.Add(combined,orig,combined)
        cv.ResetImageROI(orig)
        """
        
        return combined
        #self.grid = processor.draw_grid(orig)    


        #processor.draw_circles(storage, orig)

        #grid = processor.update_grid(storage, orig, grid)


        # Delete and recreate the storage so it has the correct width
        #del(storage)
        #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        
        #cv.ShowImage('output', orig)

        #return processed
        #cv.ShowImage('grid', warp)

        #warp = processor.perspective_transform(orig)
        #cv.ShowImage('warped', warp)

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
        combined = self.merge(orig,orig2,storage,grid,warp)
        #cv.CvtColor(grid, grid, cv.CV_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(combined.width, combined.height, combined.tostring())
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

        combined = self.merge(orig,orig2,storage,grid,warp)
        #img = processed
        if combined:
            #cv.CvtColor(combined, combined, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(combined.tostring()) # update the bitmap to the current frame
            self.Refresh()
            #del(storage)
            #storage = cv.CreateMat(orig.width, 1, cv.CV_32FC3)
        evt.Skip()


class Cameras(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280,700))

        #self.displayPanel = CvDisplayPanel(self) # display panel for video
        #displayPanel2 = CvDisplayPanel2(self)
        #displayPanel3 = CvDisplayPanel3(self)
        
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
        self.SetSizer(left) 
        
        
        
        
        self.Centre()


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

class Control(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,300))
        display = wx.TextCtrl(self, -1, '',  style=wx.TE_RIGHT)
        box = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.GridSizer(2, 3, 1, 1)
        buttons.AddMany([(wx.Button(self, 1, 'Stop') , 0, wx.EXPAND),
                        (wx.Button(self, 2, 'Up') , 0, wx.EXPAND),
                        (wx.Button(self, 3, 'Start') , 0, wx.EXPAND),
                        (wx.Button(self, 4, 'Left') , 0, wx.EXPAND),
                        (wx.Button(self, 5, 'Down') , 0, wx.EXPAND),
                        (wx.Button(self, 6, 'Right') , 0, wx.EXPAND)])
        box.Add(display, 1, wx.EXPAND)
        box.Add(buttons, 1, wx.EXPAND)
        self.SetSizer(box)
        self.Centre()

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
s = []

#processor.draw_grid(grid)

app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = Cameras(None, "Cameras") # A Frame is a top-level window.
frame.Show(True)     # Show the frame.

frame2 = Control(None, "Control") # A Frame is a top-level window.
frame2.Show(True) 
app.MainLoop()
