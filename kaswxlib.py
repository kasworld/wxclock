#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    kasworld's wxpython lib ver 1.3.1

    Copyright 2011,2013 kasw <kasworld@gmail.com>

    usage is
import sys,os.path
srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(os.path.join( os.path.split( srcdir)[0] , 'kaswlib' ))
from kaswlib import *

"""

import wx
import time
import re
import datetime
import commands
import socket
import math
import os
import cmath
import struct
import logging
import pprint
import random
import itertools
import functools
import string

wx.InitAllImageHandlers()

import sys
import os.path
srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(os.path.join(os.path.split(srcdir)[0], 'kaswlib'))
import kaswlib


def loadBitmap2MemoryDCArray(bitmapfilename, xslicenum=1, yslicenum=1,
                             totalslice=10000,  yfirst=True, reverse=False, addreverse=False):
    rtn = []
    fullbitmap = wx.Bitmap(bitmapfilename)
    dcsize = fullbitmap.GetSize()
    w, h = dcsize[0] / xslicenum, dcsize[1] / yslicenum
    if yfirst:
        for x in range(xslicenum):
            for y in range(yslicenum):
                rtn.append(wx.MemoryDC(
                    fullbitmap.GetSubBitmap(wx.Rect(x * w, y * h, w, h))))
    else:
        for y in range(yslicenum):
            for x in range(xslicenum):
                rtn.append(wx.MemoryDC(
                    fullbitmap.GetSubBitmap(wx.Rect(x * w, y * h, w, h))))
    totalslice = min(xslicenum * yslicenum, totalslice)
    rtn = rtn[:totalslice]
    if reverse:
        rtn.reverse()
    if addreverse:
        rrtn = rtn[:]
        rrtn.reverse()
        rtn += rrtn
    return rtn


def loadDirfiles2MemoryDCArray(dirname, reverse=False, addreverse=False):
    rtn = []
    filenames = sorted(os.listdir(dirname), reverse=reverse)
    for a in filenames:
        rtn.append(wx.MemoryDC(wx.Bitmap(dirname + "/" + a)))
    if addreverse:
        rrtn = rtn[:]
        rrtn.reverse()
        rtn += rrtn
    return rtn


def makeRotatedImage(image, angle):
    rad = math.radians(-angle)
    xlen, ylen = image.GetWidth(), image.GetHeight()
    #offset = wx.Point()
    # ,wx.Point(xlen,ylen) )
    rimage = image.Rotate(rad, (xlen / 2, ylen / 2), True)
    # rimage =  image.Rotate( rad, (0,0) ,True) #,wx.Point() )
    xnlen, ynlen = rimage.GetWidth(), rimage.GetHeight()
    rsimage = rimage.Size(
        (xlen, ylen), (-(xnlen - xlen) / 2, -(ynlen - ylen) / 2))
    # print angle, xlen , ylen , xnlen , ynlen , rsimage.GetWidth() ,
    # rsimage.GetHeight()
    return rsimage


def loadBitmap2RotatedMemoryDCArray(imagefilename, rangearg=(0, 360, 10),
                                    reverse=False, addreverse=False):
    rtn = []
    fullimage = wx.Bitmap(imagefilename).ConvertToImage()
    for a in range(*rangearg):
        rtn.append(wx.MemoryDC(
            makeRotatedImage(fullimage, a).ConvertToBitmap()
        ))
    if reverse:
        rtn.reverse()
    if addreverse:
        rrtn = rtn[:]
        rrtn.reverse()
        rtn += rrtn
    return rtn


class GameResource(object):

    def __init__(self, dirname):
        self.resourcedir = dirname
        self.rcsdict = {}

    def getcwdfilepath(self, filename):
        return os.path.join(srcdir, self.resourcedir, filename)

    def loadBitmap2MemoryDCArray(self, name, *args, **kwds):
        key = (name, args, str(kwds))
        if not self.rcsdict.get(key, None):
            self.rcsdict[key] = loadBitmap2MemoryDCArray(
                self.getcwdfilepath(name), *args, **kwds)
        return self.rcsdict[key]

    def loadDirfiles2MemoryDCArray(self, name, *args, **kwds):
        key = (name, args, str(kwds))
        if not self.rcsdict.get(key, None):
            self.rcsdict[key] = loadDirfiles2MemoryDCArray(
                self.getcwdfilepath(name), *args, **kwds)
        return self.rcsdict[key]

    def loadBitmap2RotatedMemoryDCArray(self, name, *args, **kwds):
        key = (name, args, str(kwds))
        if not self.rcsdict.get(key, None):
            self.rcsdict[key] = loadBitmap2RotatedMemoryDCArray(
                self.getcwdfilepath(name), *args, **kwds)
        return self.rcsdict[key]


class FPSlogic():

    def FPSTimerInit(self, maxFPS=70):
        self.maxFPS = maxFPS
        self.Bind(wx.EVT_TIMER, self.FPSTimer)
        self.timer = wx.Timer(self)
        self.repeatingcalldict = {}
        self.pause = False
        self.statFPS = kaswlib.Statistics()
        self.timer.Start(1000 / self.maxFPS, oneShot=True)
        self.frames = [time.time()]
        self.first = True

    def registerRepeatFn(self, fn, dursec):
        """
            function signature
            def repeatFn(self,repeatinfo):
            repeatinfo is {
            "dursec" : dursec ,
            "oldtime" : time.time() ,
            "starttime" : time.time(),
            "repeatcount":0 }
        """
        self.repeatingcalldict[fn] = {
            "dursec": dursec,
            "oldtime": time.time(),
            "starttime": time.time(),
            "repeatcount": 0}
        return self

    def unRegisterRepeatFn(self, fn):
        return self.repeatingcalldict.pop(fn, [])

    def FPSTimer(self, evt):
        thistime = time.time()
        self.frames.append(thistime)
        difftime = self.frames[-1] - self.frames[-2]

        while(self.frames[-1] - self.frames[0] > 1):
            del self.frames[0]

        if len(self.frames) > 1:
            fps = len(self.frames) / (self.frames[-1] - self.frames[0])
        else:
            fps = 0
        if self.first:
            self.first = False
        else:
            self.statFPS.update(fps)

        frameinfo = {
            "ThisFPS": 1 / difftime,
            "sec":  difftime,
            "FPS": fps,
            'stat': self.statFPS
        }

        if not self.pause:
            self.doFPSlogic(frameinfo)
        try :
            for fn, d in self.repeatingcalldict.iteritems():
                if thistime - d["oldtime"] > d["dursec"]:
                    self.repeatingcalldict[fn]["oldtime"] = thistime
                    self.repeatingcalldict[fn]["repeatcount"] += 1
                    fn(d)
        except Exception as e:
            print e

        idealframems = 1000 / self.maxFPS
        thisframems = (time.time() - thistime) * 1000
        thisframedelay = idealframems - thisframems
        if thisframedelay < 1:
            thisframedelay = 1
        self.timer.Start(thisframedelay, oneShot=True)

    def FPSTimerDel(self):
        self.timer.Stop()
        #del self.timer

    def doFPSlogic(self, thisframe):
        pass

if __name__ == "__main__":
    pass
