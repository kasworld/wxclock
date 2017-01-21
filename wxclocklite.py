#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    wximageclock ver 2.1

    Copyright 2010,2011 kasw <kasworld@gmail.com>
    
"""
import os
import sys
import os.path
import time
import math
import random
import wx
from time import strftime, localtime
import time
import calendar

wx.InitAllImageHandlers()


def getHMSAngle():
    mst = time.time()
    lt = time.localtime(mst)
    ms = int((mst - int(mst)) * 1000)
    secangle = lt[5] * 6.0 + ms * 6 / 1000.0 + 90
    minangle = lt[4] * 6.0 + lt[5] / 10.0 + ms / 10000.0 + 90
    hourangle = lt[3] * 30.0 + lt[4] / 2.0 + lt[5] / 120.0 + 90
    return hourangle, minangle, secangle


class kclock(wx.Frame):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE  # | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.fps = 10
        self.isfullscreen = True
        self.ShowFullScreen(self.isfullscreen)
        self.rawbgimage = None
        self.getbgimagefilename()
        self.loadbgimage()

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_TIMER, self._OnTimer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.timer = wx.Timer(self)
        self.timer.Start(1000 / self.fps)

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
        self.SetTitle(datetext)

        if time.time() - self.imageloadtime > 60:
            self.loadbgimage()
            self._OnSize(None)
            # self.Refresh(True)
            # self.Update()

    def OnMouse(self, evt):
        if evt.LeftIsDown():
            self.Close()
        if evt.RightDown():
            self.isfullscreen = not self.isfullscreen
            self.ShowFullScreen(self.isfullscreen)
            self._OnSize(None)

    def _OnDestroyWindow(self, evt):
        self.timer.Stop()
        del self.timer

    def getbgimagefilename(self):
        if len(sys.argv) == 2:
            imagebasedirname = sys.argv[1]
        else:
            basedirname = os.path.dirname(os.path.abspath(__file__))
            imagebasedirname = os.path.join(basedirname, "bgimages")
        self.imagefilenames = []
        for root, dirs, files in os.walk(imagebasedirname):
            self.imagefilenames.extend(
                [os.path.join(root, f) for f in
                 filter(lambda f: f[-4:].lower() in ['.jpg', '.bmp', '.png'],
                        files)]
            )
        random.shuffle(self.imagefilenames)

    def loadbgimage(self):
        self.imageloadtime = time.time()
        if self.imagefilenames:
            imagename = self.imagefilenames.pop()
        nulog = wx.LogNull()
        try:
            f = open(imagename, "rb")
            f.close()
            self.rawbgimage = wx.Image(imagename)
            self.imagefilenames.insert(0, imagename)
        except:
            self.rawbgimage = None

    def resizefixaspect(self, image, wx, wy):
        oriw = image.GetWidth()
        orih = image.GetHeight()
        oriap = float(oriw) / orih
        targetap = float(wx) / wy
        if oriap < targetap:  # ori is wider
            scalerate = float(wy) / orih
        else:
            scalerate = float(wx) / oriw
        rtnimg = None
        try:
            rtnimg = image.Scale(oriw * scalerate, orih * scalerate).Size(
                (wx, wy), ((wx - oriw * scalerate) / 2, (wy - orih * scalerate) / 2))
        except:
            pass
        return rtnimg

    def _recalcCoords(self, size):
        if self.rawbgimage:
            self.bgbitmap = self.resizefixaspect(
                self.rawbgimage, size.width, size.height).ConvertToBitmap()
        else:
            self.bgbitmap = wx.EmptyBitmap(*size.Get())
        self.clientsize = self.GetClientSizeTuple()
        self.adj = min(self.clientsize[0] / 10, self.clientsize[1] / 10)
        self.calendarFont = wx.Font(
            self.adj / 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.timeFont = wx.Font(self.adj * 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2
        if self.rawbgimage:
            self.maxlen = min(self.mcenterx, self.mcentery) / 2
        else:
            self.maxlen = min(self.mcenterx, self.mcentery)
        self.anclockmcenterx = self.clientsize[0] - self.maxlen
        self.anclockmcentery = self.clientsize[1] - self.maxlen

    def _printCenterXText(self, dc, pstr, x, y, r=True, g=True, b=True, depth=2):
        w, h = dc.GetTextExtent(pstr)
        for i in range(0, depth):
            cr = int(i * 128. / (depth - 1))
            dc.SetTextForeground(
                wx.Colour(cr if r else cr / 2, cr if g else cr /
                          2, cr if b else cr / 2, 0x7f)
            )
            dc.DrawText(pstr,  -w / 2 + x + depth - i, y + depth - i)
            # dc.DrawText(pstr, max(0, -w / 2 + x + depth - i),
            #             max(0, y + depth - i))

    def _drawCalendar(self, dc):
        if self.rawbgimage:
            dc.DrawBitmap(self.bgbitmap, 0, 0)
        dc.SetFont(self.calendarFont)
        #dc.SetPen(wx.Pen(self.border, self.width, wx.SOLID))

        datetext = strftime("%Y-%m-%d", localtime())
        #w,h = dc.GetTextExtent( datetext)
        self._printCenterXText(dc, datetext, self.adj * 4, self.adj * 3.5)

        calday = calendar.Calendar(6).monthdays2calendar(
            localtime()[0], localtime()[1])
        """[[(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)], [(5, 0), (6, 1), (7, 2), (8, 3), (9, 4), (10, 5), (11, 6)], [(12, 0), (13, 1), (14, 2), (15, 3), (16, 4), (17, 5), (18, 6)], [(19, 0), (20, 1), (21, 2), (22, 3), (23, 4), (24, 5), (25, 6)], [(26, 0), (27, 1), (28, 2), (29, 3), (30, 4), (31, 5), (0, 6)]]"""
        wwy = 0
        for wwl in calday:
            posx = 0
            for wwx in wwl:
                # pos is wd[1] , wwc
                if (wwx[0]):
                    ccc = (1, 1, 1)
                    if wwx[1] == 5:
                        ccc = (0, 0, 1)
                    if wwx[1] == 6:
                        ccc = (1, 0, 0)
                    if wwx[0] == localtime()[2]:
                        ccc = (0, 1, 0)
                    self._printCenterXText(dc, str(wwx[0]),
                                           self.adj + posx * self.adj * 1.3,
                                           self.clientsize[1] - self.adj *
                                           5.5 + wwy * self.adj * 1.0,
                                           *ccc)
                posx += 1
            wwy += 1

    def _drawBox(self):
        """Draws clock face and tick marks onto the faceBitmap."""
        pdc = wx.BufferedDC(None, self.bgbitmap)
        # try:
        #    dc = wx.GCDC(pdc)
        # except:
        #    dc = pdc
        #dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        if not self.rawbgimage:
            pdc.SetBackground(wx.Brush("Black", wx.SOLID))
            pdc.Clear()
        self._drawCalendar(pdc)
        self._drawClockTicks(pdc)

    def getpoint(self, angle, length):
        rad = math.radians(angle + 270)
        l = self.maxlen * length
        return self.anclockmcenterx + l * math.cos(rad), self.anclockmcentery + l * math.sin(rad)

    def gethms(self, pt):
        lx = self.anclockmcenterx - pt[0]
        ly = self.anclockmcentery - pt[1]
        a = math.atan2(ly, lx)
        a = (math.degrees(a) + 270) % 360
        ss = 12 * 60 * 60 * a / 360
        return ss - ss % 60

    def _drawClockTicks(self, dc):
        tw = self.adj / 50
        td = max(self.adj / 100, 1)
        dc.SetPen(wx.Pen("Black", tw))
        for a in range(0, 360):
            c = (255, 255, 255)
            p1 = self.getpoint(a, 1.0)
            if a % 30 == 0:  # hour
                p2 = self.getpoint(a, 0.90)
            elif a % 6 == 0:  # min & sec
                p2 = self.getpoint(a, 0.95)
            else:  # 1 degree
                p2 = self.getpoint(a, 0.98)
            dc.DrawLine(p1[0] + td, p1[1] + td, p2[0] + td, p2[1] + td)
        dc.SetPen(wx.Pen("White", tw))
        for a in range(0, 360):
            c = (255, 255, 255)
            p1 = self.getpoint(a, 1.0)
            if a % 30 == 0:  # hour
                p2 = self.getpoint(a, 0.90)
            elif a % 6 == 0:  # min & sec
                p2 = self.getpoint(a, 0.95)
            else:  # 1 degree
                p2 = self.getpoint(a, 0.98)
            dc.DrawLine(p1[0], p1[1], p2[0], p2[1])

    def makehandpts(self, angle, length, da, rlen=0.15):
        p1 = self.getpoint(angle, length)
        p3 = self.getpoint(angle, -rlen)
        p2 = self.getpoint(angle + da, 0.05)
        p4 = self.getpoint(angle - da, 0.05)
        p5 = self.getpoint(angle + da, -0.05)
        p6 = self.getpoint(angle - da, -0.05)
        pts = (p2, p1, p4, p6, p3, p5,  p2)
        return pts

    def _drawclockhands(self, dc):
        hw = self.adj / 40
        hourangle, minangle, secangle = getHMSAngle()

        for d in range(30, 0, -30):
            maxrgb = min(abs(d * 9), 255)
            dc.SetPen(wx.Pen(wx.Colour(40, 40, maxrgb), hw))
            dc.DrawLines(self.makehandpts(secangle, 1.0, d, 0.3))

            dc.SetPen(wx.Pen(wx.Colour(40, maxrgb, 40), hw))
            dc.DrawLines(self.makehandpts(minangle, 0.90, d, 0.2))

            dc.SetPen(wx.Pen(wx.Colour(maxrgb, 40, 40), hw))
            dc.DrawLines(self.makehandpts(hourangle, 0.80, d,  0.1))

    def _drawHands(self, dc):
        self._drawclockhands(dc)

        #dc.SetBrush(wx.Brush(wx.Colour( 0x7f,0x7f,0x7f), wx.SOLID))
        #dc.DrawCircle( self.mcenterx, self.mcentery , self.adj/10)

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        # try:
        #    dc = wx.GCDC(pdc)
        # except:
        #    dc = pdc
        dc.DrawBitmap(self.bgbitmap, 0, 0)

        dc.SetFont(self.timeFont)
        datetext = strftime("%H:%M:%S", localtime())
        self._printCenterXText(dc, datetext, self.mcenterx, 0)
        self._drawHands(dc)

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, size=(640, 480))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
