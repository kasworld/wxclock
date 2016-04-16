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
    depth = max(2, depth)
    w, h = dc.GetTextExtent(pstr)
    for i in range(0, depth):
        cr = int(i * 255. / (depth - 1))
        dc.SetTextForeground(
            wx.Colour(cr if r else cr * .8, cr if g else cr * .8,
                      cr if b else cr * .8, 0x80)
        )
        dc.DrawText(pstr,  x - w / 2 + depth - i,  y - h / 2 + depth - i)


def makeCalendarImg(bx, by):
    bitMap = wx.EmptyBitmap(bx, by)
    calfont = wx.Font(min(bx / 16, by / 10), wx.SWISS, wx.NORMAL, wx.NORMAL)

    dc = wx.MemoryDC()
    dc.SelectObject(bitMap)
    dc.SetBackground(wx.Brush("black", wx.SOLID))
    dc.Clear()
    dc.SetFont(calfont)

    # w, h = dc.GetTextExtent("00")
    w = bx / 7
    h = by / 7
    depth = min(bx, by) / 100

    disptext = "{0:%Y-%m-%d}".format(datetime.datetime.now())
    drawTextRaw2DC(dc, disptext, bx / 3, h / 2, depth=depth)

    calday = calendar.Calendar(6).monthdays2calendar(
        time.localtime()[0], time.localtime()[1])
    """[[(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)], [(5, 0), (6, 1), (7, 2), (8, 3), (9, 4), (10, 5), (11, 6)], [(12, 0), (13, 1), (14, 2), (15, 3), (16, 4), (17, 5), (18, 6)], [(19, 0), (20, 1), (21, 2), (22, 3), (23, 4), (24, 5), (25, 6)], [(26, 0), (27, 1), (28, 2), (29, 3), (30, 4), (31, 5), (0, 6)]]"""
    wwy = 1.5
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
                               posx * w,
                               wwy * h,
                               *ccc, depth=depth)
            posx += 1
        wwy += 1
    dc.SelectObject(wx.NullBitmap)
    return bitMap


def makeDigiClockImg(bx, by, smallFont, bigFont):
    # bigfont = wx.Font(min(bx / 6, by / 4), wx.SWISS, wx.NORMAL, wx.NORMAL)
    # smallfont = wx.Font(min(bx / 32, by / 20), wx.SWISS, wx.NORMAL, wx.NORMAL)

    bitMap = wx.EmptyBitmap(bx, by)
    depth = min(bx, by) / 50

    dc = wx.MemoryDC()
    dc.SelectObject(bitMap)
    dc.SetBackground(wx.Brush("black", wx.SOLID))
    dc.Clear()

    dc.SetFont(bigFont)
    datetext = time.strftime("%H:%M:%S", time.localtime())
    drawTextRaw2DC(dc, datetext, bx / 2, by / 4, depth=depth)

    dc.SetFont(smallFont)
    disptext = "{0:5.1f}MHz {1:4.1f}C".format(
        kaswlib.CPUClock() / 1000, kaswlib.CPUTemp())
    drawTextRaw2DC(dc, disptext, bx / 2, by / 2, depth=depth / 4)

    dc.SelectObject(wx.NullBitmap)
    return bitMap


def getBGImageFilename():
    if len(sys.argv) == 2:
        imageBaseDirname = sys.argv[1]
    else:
        basedirname = os.path.dirname(os.path.abspath(__file__))
        imageBaseDirname = os.path.join(basedirname, "bgimages")
    imageFileNames = []
    for root, dirs, files in os.walk(imageBaseDirname):
        imageFileNames.extend(
            [os.path.join(root, f) for f in
             filter(lambda f: f[-4:].lower() in ['.jpg', '.bmp', '.png'],
                    files)]
        )
    random.shuffle(imageFileNames)
    return imageFileNames


class kclock(wx.Frame, kaswxlib.FPSlogic):

    def doFPSlogic(self, thisframe):
        self.Refresh(False)

        thistime = time.localtime()
        if self.lastTime[3] != thistime[3]:
            self.doHourly()
        if self.lastTime[4] != thistime[4]:
            self.doMinutely()
        if self.lastTime[5] != thistime[5]:
            self.doSecondly()
        self.lastTime = thistime

    def doSecondly(self):
        datetext = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.SetTitle(datetext)
        self.digiClockBitMap = makeDigiClockImg(
            self.Size[0] / 2, self.Size[1] / 2, self.smallFont, self.bigFont)

    def doMinutely(self):
        pass

    def doHourly(self):
        self.calBitMap = makeCalendarImg(self.Size[0] / 2, self.Size[1] / 2)

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE  # | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.lastTime = time.localtime()
        self.showClock = True
        self.isFullscreen = True
        self.ShowFullScreen(self.isFullscreen)
        self.rawBGImage = None
        self.imageFileNames = getBGImageFilename()
        self.loadBGImage()

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self._OnSize(None)
        self.FPSTimerInit(60)

    def _OnSize(self, evt):
        if self.Size[0] < 1 or self.Size[1] < 1:
            return

        bx, by = self.Size[0] / 2, self.Size[1] / 2
        self.bigFont = wx.Font(min(bx / 6, by / 3),
                               wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.smallFont = wx.Font(
            min(bx / 32, by / 20), wx.SWISS, wx.NORMAL, wx.NORMAL)

        self.digiClockBitMap = makeDigiClockImg(
            bx, by, self.smallFont, self.bigFont)

        self.calBitMap = makeCalendarImg(self.Size[0] / 2, self.Size[1] / 2)

        if self.rawBGImage:
            self.bgBitmap = self.rawBGImage.Scale(
                self.Size[0], self.Size[1]).ConvertToBitmap()
        else:
            self.bgBitmap = wx.EmptyBitmap(*self.Size)

        self.maxLen = min(self.Size[0], self.Size[1]) / 2

        pdc = wx.BufferedDC(None, self.bgBitmap)
        if not self.rawBGImage:
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
            self.isFullscreen = not self.isFullscreen
            self.ShowFullScreen(self.isFullscreen)
            self._OnSize(None)

    def _OnDestroyWindow(self, evt):
        self.timer.Stop()
        del self.timer

    def loadBGImage(self):
        self.imageloadtime = time.time()
        if self.imageFileNames:
            imagename = self.imageFileNames.pop()
        try:
            f = open(imagename, "rb")
            f.close()
            self.rawBGImage = wx.Image(imagename)
            self.imageFileNames.insert(0, imagename)
        except:
            self.rawBGImage = None

    def getCenterPos(self, even=True):
        mst = time.time()
        lt = time.localtime(mst)
        ms = int((mst - int(mst)) * 1000)

        centerlen = self.maxLen + \
            (self.Size[0] - self.maxLen * 2) * \
            (lt.tm_sec * 100 + ms / 10.0) / 6000.0
        if lt.tm_min % 2:
            rtnx = self.Size[0] - centerlen if even else centerlen
        else:
            rtnx = centerlen if even else self.Size[0] - centerlen

        centerlen = self.maxLen + \
            (self.Size[1] - self.maxLen * 2) * \
            (lt.tm_sec * 100 + ms / 10.0) / 6000.0
        if lt.tm_min % 2:
            rtny = self.Size[1] - centerlen if even else centerlen
        else:
            rtny = centerlen if even else self.Size[1] - centerlen

        return rtnx, rtny

    def drawAnalogClock(self, dc, mst):
        wdposx, wdposy = self.getCenterPos(True)

        hourangle, minangle, secangle = getHMSAngles(mst)

        hourco = wx.Colour(0xff, 0x40, 0x40)
        minco = wx.Colour(0, 0xc0, 0)
        secco = wx.Colour(0x40, 0x40, 0xff)

        if True:
            hourlen, minlen, seclen = 0.6, 0.8, 1.0

            seccx, seccy = wdposx, wdposy
            mincx, mincy = getPoint2(
                seccx, seccy, self.maxLen, secangle, 0.2)
            hourcx, hourcy = getPoint2(
                mincx, mincy, self.maxLen, minangle, 0.2)
        else:
            hourlen, minlen, seclen = 1.0, 0.8, 0.6

            hourcx, hourcy = wdposx, wdposy
            mincx, mincy = getPoint2(
                hourcx, hourcy, self.maxLen, hourangle, 0.2)
            seccx, seccy = getPoint2(
                mincx, mincy, self.maxLen, minangle, 0.2)

        drawClock1(dc, hourcx, hourcy, hourangle,
                   self.maxLen, hourlen, hourco)  # , "black" )

        drawClock1(dc, mincx, mincy, minangle,
                   self.maxLen, minlen, minco)  # , "black" )

        drawClock1(dc, seccx, seccy, secangle,
                   self.maxLen, seclen, secco)  # , "black" )

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bgBitmap, 0, 0)

        wdposx, wdposy = self.getCenterPos(False)
        dc.DrawBitmap(self.digiClockBitMap, wdposx - self.Size[0] / 4, 0)
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
