'''How to integrate openCV and wxpython.

This program loads an image file using openCV, converts it to a format
which wxpython can handle and displays the resulting image in a
wx.Frame.'''


import wx
import cv2.cv as cv
import win32api 
import win32con 


#The panel containing the webcam video
class CvDisplayPanel(wx.Panel):
    TIMER_PLAY_ID = 101 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        #magic to stop the flickering
        def SetCompositeMode(self, on=True): 
            exstyle = win32api.GetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE) 
            if on: 
                exstyle |= win32con.WS_EX_COMPOSITED 
            else: 
                exstyle &= ~win32con.WS_EX_COMPOSITED 
            win32api.SetWindowLong(self.GetHandle(), win32con.GWL_EXSTYLE, exstyle) 

        SetCompositeMode(self, True)

        self.capture = cv.CaptureFromCAM(0) # turn on the webcam
        img = cv.QueryFrame(self.capture) # Convert the raw image data to something wxpython can handle.
        cv.CvtColor(img, img, cv.CV_BGR2RGB) # fix color distortions

        self.bmp = wx.BitmapFromBuffer(img.width, img.height, img.tostring())
        sbmp = wx.StaticBitmap(self, -1, bitmap=self.bmp) # Display the resulting image

        
        self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID) 
        wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onNextFrame) 
        fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS) 

        if fps!=0: self.playTimer.Start(1000/fps) # every X ms 
        else: self.playTimer.Start(1000/15) # assuming 15 fps 


    def onNextFrame(self, evt):
        img = cv.QueryFrame(self.capture)
        if img:
            cv.CvtColor(img, img, cv.CV_BGR2RGB)
            self.bmp.CopyFromBuffer(img.tostring()) # update the bitmap to the current frame
            self.Refresh()
        evt.Skip()


class MyFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(700,700))
        self.displayPanel = CvDisplayPanel(self) # display panel for video

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


app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = MyFrame(None, "GUI Magic") # A Frame is a top-level window.
frame.Show(True)     # Show the frame.
app.MainLoop()
