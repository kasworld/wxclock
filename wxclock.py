#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys,os.path,time,math
import wx
from time import strftime,localtime 
import calendar

wx.InitAllImageHandlers()
bgimage = None
try :
    f = open('background.jpg',"rb")
    f.close()
    bgimage = wx.Image('background.jpg')
except :
    pass


class kclock(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.fps = 30

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_TIMER, self._OnTimer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)

        # Initialize the timer that drives the update of the clock face.
        # Update every half second to ensure that there is at least one true
        # update during each realtime second.
        self.timer = wx.Timer(self)
        self.timer.Start(1000/self.fps)

        self._OnSize(None)

    def _OnSize(self, evt):
        size = self.GetClientSize()
        if size.x < 1 or size.y < 1:
            return

        self._recalcCoords(size)
        self._drawBox()

    def _OnTimer(self, evt):
        self.Refresh(False)
        datetext = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.SetTitle( datetext )
        #self.Update()
        
    def _OnDestroyWindow(self, evt):
        self.timer.Stop()
        del self.timer

    def _recalcCoords(self, size):
        if bgimage :
            self.bgbitmap = bgimage.Scale( size.width, size.height ).ConvertToBitmap()
        else :
            self.bgbitmap = wx.EmptyBitmap(*size.Get())
        self.clientsize = self.GetClientSizeTuple()
        self.adj = min(self.clientsize[0]/15,self.clientsize[1]/10)
        self.calfont = wx.Font(self.adj, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0]/2
        self.mcentery = self.clientsize[1]/2
        self.maxlen = min( self.mcenterx, self.mcentery )

    def _printText( self,dc, pstr, x, y ,r=True,g=True,b=True, depth = 5):
        w,h = dc.GetTextExtent( pstr)
        for i in range(0,depth) :
            cr = int(i*128./(depth-1))
            dc.SetTextForeground(  
                    wx.Colour( cr if r else cr/2 ,cr if g else cr/2  , cr if b else cr/2, 0x7f )  
                    )
            dc.DrawText( pstr , max(0,-w/2 + x +depth -i) , max(0,y +depth -i) ) 

    def _drawCalendar(self,dc):
        if bgimage :
            dc.DrawBitmap(self.bgbitmap,0,0)
        dc.SetFont(self.calfont)
        #dc.SetPen(wx.Pen(self.border, self.width, wx.SOLID))
        
        datetext = strftime("%Y-%m-%d", localtime())
        #w,h = dc.GetTextExtent( datetext)
        self._printText( dc,datetext,self.clientsize[0]/4 , 0) 

        calday = calendar.Calendar().monthdays2calendar(localtime()[0], localtime()[1])
        """[[(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)], [(5, 0), (6, 1), (7, 2), (8, 3), (9, 4), (10, 5), (11, 6)], [(12, 0), (13, 1), (14, 2), (15, 3), (16, 4), (17, 5), (18, 6)], [(19, 0), (20, 1), (21, 2), (22, 3), (23, 4), (24, 5), (25, 6)], [(26, 0), (27, 1), (28, 2), (29, 3), (30, 4), (31, 5), (0, 6)]]"""
        wwy = 0
        for wwl in calday :
            wwy += 1
            for wwx in wwl :
                # pos is wd[1] , wwc 
                if ( wwx[0] ) :
                    ccc = ( 1,1,1)
                    if wwx[1] == 5 :
                        ccc = ( 0,0,1)
                    if wwx[1] == 6 :
                        ccc = ( 1,0,0)
                    if wwx[0] ==localtime()[2] :
                        ccc = ( 0,1,0)
                    self._printText( dc, str(wwx[0]) ,self.adj+ wwx[1] * self.clientsize[0]/7  , wwy *self.clientsize[1]/7, *ccc  )

    def _drawBox(self):
        """Draws clock face and tick marks onto the faceBitmap."""
        pdc = wx.BufferedDC(None, self.bgbitmap)
        #try:
        #    dc = wx.GCDC(pdc)
        #except:
        #    dc = pdc
        #dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        if not bgimage :
            pdc.SetBackground(wx.Brush("Black", wx.SOLID))
            pdc.Clear()
        self._drawCalendar(pdc)
        self._drawClockTicks(pdc)

    def getpoint(self, angle, length ):
        rad = math.radians( angle + 270 )
        l = self.maxlen * length
        return self.mcenterx + l * math.cos( rad ) , self.mcentery + l * math.sin( rad )

    def gethms(self, pt ):
        lx = self.mcenterx - pt[0]
        ly = self.mcentery - pt[1]
        a = math.atan2( ly,lx )
        a = (math.degrees( a) +270 ) % 360
        ss = 12*60*60*a/360
        return ss - ss%60
    def _drawClockTicks(self, dc ):
        dc.SetPen(wx.Pen("White", 1))
        for a in range( 0,360 ):
            c = (255,255,255)
            p1 = self.getpoint( a , 1.0 )
            if a% 30 ==0 : # hour 
                p2 = self.getpoint( a    , 0.90 ) 
            elif a % 6 == 0: # min & sec 
                p2 = self.getpoint( a    , 0.95 ) 
            else : # 1 degree
                p2 = self.getpoint( a    , 0.98 )
            dc.DrawLine( p1[0],p1[1] , p2[0], p2[1]  )
    
    def makehandpts( self,angle, length, da,rlen= 0.15 ):
        p1 = self.getpoint( angle, length )
        p3 = self.getpoint( angle, -rlen )
        p2 = self.getpoint( angle+da, 0.05 )
        p4 = self.getpoint( angle-da, 0.05 )
        pts = (p2,p1, p4 ,
                (self.clientsize[0] - p4[0],self.clientsize[1]-p4[1]), 
                p3, 
                (self.clientsize[0] - p2[0],self.clientsize[1]-p2[1]),
                p2
                )
        return pts
    def _drawclockhands( self,dc, hh,mm,ss,ms ):
        secangle = ss *6.0 + ms*6/1000.0
        minangle = mm * 6.0 + ss/10.0 + ms/10000.0
        hourangle = hh * 30.0  + mm/2.0 + ss/120.0
        for d in range( 0,30,1):
            maxrgb = min( abs(d*9) , 255 )
            dc.SetPen(wx.Pen(wx.Colour( 40, 40, maxrgb) , 1))
            dc.DrawLines(  self.makehandpts(secangle, 1.0, d, 0.3  )  )

            dc.SetPen(wx.Pen(wx.Colour( 40, maxrgb,40) , 1))
            dc.DrawLines(  self.makehandpts(minangle, 0.90, d, 0.2 )  )

            dc.SetPen(wx.Pen(wx.Colour( maxrgb,40,40) , 1))
            dc.DrawLines(  self.makehandpts(hourangle, 0.80, d,  0.1 )  )

    def _drawHands(self,dc):
        mst = time.time()
        self.lt = time.localtime(mst)
        ms = int((mst - int(mst))*1000)
        self._drawclockhands(dc, self.lt[3],self.lt[4],self.lt[5],ms )

        dc.SetBrush(wx.Brush(wx.Colour( 0x7f,0x7f,0x7f), wx.SOLID))
        dc.DrawCircle( self.clientsize[0]/2, self.clientsize[1]/2 , self.clientsize[1]/100)

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        #try:
        #    dc = wx.GCDC(pdc)
        #except:
        #    dc = pdc
        dc.DrawBitmap(self.bgbitmap, 0, 0)

        dc.SetFont(self.calfont)
        datetext = strftime("%H:%M:%S", localtime())
        self._printText( dc,datetext,self.clientsize[0] - self.clientsize[0]/4 , 0) 
        self._drawHands( dc )

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, size=(640, 480))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
