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
import calendar
import time
import datetime

wx.InitAllImageHandlers()


srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(os.path.join(os.path.split(srcdir)[0], 'kaswlib'))
import kaswxlib
import kaswlib


def getHMSAngles(mst):
    """ clock hands angle
    mst = time.time()"""

    lt = time.localtime(mst)
    ms = mst - int(mst)
    return lt[3] * 30.0 + lt[4] / 2.0 + lt[5] / 120.0, lt[4] * 6.0 + lt[5] / 10.0 + ms / 10, lt[5] * 6.0 + ms * 6


def getPoint2(cx, cy, r, angle, length):
    rad = math.radians(angle + 270)
    l = r * length
    return cx + l * math.cos(rad), cy + l * math.sin(rad)


def drawClock1(dc, cx, cy, angle, maxlen, rate, c1, c2=None):

    pos = getPoint2(cx, cy, maxlen, angle, rate)
    dc.SetPen(wx.Pen(c1, maxlen / 100 * rate))
    dc.DrawLines(((cx, cy), pos))

    r = maxlen * rate
    tw = r / 150

    if c2:
        td = max(tw / 2, 1)
        dc.SetPen(wx.Pen(c2, tw))
        for a in range(0, 360):
            # c = (255,255,255)
            p1 = getPoint2(cx, cy, r, a, 1.0)
            if a % 30 == 0:  # hour
                p2 = getPoint2(cx, cy, r, a, 0.90)
            elif a % 6 == 0:  # min & sec
                p2 = getPoint2(cx, cy, r, a, 0.95)
            else:  # 1 degree
                p2 = getPoint2(cx, cy, r, a, 0.98)
            dc.DrawLine(p1[0] + td, p1[1] + td, p2[0] + td, p2[1] + td)

    dc.SetPen(wx.Pen(c1, tw))
    for a in range(0, 360):
        # c = (255,255,255)
        p1 = getPoint2(cx, cy, r, a, 1.0)
        if a % 30 == 0:  # hour
            p2 = getPoint2(cx, cy, r, a, 0.90)
        elif a % 6 == 0:  # min & sec
            p2 = getPoint2(cx, cy, r, a, 0.95)
        else:  # 1 degree
            p2 = getPoint2(cx, cy, r, a, 0.98)
        dc.DrawLine(p1[0], p1[1], p2[0], p2[1])

    dc.SetBrush(wx.Brush(c1, wx.SOLID))
    dc.DrawCircle(cx, cy, maxlen / 50)


def drawTextRaw2DC(dc, pstr, x, y, r=True, g=True, b=True, depth=2):
    w, h = dc.GetTextExtent(pstr)
    for i in range(0, depth):
        cr = int(i * 255. / (depth - 1))
        dc.SetTextForeground(
            wx.Colour(cr if r else cr * .8, cr if g else cr * .8,
                      cr if b else cr * .8, 0x80)
        )
        dc.DrawText(pstr,  x - w / 2 + depth - i,  y - h / 2 + depth - i)


def makeCalendarImg(bx, by):
    calBitMap = wx.EmptyBitmap(bx, by)
    calfont = wx.Font(bx / 20, wx.SWISS, wx.NORMAL, wx.NORMAL)

    dc = wx.MemoryDC()
    dc.SelectObject(calBitMap)
    dc.SetBackground(wx.Brush("black", wx.SOLID))
    dc.Clear()
    dc.SetFont(calfont)

    w, h = dc.GetTextExtent("00")

    disptext = "{0:%Y-%m-%d}".format(datetime.datetime.now())
    drawTextRaw2DC(dc, disptext, bx / 3, h / 2)

    calday = calendar.Calendar(6).monthdays2calendar(
        time.localtime()[0], time.localtime()[1])
    """[[(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)], [(5, 0), (6, 1), (7, 2), (8, 3), (9, 4), (10, 5), (11, 6)], [(12, 0), (13, 1), (14, 2), (15, 3), (16, 4), (17, 5), (18, 6)], [(19, 0), (20, 1), (21, 2), (22, 3), (23, 4), (24, 5), (25, 6)], [(26, 0), (27, 1), (28, 2), (29, 3), (30, 4), (31, 5), (0, 6)]]"""
    wwy = 1.4
    for wwl in calday:
        posx = 0.5
        for wwx in wwl:
            # pos is wd[1] , wwc
            if (wwx[0]):
                ccc = (True, True, True)
                if wwx[1] == 5:
                    ccc = (False, True, True)
                if wwx[1] == 6:
                    ccc = (True, False, False)
                if wwx[0] == time.localtime()[2]:
                    ccc = (False, True, False)
                drawTextRaw2DC(dc, str(wwx[0]),
                               posx * w * 1.5,
                               wwy * h * 1.1,
                               *ccc)
            posx += 1
        wwy += 1
    dc.SelectObject(wx.NullBitmap)
    return calBitMap


class kclock(wx.Frame, kaswxlib.FPSlogic):

    def doFPSlogic(self, thisframe):
        self.Refresh(False)

        thistime = time.localtime()
        if self.LastTime[3] != thistime[3]:
            self.doHourly()
        if self.LastTime[4] != thistime[4]:
            self.doMinutely()
        if self.LastTime[5] != thistime[5]:
            self.doSecondly()
        self.LastTime = thistime

    def doSecondly(self):
        self.getSensor()
        datetext = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.SetTitle(datetext)

    def doMinutely(self):
        pass

    def doHourly(self):
        self.calBitMap = makeCalendarImg(self.Size[0] / 2, self.Size[1] / 2)

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE  # | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.fps = 60
        self.CPUClock = 0
        self.CPUTemp = 0
        self.LastTime = time.localtime()
        self.showClock = True
        self.isfullscreen = True
        self.ShowFullScreen(self.isfullscreen)
        self.rawbgimage = None
        self.getBGImageFilename()
        self.loadBGImage()

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self._OnSize(None)
        self.FPSTimerInit(self.fps)

    def getSensor(self):
        self.CPUClock = kaswlib.CPUClock() / 1000
        self.CPUTemp = kaswlib.CPUTemp()

    def _OnSize(self, evt):
        size = self.GetClientSize()
        if size.x < 1 or size.y < 1:
            return

        self._recalcCoords(size)
        self._drawBox()

    def _drawBox(self):
        """Draws clock face and tick marks onto the faceBitmap."""
        pdc = wx.BufferedDC(None, self.bgBitmap)
        if not self.rawbgimage:
            pdc.SetBackground(wx.Brush("black", wx.SOLID))
            pdc.Clear()
        else:
            pdc.DrawBitmap(self.bgBitmap, 0, 0)

    def OnMouse(self, evt):
        if evt.LeftIsDown():
            self.Close()
        if evt.MiddleIsDown():
            self.showClock = not self.showClock
        if evt.RightDown():
            self.isfullscreen = not self.isfullscreen
            self.ShowFullScreen(self.isfullscreen)
            self._OnSize(None)

    def _OnDestroyWindow(self, evt):
        self.timer.Stop()
        del self.timer

    def getBGImageFilename(self):
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

    def loadBGImage(self):
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

    def resizeFixAspect(self, image, wx, wy):
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
        self.size = size
        if self.rawbgimage:
            self.bgBitmap = self.resizeFixAspect(
                self.rawbgimage, size.width, size.height).ConvertToBitmap()
        else:
            self.bgBitmap = wx.EmptyBitmap(*size.Get())
        self.clientsize = self.GetClientSizeTuple()
        self.adj = min(self.clientsize[0] / 10, self.clientsize[1] / 10)
        self.smallfont = wx.Font(self.adj / 4, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.bigfont = wx.Font(self.adj * 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2
        if self.rawbgimage:
            self.maxlen = min(self.mcenterx, self.mcentery) / 2
        else:
            self.maxlen = min(self.mcenterx, self.mcentery)
        self.mcenterx = self.clientsize[0] - self.maxlen
        self.mcentery = self.clientsize[1] - self.maxlen

        self.calBitMap = makeCalendarImg(self.Size[0] / 2, self.Size[1] / 2)

    def _printText(self, dc, pstr, x, y, r=True, g=True, b=True, depth=2):
        w, h = dc.GetTextExtent(pstr)
        for i in range(0, depth):
            cr = int(i * 255. / (depth - 1))
            dc.SetTextForeground(
                wx.Colour(cr if r else cr * .8, cr if g else cr * .8,
                          cr if b else cr * .8, 0x80)
            )
            dc.DrawText(pstr, min(self.clientsize[0] - w, max(0, -w / 2 + x + depth - i)),
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

    def drawAnalogClock(self, dc, mst):
        wdposx, wdposy = self.getCenterPos(True)

        hourangle, minangle, secangle = getHMSAngles(mst)

        hourco = wx.Colour(0xff, 0x40, 0x40)
        minco = wx.Colour(0, 0xc0, 0)
        secco = wx.Colour(0x40, 0x40, 0xff)

        if True:
            hourlen, minlen, seclen = 0.6, 0.8, 1.0

            seccx, seccy = wdposx, wdposy  # self.mcentery
            mincx, mincy = getPoint2(
                seccx, seccy, self.maxlen, secangle, 0.2)
            hourcx, hourcy = getPoint2(
                mincx, mincy, self.maxlen, minangle, 0.2)
        else:
            hourlen, minlen, seclen = 1.0, 0.8, 0.6

            hourcx, hourcy = wdposx, wdposy  # self.mcentery
            mincx, mincy = getPoint2(
                hourcx, hourcy, self.maxlen, hourangle, 0.2)
            seccx, seccy = getPoint2(
                mincx, mincy, self.maxlen, minangle, 0.2)

        drawClock1(dc, hourcx, hourcy, hourangle,
                   self.maxlen, hourlen, hourco)  # , "black" )

        drawClock1(dc, mincx, mincy, minangle,
                   self.maxlen, minlen, minco)  # , "black" )

        drawClock1(dc, seccx, seccy, secangle,
                   self.maxlen, seclen, secco)  # , "black" )

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bgBitmap, 0, 0)

        wdposx, wdposy = self.getCenterPos(False)
        dc.SetFont(self.bigfont)
        datetext = time.strftime("%H:%M:%S", time.localtime())
        self._printText(dc, datetext, wdposx, wdposy - self.adj * 5)

        dc.SetFont(self.smallfont)
        disptext = "{0:5.1f}MHz {1:4.1f}C".format(
            self.CPUClock, self.CPUTemp)
        self._printText(dc, disptext, wdposx, wdposy - self.adj * 1.5)

        wdposx, wdposy = self.getCenterPos(False)
        dc.DrawBitmap(self.calBitMap, wdposx - self.Size[0] / 4, wdposy)

        if self.showClock:
            self.drawAnalogClock(dc, time.time())


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, size=(640, 480))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
