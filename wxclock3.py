#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    wximageclock ver 2.1

    Copyright 2010,2011 kasw <kasworld@gmail.com>

"""
import os
import sys
import os.path
import math
import random
import wx
from time import strftime, localtime
import calendar

wx.InitAllImageHandlers()

import time

import sys
import os.path
srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(os.path.join(os.path.split(srcdir)[0], 'kaswlib'))
from kaswxlib import *


def getHMSAngles(mst):
    """ clock hands angle
    mst = time.time()"""

    lt = time.localtime(mst)
    ms = mst - int(mst)
    return lt[3] * 30.0 + lt[4] / 2.0 + lt[5] / 120.0, lt[4] * 6.0 + lt[5] / 10.0 + ms / 10, lt[5] * 6.0 + ms * 6


class kclock(wx.Frame, FPSlogic):

    def doFPSlogic(self, thisframe):
        self.Refresh(False)
        datetext = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.SetTitle(datetext)
        #~ if time.time() - self.imageloadtime > 60 :
        #~ self.loadbgimage()
        #~ self._OnSize(None)

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE  # | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.fps = 30
        self.isfullscreen = True
        self.ShowFullScreen(self.isfullscreen)
        self.rawbgimage = None
        self.getbgimagefilename()
        self.loadbgimage()

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self._OnSize(None)
        self.FPSTimerInit(self.fps)

    def _OnSize(self, evt):
        size = self.GetClientSize()
        if size.x < 1 or size.y < 1:
            return

        self._recalcCoords(size)
        self._drawBox()

    def OnMouse(self, evt):
        # if evt.LeftIsDown():
        #     self.Close()
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
        self.calfont = wx.Font(self.adj / 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.bigfont = wx.Font(self.adj * 1.6, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2
        if self.rawbgimage:
            self.maxlen = min(self.mcenterx, self.mcentery) / 2
        else:
            self.maxlen = min(self.mcenterx, self.mcentery)
        self.mcenterx = self.clientsize[0] - self.maxlen
        self.mcentery = self.clientsize[1] - self.maxlen

    def _printText(self, dc, pstr, x, y, r=True, g=True, b=True, depth=2):
        w, h = dc.GetTextExtent(pstr)
        for i in range(0, depth):
            cr = int(i * 255. / (depth - 1))
            dc.SetTextForeground(
                wx.Colour(cr if r else cr * .8, cr if g else cr * .8,
                          cr if b else cr * .8, 0x80)
            )
            dc.DrawText(pstr, max(0, -w / 2 + x + depth - i),
                        max(0, y + depth - i))

    def getCenterPos(self, even=True):
        mst = time.time()
        lt = time.localtime(mst)
        ms = int((mst - int(mst)) * 1000)

        centerlen = self.maxlen + \
            (self.clientsize[0] - self.maxlen * 2) * \
            (lt.tm_sec * 100 + ms / 10.0) / 6000.0
        if lt.tm_min % 2:
            rtnx = self.clientsize[0] - centerlen if even else centerlen
        else:
            rtnx = centerlen if even else self.clientsize[0] - centerlen

        centerlen = self.maxlen + \
            (self.clientsize[1] - self.maxlen * 2) * \
            (lt.tm_sec * 100 + ms / 10.0) / 6000.0
        if lt.tm_min % 2:
            rtny = self.clientsize[1] - centerlen if even else centerlen
        else:
            rtny = centerlen if even else self.clientsize[1] - centerlen

        return rtnx, rtny

    def _drawCalendar(self, dc):
        wdposx, wdposy = self.getCenterPos(False)
        dc.SetFont(self.calfont)
        w, h = dc.GetTextExtent("00")
        calday = calendar.Calendar(6).monthdays2calendar(
            localtime()[0], localtime()[1])
        """[[(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)], [(5, 0), (6, 1), (7, 2), (8, 3), (9, 4), (10, 5), (11, 6)], [(12, 0), (13, 1), (14, 2), (15, 3), (16, 4), (17, 5), (18, 6)], [(19, 0), (20, 1), (21, 2), (22, 3), (23, 4), (24, 5), (25, 6)], [(26, 0), (27, 1), (28, 2), (29, 3), (30, 4), (31, 5), (0, 6)]]"""
        wwy = 0
        for wwl in calday:
            posx = 0
            for wwx in wwl:
                # pos is wd[1] , wwc
                if (wwx[0]):
                    ccc = (True, True, True)
                    if wwx[1] == 5:
                        ccc = (False, True, True)
                    if wwx[1] == 6:
                        ccc = (True, False, False)
                    if wwx[0] == localtime()[2]:
                        ccc = (False, True, False)
                    self._printText(dc, str(wwx[0]),
                                    wdposx + (posx - 3) * w * 1.5,
                                    wdposy + wwy * h * 1.1,
                                    # wdposy self.clientsize[1] - (5-wwy)*h*1.5
                                    # ,
                                    *ccc)
                posx += 1
            wwy += 1

    def _drawBox(self):
        """Draws clock face and tick marks onto the faceBitmap."""
        pdc = wx.BufferedDC(None, self.bgbitmap)
        if not self.rawbgimage:
            pdc.SetBackground(wx.Brush("grey", wx.SOLID))
            pdc.Clear()
        else:
            pdc.DrawBitmap(self.bgbitmap, 0, 0)
        # self._drawCalendar(pdc)

    def getpoint2(self, cx, cy, r, angle, length):
        rad = math.radians(angle + 270)
        l = r * length
        return cx + l * math.cos(rad), cy + l * math.sin(rad)

    def _drawClockTicks2(self, dc, cx, cy, r, c1, c2=None):
        tw = r / 150
        td = max(tw / 2, 1)
        if c2:
            dc.SetPen(wx.Pen(c2, tw))
            for a in range(0, 360):
                #c = (255,255,255)
                p1 = self.getpoint2(cx, cy, r, a, 1.0)
                if a % 30 == 0:  # hour
                    p2 = self.getpoint2(cx, cy, r, a, 0.90)
                elif a % 6 == 0:  # min & sec
                    p2 = self.getpoint2(cx, cy, r, a, 0.95)
                else:  # 1 degree
                    p2 = self.getpoint2(cx, cy, r, a, 0.98)
                dc.DrawLine(p1[0] + td, p1[1] + td, p2[0] + td, p2[1] + td)
        dc.SetPen(wx.Pen(c1, tw))
        for a in range(0, 360):
            #c = (255,255,255)
            p1 = self.getpoint2(cx, cy, r, a, 1.0)
            if a % 30 == 0:  # hour
                p2 = self.getpoint2(cx, cy, r, a, 0.90)
            elif a % 6 == 0:  # min & sec
                p2 = self.getpoint2(cx, cy, r, a, 0.95)
            else:  # 1 degree
                p2 = self.getpoint2(cx, cy, r, a, 0.98)
            dc.DrawLine(p1[0], p1[1], p2[0], p2[1])

    def makehandpts2(self, cx, cy, r, angle, length, da, rlen=0.15):
        p1 = self.getpoint2(cx, cy, r,  angle, length)
        #p3 = self.getpoint2(cx,cy,r,  angle, -rlen )
        #p2 = self.getpoint2(cx,cy,r,  angle+da, 0.05 )
        #p4 = self.getpoint2(cx,cy,r,  angle-da, 0.05 )
        #p5 = self.getpoint2(cx,cy,r,  angle+da, -0.05 )
        #p6 = self.getpoint2(cx,cy,r,  angle-da, -0.05 )
        #pts = (p2,p1, p4 , p6 , p3, p5,  p2 )
        return (p1, (cx, cy))  # pts

    def _drawclockhands(self, dc, mst, wday):
        wdposx, wdposy = self.getCenterPos(True)
        hw = self.adj / 40

        #~ secangle = ss *6.0 + ms*6/1000.0
        #~ minangle = mm * 6.0 + ss/10.0 + ms/10000.0
        #~ hourangle = hh * 30.0  + mm/2.0 + ss/120.0

        hourangle, minangle, secangle = getHMSAngles(mst)

        hourco = wx.Colour(0xff, 0x40, 0x40)
        minco = wx.Colour(0, 0xc0, 0)
        secco = wx.Colour(0x40, 0x40, 0xff)

        if True:
            hourlen, minlen, seclen = 0.6, 0.8, 1.0

            seccx, seccy = wdposx, wdposy  # self.mcentery
            mincx, mincy = self.getpoint2(
                seccx, seccy, self.maxlen, secangle, 0.2)
            hourcx, hourcy = self.getpoint2(
                mincx, mincy, self.maxlen, minangle, 0.2)
        else:
            hourlen, minlen, seclen = 1.0, 0.8, 0.6

            hourcx, hourcy = wdposx, wdposy  # self.mcentery
            mincx, mincy = self.getpoint2(
                hourcx, hourcy, self.maxlen, hourangle, 0.2)
            seccx, seccy = self.getpoint2(
                mincx, mincy, self.maxlen, minangle, 0.2)

        hourpos = self.getpoint2(
            hourcx, hourcy, self.maxlen, hourangle, hourlen)
        minpos = self.getpoint2(mincx, mincy, self.maxlen, minangle, minlen)
        secpos = self.getpoint2(seccx, seccy, self.maxlen, secangle, seclen)

        dc.SetPen(wx.Pen(hourco, hw))
        dc.DrawLines(((hourcx, hourcy), hourpos))
        self._drawClockTicks2(dc, hourcx, hourcy,
                              self.maxlen * hourlen, hourco)  # , "black" )

        dc.SetBrush(wx.Brush(hourco, wx.SOLID))
        dc.DrawCircle(hourcx, hourcy, self.adj / 10)

        dc.SetPen(wx.Pen(minco, hw))
        dc.DrawLines(((mincx, mincy), minpos))
        self._drawClockTicks2(
            dc, mincx, mincy, self.maxlen * minlen, minco)  # , "black" )

        dc.SetBrush(wx.Brush(minco, wx.SOLID))
        dc.DrawCircle(mincx, mincy, self.adj / 10)

        dc.SetPen(wx.Pen(secco, hw))
        dc.DrawLines(((seccx, seccy), secpos))
        self._drawClockTicks2(
            dc, seccx, seccy, self.maxlen * seclen, secco)  # , "black" )

        dc.SetBrush(wx.Brush(secco, wx.SOLID))
        dc.DrawCircle(seccx, seccy, self.adj / 10)

    def _drawHands(self, dc):
        #~ mst = time.time()
        #~ self.lt = time.localtime(mst)
        #~ ms = int((mst - int(mst))*1000)
        self._drawclockhands(dc, time.time(),  time.localtime().tm_wday)

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bgbitmap, 0, 0)

        wdposx, wdposy = self.getCenterPos(False)
        dc.SetFont(self.bigfont)
        datetext = strftime("%H:%M:%S", localtime())
        self._printText(dc, datetext, wdposx, wdposy - self.adj * 5)
        dc.SetFont(self.calfont)
        datetext = strftime("%Y-%m-%d", localtime())
        self._printText(dc, datetext, wdposx, wdposy - self.adj * 2)
        self._drawCalendar(dc)
        self._drawHands(dc)

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, size=(640, 480))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
