import wx
import cv2.cv as cv
import cv2


class ColorFilter(wx.Frame):
    global red
    global blue
    global green
    global yellow

    red =  [(160, 70,70), (180, 255, 255)]
    blue =  [(100, 100, 100), (120,255,255)]
    green = [(70, 70, 70), (80, 255, 255)]
    yellow = [(20, 70, 70), (60, 255, 255)]

           
    def __init__(self, *args, **kw):
        super(ColorFilter, self).__init__(*args, **kw) 
        
        self.InitUI()
    


    def InitUI(self):   
        
        self.pnl = wx.Panel(self)
        

        rtb = wx.Button(self.pnl,id=11, label='red', pos=(50, 25))
        ytb = wx.Button(self.pnl,id=12, label='yellow', pos=(150, 25))
        gtb = wx.Button(self.pnl,id=13, label='green', pos=(250, 25))
        btb = wx.Button(self.pnl,id=14, label='blue', pos=(350, 25))

        #self.cself.pnl  = wx.Panel(self.pnl, pos=(150, 20), size=(110, 110))
        #self.cself.pnl.SetBackgroundColour(self.col)
        self.txt = wx.StaticText(self.pnl, label='Hue', pos=(400, 125))
        self.txt = wx.StaticText(self.pnl, label='Min', pos=(20, 90))   
        self.sld_hue_min = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 100), 
            size=(250, -1), style=wx.SL_HORIZONTAL)

        self.txt = wx.StaticText(self.pnl, label='Max', pos=(20, 140))
        self.sld_hue_max = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 150), 
            size=(250, -1), style=wx.SL_HORIZONTAL)

        
        self.txt = wx.StaticText(self.pnl, label='Saturation', pos=(400, 275)) 
        self.txt = wx.StaticText(self.pnl, label='Min', pos=(20, 240)) 
        self.sld_sat_min = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 250), 
            size=(250, -1), style=wx.SL_HORIZONTAL)
        
        self.txt = wx.StaticText(self.pnl, label='Max', pos=(20, 290))
        self.sld_sat_max = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 300), 
            size=(250, -1), style=wx.SL_HORIZONTAL)

        
        self.txt = wx.StaticText(self.pnl, label='Value', pos=(400, 425)) 
        self.txt = wx.StaticText(self.pnl, label='Min', pos=(20, 390)) 
        self.sld_val_min = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 400), 
            size=(250, -1), style=wx.SL_HORIZONTAL)
        
        self.txt = wx.StaticText(self.pnl, label='Max', pos=(20, 440)) 
        self.sld_val_max = wx.Slider(self.pnl, value=200, minValue=0, maxValue=255, pos=(40, 450), 
            size=(250, -1), style=wx.SL_HORIZONTAL)


        rtb.Bind(wx.EVT_BUTTON, self.ButtonRed, id =11)
        ytb.Bind(wx.EVT_BUTTON, self.ButtonYellow, id =12)
        gtb.Bind(wx.EVT_BUTTON, self.ButtonGreen, id =13)
        btb.Bind(wx.EVT_BUTTON, self.ButtonBlue, id =14)

        self.SetSize((500, 550))
        self.SetTitle('ColorFilter')
        self.Centre()
        self.Show(True)     


    def ButtonRed(self, e):
        
        #obj = e.GetEventObject()
        #isPressed = obj.GetValue()
        
        #self.color = "red"
        #pnl.Hide()
        self.sld_hue_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_min_red)
        self.sld_hue_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_max_red)
        self.sld_sat_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_min_red)
        self.sld_sat_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_max_red)
        self.sld_val_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_min_red)
        self.sld_val_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_max_red)
        self.sld_hue_min.SetValue(red[0][0])
        self.sld_hue_max.SetValue(red[1][0])
        self.sld_sat_min.SetValue(red[0][1])
        self.sld_sat_max.SetValue(red[1][1])
        self.sld_val_min.SetValue(red[0][2])
        self.sld_val_max.SetValue(red[1][2])

        #cv.ShowImage("ColorFilter_Image", Cameras.hsv_filter)


        
    def ButtonGreen(self, e):
        
        #obj = e.GetEventObject()
        #isPressed = obj.GetValue()
        
        #self.color = "green"
        self.sld_hue_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_min_green)
        self.sld_hue_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_max_green)
        self.sld_sat_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_min_green)
        self.sld_sat_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_max_green)
        self.sld_val_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_min_green)
        self.sld_val_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_max_green)
        self.sld_hue_min.SetValue(green[0][0])
        self.sld_hue_max.SetValue(green[1][0])
        self.sld_sat_min.SetValue(green[0][1])
        self.sld_sat_max.SetValue(green[1][1])
        self.sld_val_min.SetValue(green[0][2])
        self.sld_val_max.SetValue(green[1][2])

        #cv.ShowImage("ColorFilter_Image", Cameras.hsv_filter)
            
        #self.cpnl.SetBackgroundColour(self.col)
        
    def ButtonBlue(self, e):
        
        #obj = e.GetEventObject()
        #isPressed = obj.GetValue()
        
        #self.color = "blue"
        self.sld_hue_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_min_blue)
        self.sld_hue_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_max_blue)
        self.sld_sat_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_min_blue)
        self.sld_sat_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_max_blue)
        self.sld_val_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_min_blue)
        self.sld_val_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_max_blue)
        self.sld_hue_min.SetValue(blue[0][0])
        self.sld_hue_max.SetValue(blue[1][0])
        self.sld_sat_min.SetValue(blue[0][1])
        self.sld_sat_max.SetValue(blue[1][1])
        self.sld_val_min.SetValue(blue[0][2])
        self.sld_val_max.SetValue(blue[1][2])

        #cv.ShowImage("ColorFilter_Image", Cameras.hsv_filter)
            
        #self.cpnl.SetBackgroundColour(self.col)
        
    def ButtonYellow(self, e):
        
        #obj = e.GetEventObject()
        #isPressed = obj.GetValue()
        
        #self.color = "yellow"
        self.sld_hue_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_min_yellow)
        self.sld_hue_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_hue_max_yellow)
        self.sld_sat_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_min_yellow)
        self.sld_sat_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_sat_max_yellow)
        self.sld_val_min.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_min_yellow)
        self.sld_val_max.Bind(wx.EVT_SCROLL, self.OnSliderScroll_sld_val_max_yellow)
        self.sld_hue_min.SetValue(yellow[0][0])
        self.sld_hue_max.SetValue(yellow[1][0])
        self.sld_sat_min.SetValue(yellow[0][1])
        self.sld_sat_max.SetValue(yellow[1][1])
        self.sld_val_min.SetValue(yellow[0][2])
        self.sld_val_max.SetValue(yellow[1][2])

        #cv.ShowImage("ColorFilter_Image", Cameras.hsv_filter)
            
        #self.cpnl.SetBackgroundColour(self.col)
        

    def OnSliderScroll_sld_hue_min_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()
        
        red = ((val,red[0][1],red[0][2]),(red[1][0],red[1][1],red[1][2]))
        #red[0][0] = val

    def OnSliderScroll_sld_hue_max_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()
        
        #red[1][0] = val
        red = ((red[0][0],red[0][1],red[0][2]),(val,red[1][1],red[1][2])) 

    def OnSliderScroll_sld_sat_min_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()
        
        #red[0][1] = val
        red = ((red[0][0],val,red[0][2]),(red[1][0],red[1][1],red[1][2]))

    def OnSliderScroll_sld_sat_max_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()

        #red[1][1] = val
        red = ((red[0][0],red[0][1],red[0][2]),(red[1][0],val,red[1][2])) 

    def OnSliderScroll_sld_val_min_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()

        #red[0][2] = val
        red = ((red[0][0],red[0][1],val),(red[1][0],red[1][1],red[1][2])) 

    def OnSliderScroll_sld_val_max_red(self, e):
        global red
        
        obj = e.GetEventObject()
        val = obj.GetValue()

        #red[1][2] = val
        red = ((red[0][0],red[0][1],red[0][2]),(red[1][0],red[1][1],val)) 



    def OnSliderScroll_sld_hue_min_green(self, e):
        global green
        
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[0][0] = val
        green = ((val,green[0][1],green[0][2]),(green[1][0],green[1][1],green[1][2])) 

    def OnSliderScroll_sld_hue_max_green(self, e):
        global green
        
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[1][0] = val
        green = ((green[0][0],green[0][1],green[0][2]),(val,green[1][1],green[1][2])) 

    def OnSliderScroll_sld_sat_min_green(self, e):
        global green
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[0][1] = val
        green = ((green[0][0],val,green[0][2]),(green[1][0],green[1][1],green[1][2])) 

    def OnSliderScroll_sld_sat_max_green(self, e):
        global green
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[1][1] = val
        green = ((green[0][0],green[0][1],green[0][2]),(green[1][0],val,green[1][2])) 

    def OnSliderScroll_sld_val_min_green(self, e):
        global green
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[0][2] = val
        green = ((green[0][0],green[0][1],val),(green[1][0],green[1][1],green[1][2])) 

    def OnSliderScroll_sld_val_max_green(self, e):
        global green
        obj = e.GetEventObject()
        val = obj.GetValue()

        #green[1][2] = val
        green = ((green[0][0],green[0][1],green[0][2]),(green[1][0],green[1][1],val)) 





    def OnSliderScroll_sld_hue_min_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[0][0] = val
        blue = ((val,blue[0][1],blue[0][2]),(blue[1][0],blue[1][1],blue[1][2])) 

    def OnSliderScroll_sld_hue_max_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[1][0] = val
        blue = ((blue[0][0],blue[0][1],blue[0][2]),(val,blue[1][1],blue[1][2])) 

    def OnSliderScroll_sld_sat_min_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[0][1] = val
        blue = ((blue[0][0],val,blue[0][2]),(blue[1][0],blue[1][1],blue[1][2])) 

    def OnSliderScroll_sld_sat_max_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[1][1] = val
        blue = ((blue[0][0],blue[0][1],blue[0][2]),(blue[1][0],val,blue[1][2])) 

    def OnSliderScroll_sld_val_min_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[0][2] = val
        blue = ((blue[0][0],blue[0][1],val),(blue[1][0],blue[1][1],blue[1][2])) 

    def OnSliderScroll_sld_val_max_blue(self, e):
        global blue
        obj = e.GetEventObject()
        val = obj.GetValue()

        #blue[1][2] = val
        blue = ((blue[0][0],blue[0][1],blue[0][2]),(blue[1][0],blue[1][1],val)) 




    def OnSliderScroll_sld_hue_min_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[0][0] = val
        yellow = ((val,yellow[0][1],yellow[0][2]),(yellow[1][0],yellow[1][1],yellow[1][2])) 

    def OnSliderScroll_sld_hue_max_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[1][0] = val
        yellow = ((yellow[0][0],yellow[0][1],yellow[0][2]),(val,yellow[1][1],yellow[1][2])) 

    def OnSliderScroll_sld_sat_min_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[0][1] = val
        yellow = ((yellow[0][0],val,yellow[0][2]),(yellow[1][0],yellow[1][1],yellow[1][2])) 

    def OnSliderScroll_sld_sat_max_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[1][1] = val
        yellow = ((yellow[0][0],yellow[0][1],yellow[0][2]),(yellow[1][0],val,yellow[1][2])) 

    def OnSliderScroll_sld_val_min_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[0][2] = val
        yellow = ((yellow[0][0],yellow[0][1],val),(yellow[1][0],yellow[1][1],yellow[1][2])) 

    def OnSliderScroll_sld_val_max_yellow(self, e):
        global yellow
        obj = e.GetEventObject()
        val = obj.GetValue()

        #yellow[1][2] = val
        yellow = ((yellow[0][0],yellow[0][1],yellow[0][2]),(yellow[1][0],yellow[1][1],val)) 
