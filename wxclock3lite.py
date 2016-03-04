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

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE  # | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.fps = 5
        self.isfullscreen = True
        self.ShowFullScreen(self.isfullscreen)

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
        self.bgbitmap = wx.EmptyBitmap(*size.Get())
        self.clientsize = self.GetClientSizeTuple()
        self.adj = min(self.clientsize[0] / 10, self.clientsize[1] / 10)
        self.calfont = wx.Font(self.adj / 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.bigfont = wx.Font(self.adj * 2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2
        self.maxlen = min(self.mcenterx, self.mcentery)
        self.mcenterx = self.clientsize[0] - self.maxlen
        self.mcentery = self.clientsize[1] - self.maxlen

    def _printText(self, dc, pstr, x, y, r=True, g=True, b=True, depth=2):
        w, h = dc.GetTextExtent(pstr)
        for i in range(0, depth):
            cr = int(i * 255. / (depth - 1))
            dc.SetTextForeground(
                wx.Colour(cr if r else cr * .7, cr if g else cr * .7,
                          cr if b else cr * .7, 0x80)
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
        pdc.SetBackground(wx.Brush("black", wx.SOLID))
        pdc.Clear()
        # self._drawCalendar(pdc)

    def _OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bgbitmap, 0, 0)

        wdposx, wdposy = self.getCenterPos(False)
        dc.SetFont(self.bigfont)
        datetext = strftime("%H:%M:%S", localtime())
        self._printText(dc, datetext, wdposx, wdposy - self.adj * 5)
        dc.SetFont(self.calfont)
        datetext = strftime("%Y-%m-%d", localtime())
        self._printText(dc, datetext, wdposx, wdposy - self.adj * 1)
        self._drawCalendar(dc)

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, size=(640, 480))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
