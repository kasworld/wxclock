#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    wximageclock ver 3.10

    Copyright 2010,2011 kasw <kasworld@gmail.com>

"""

import sys
import os.path
# sys.path.append(os.path.join( os.path.split( os.path.dirname(os.path.abspath(sys.argv[0])) )[0] , 'kaswlib' ))
from kaswxlib import *

import os
import sys
import os.path
import time
import math
import random
import wx
from time import strftime
import time
import datetime
import calendar
import pprint
import math
import exceptions
wx.InitAllImageHandlers()


def getProgress(minstart, maxstop, progress):
    return int(minstart + (maxstop - minstart) * (math.sin(math.pi * progress - math.pi / 2) + 1) / 2)


def makeSizeList2(slist):
    """slist: ( ( w,h) , optional count , ( w2,h2) , optional count2 , ( w3,h3 ) , optional count3 , ... ( wn,hn ) ) """
    rtn = []
    for i, carg in zip(range(len(slist)), slist):
        if type(carg) is int:
            if type(slist[i - 1]) in (list, tuple) and type(slist[i + 1]) in (list, tuple):
                for j in range(1, carg):
                    rtn.append((getProgress(slist[i - 1][0], slist[i + 1][0],  float(j) / carg),
                                getProgress(slist[i - 1][1], slist[i + 1][1],  float(j) / carg))
                               )
            else:
                raise exceptions.TypeError('invalid type in list ')
        elif type(carg) in (list, tuple):
            rtn.append(carg)
        else:
            raise exceptions.TypeError(
                'invalid type %s type must list or tuple' % type(carg))
    return rtn


class kclock(wx.Frame, FPSlogic):

    def __init__(self, *args, **kwds):
        self.fold = True
        self.foldstep = 0
        self.winSizeList = makeSizeList2(
            ((512, 32),  10,  (512, 16 * (20 + worldTime.getCount()))))
        kwds["size"] = self.winSizeList[self.foldstep]
        kwds["style"] = wx.STAY_ON_TOP | wx.NO_BORDER | wx.FRAME_TOOL_WINDOW
        wx.Frame.__init__(self, *args, **kwds)
        self.SetBackgroundColour(wx.Colour(0xff, 0xff, 0xff))
        self.SetMinSize(self.winSizeList[0])
        self.SetMaxSize(self.winSizeList[-1])

        self.FPSTimerInit(60)
        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)

        self.Bind(wx.EVT_LEFT_DOWN,     self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,       self.OnLeftUp)
        self.Bind(wx.EVT_ENTER_WINDOW,   self.OnEnterMouse)
        self.Bind(wx.EVT_LEAVE_WINDOW,     self.OnLeaveMouse)
        self.Bind(wx.EVT_MOTION,        self.OnMouseMove)
        self.Bind(wx.EVT_RIGHT_UP,      self.OnExit)

        self.registerRepeatFn(self.doTimeUpdate, 1)

    def _OnSize(self, evt):
        self.clientsize = evt.GetSize()  # self.GetClientSizeTuple()
        if self.clientsize[0] < 1 or self.clientsize[1] < 1:
            return
        # min(self.clientsize[0]/6,self.clientsize[1]/3)
        self.adj = self.clientsize[0] / 32
        self.calfont = wx.Font(self.adj * 0.9, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.bigfont = wx.Font(self.adj * 1.9, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.midfont = wx.Font(self.adj * 1.2, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2

    def doFPSlogic(self, thisframe):
        if self.fold and self.foldstep > 0:
            self.foldstep -= 1
            self.SetSize(self.winSizeList[self.foldstep])
        elif not self.fold and self.foldstep < len(self.winSizeList) - 1:
            self.foldstep += 1
            self.SetSize(self.winSizeList[self.foldstep])

    def doTimeUpdate(self, repeatinfo):
        self.Refresh(False)

    def OnExit(self, evt):
        self.Close()

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        x, y = self.ClientToScreen(evt.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnEnterMouse(self, evt):
        self.fold = False
        self.SetSize(self.winSizeList[self.foldstep])

    def OnLeaveMouse(self, evt):
        self.fold = True
        self.SetSize(self.winSizeList[self.foldstep])

    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            x, y = self.ClientToScreen(evt.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)

    def _OnDestroyWindow(self, evt):
        self.FPSTimerDel()

    def _printText(self, dc, pstr, x, y, r=0, g=0, b=0):
        w, h = dc.GetTextExtent(pstr)
        dc.SetTextForeground(
            wx.Colour(r, g, b)
        )
        dc.DrawText(pstr,  x - w / 2, y - h / 2)

    def drawCalendar(self, dc, today):
        dc.SetPen(wx.Pen(wx.Colour(0x7f, 0x7f, 0x7f), 0))
        dc.SetBrush(wx.Brush(wx.Colour(0xaf, 0xaf, 0xaf), wx.SOLID))
        dc.DrawRectangle(0, self.adj * 3, self.clientsize[0], 14 * self.adj)

        calobj = calendar.Calendar(6)
        wds = list('SMTWTFS')
        for i in range(7):
            ccc = (0, 0, 0)
            if i == 6:
                ccc = (0, 0, 0xff)
            if i == 0:
                ccc = (0xff, 0, 0)
            self._printText(dc, wds[i],
                            self.adj * 2 + i * self.adj * 4.5,
                            self.adj * 4,
                            *ccc)
        stday = today.date() - datetime.timedelta(7 * 2 + today.weekday() + 1)
        enday = today.date() + datetime.timedelta(7 * 4 - today.weekday() - 1)
        x = y = 0
        cday = stday
        while enday > cday:
            ccc = (0, 0, 0)
            if cday.weekday() == 5:
                ccc = (0, 0, 0xff)
            if cday.weekday() == 6:
                ccc = (0xff, 0, 0)
            if cday.day == today.day:
                ccc = (0, 0xaf, 0)
            self._printText(dc, str(cday.day),
                            self.adj * 2 + (x % 7) * self.adj * 4.5,
                            self.adj * 6 + (x / 7) * self.adj * 2,
                            *ccc)
            # print x,self.adj*6 + (x/7) * self.adj*2, cday
            x += 1
            cday += datetime.timedelta(1)

    def _OnPaint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetPen(wx.Pen(wx.Colour(0x7f, 0x7f, 0x7f), 0))
        dc.DrawRectangle(0, 0, self.clientsize[0], self.clientsize[1])

        cper = getCpuPer() / 100.0
        dc.SetPen(wx.Pen(wx.Colour(0x7f, 0x7f, 0x7f), 0))
        dc.SetBrush(
            wx.Brush(wx.Colour(0xff, 0xff * (1 - cper), 0xff * (1 - cper)), wx.SOLID))
        dc.DrawRectangle(0, 0, self.clientsize[0] * cper, 1.1 * self.adj)

        minfo = meminfo()
        mtot, mfree, mbuf, mcach = minfo['MemTotal'], minfo[
            'MemFree'], minfo['Buffers'], minfo['Cached']
        mper = 1 - (mfree + mbuf + mcach) * 1.0 / mtot
        dc.SetPen(wx.Pen(wx.Colour(0x7f, 0x7f, 0x7f), 0))
        dc.SetBrush(wx.Brush(wx.Colour(0xff * (1 - mper),
                                       0xff, 0xaf * (1 - mper)), wx.SOLID))
        dc.DrawRectangle(0, 1.1 * self.adj,
                         self.clientsize[0] * mper, 1.1 * self.adj)

        #today = time.localtime()
        today = datetime.datetime.today()

        dc.SetFont(self.bigfont)
        #datetext = strftime("%H:%M:%S", today)
        self._printText(dc, today.strftime("%H:%M:%S"),
                        self.adj * 6, 1.1 * self.adj)

        dc.SetFont(self.calfont)
        #datetext = strftime("%a %Y-%m-%d", today)
        self._printText(dc, today.strftime("%a %Y-%m-%d"),
                        self.adj * 22, 0.55 * self.adj)

        datetext = "%s:%s" % (myHostname(), ','.join(getMyIPAddress()))
        self._printText(dc, datetext, self.adj * 22, self.adj * 1.6)

        #datetext = "%5.1f%% %4.1f%%" % (getCpuPer(), mper )
        #self._printText( dc,datetext,self.adj*26 , 0.55*self.adj)

        if self.foldstep > 0:
            dc.SetFont(self.midfont)

            for i in range(worldTime.getCount()):
                #datetext = clocks[i][0] + clocks[i][1]( clocks[i][2]).strftime(datetimeformatstring )
                datetext = worldTime.getStr(i)
                self._printText(dc, datetext, self.adj * 16,
                                self.adj * (18 + i * 2), 0x6f, 0x6f, 0x6f)

            self.drawCalendar(dc, today)


def rundigiclock():
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = kclock(None, -1, pos=(100, 100))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()


if __name__ == "__main__":
    rundigiclock()
    # print getMyIPAddress()
