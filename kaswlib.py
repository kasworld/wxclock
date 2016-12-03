#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    kasworld's python lib ver 2.0.0

    Copyright 2011,2012,2013 kasw <kasworld@gmail.com>

    modified for python 2.x and 3.x

    usage is
import sys,os.path
srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.extend( [
    os.path.join( srcdir , 'kaswlib' ),
    os.path.join( os.path.split( srcdir)[0] , 'kaswlib' ),
    ])
try :
    from kaswlib import *
except :
    print 'kaswlib import fail'
    pass

"""

import sys
if sys.version_info[0] < 3:
    range = xrange

import time
import re
import datetime
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
import sys
import pwd
import os.path
srcdir = os.path.dirname(os.path.abspath(sys.argv[0]))
# sys.path.append(os.path.join( os.path.split( srcdir)[0] , 'kaswlib' ))


def getcwdfilepath(filename):
    return os.path.join(srcdir, filename)


"""
    # cmath compatible functions
    @staticmethod
    def rect( l, a ):
        return Vector2( l*math.cos(a) , l*math.sin(a) )
    def phase( self):
        return math.atan2( self.y , self.x )
    def polar(self):
        return abs(self), self.phase()
    def negX( self):
        return Vector2( -self.x , self.y )
    def negY( self):
        return Vector2( self.x , -self.y )
    def addAngle( self , angle ):
        return Vector2.rect( abs(self ) , self.phase() + angle )
    def rotate( self, center, angle ):
        vt = self - center
        return vt.addAngle(angle) + center
"""


def frozen(set):
    """Raise an error when trying to set an undeclared name, or when calling
       from a method other than Frozen.__init__ or the __init__ method of
       a class derived from Frozen"""

    def set_attr(self, name, value):
        import sys
        if hasattr(self, name):  # If attribute already exists, simply set it
            set(self, name, value)
            return
        # Allow __setattr__ calls in __init__ calls of proper object types
        elif sys._getframe(1).f_code.co_name is '__init__':
            for k, v in sys._getframe(1).f_locals.items():
                if k == "self" and isinstance(v, self.__class__):
                    set(self, name, value)
                    return
        raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


class Frozen(object):

    """Subclasses of Frozen are frozen, i.e. it is impossibile to add
     new attributes to them and their instances."""
    __setattr__ = frozen(object.__setattr__)

    class __metaclass__(type):
        __setattr__ = frozen(type.__setattr__)


class DictAsProperty2(dict):
    validFields = {
    }

    def __init__(self, data=None):
        if data:
            dict.__setattr__(self, 'validFields', data.copy())
            dict.__init__(self, data)
        else:
            dict.__init__(self, self.validFields)

    def __getitem__(self, name):
        if name in self.validFields:
            return dict.__getitem__(self, name)
        raise AttributeError(name)

    def __getattr__(self, name):
        if name in self.validFields:
            return dict.__getitem__(self, name)
        raise AttributeError(name)

    def __setitem__(self, name, value):
        if name in self.validFields:
            dict.__setitem__(self, name, value)
            return self
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.validFields:
            dict.__setitem__(self, name, value)
            return self
        raise AttributeError(name)


class DictAsProperty(object):
    validFields = {
    }

    def __init__(self, data=None):
        self.datadict = {}
        if data:
            self.setDict(data)

    def __str__(self):
        return pprint.pformat(self.datadict)

    def __getattr__(self, name):
        if name in self.validFields:
            return self.datadict.setdefault(name, self.validFields[name])
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.validFields:
            self.datadict[name] = value
            return self
        return object.__setattr__(self, name, value)

    def getDict(self):
        return self.datadict

    def setDict(self, datadict):
        self.datadict = datadict
        return self


class Storage(dict):

    """from gluon storage.py """
    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get
    __getattr__ = dict.get
    __repr__ = lambda self: '<Storage %s>' % dict.__repr__(self)
    # http://stackoverflow.com/questions/5247250/why-does-pickle-getstate-accept-as-a-return-value-the-very-instance-it-requi
    __getstate__ = lambda self: None
    __copy__ = lambda self: Storage(self)

    def getlist(self, key):
        value = self.get(key, [])
        if value is None or isinstance(value, (list, tuple)):
            return value
        else:
            return [value]

    def getfirst(self, key, default=None):
        values = self.getlist(key)
        return values[0] if values else default

    def getlast(self, key, default=None):
        values = self.getlist(key)
        return values[-1] if values else default


class FastStorage(dict):

    """from gluon storage.py """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        return getattr(self, key) if key in self else None

    def __getitem__(self, key):
        return dict.get(self, key, None)

    def copy(self):
        self.__dict__ = {}
        s = FastStorage(self)
        self.__dict__ = self
        return s

    def __repr__(self):
        return '<Storage %s>' % dict.__repr__(self)

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, sdict):
        dict.__init__(self, sdict)
        self.__dict__ = self

    def update(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

if sys.version_info >= (2, 7, 4):
    # check if Issue1469629 solved version
    Storage = FastStorage


class Statistics(object):

    def __init__(self, timeFn=None):
        self.datadict = {
            'min': 0,
            'max': 0,
            'avg': 0,
            'sum': 0,
            'last': 0,
            'count': 0,
        }
        self.formatstr = '%(last)s(%(min)s~%(max)s), %(avg)s=%(sum)s/%(count)d'

        self.timeFn = timeFn  # FPS mode
        if self.timeFn:
            self.frames = []

    def update(self, data):
        data = float(data)
        self.datadict['count'] += 1
        self.datadict['sum'] += data

        if self.datadict['last'] is not None:
            self.datadict['min'] = min(self.datadict['min'], data)
            self.datadict['max'] = max(self.datadict['max'], data)
            self.datadict['avg'] = self.datadict[
                'sum'] / self.datadict['count']
        else:
            self.datadict['min'] = data
            self.datadict['max'] = data
            self.datadict['avg'] = data
            self.formatstr = '%(last).2f(%(min).2f~%(max).2f), %(avg).2f=%(sum).2f/%(count)d'

        self.datadict['last'] = data

        return self

    def updateFPS(self):
        if not self.timeFn:
            raise AttributeError('NOT FPS stat')
        thistime = self.timeFn()
        self.frames.append(thistime)
        while(self.frames[-1] - self.frames[0] > 1):
            del self.frames[0]

        if len(self.frames) > 1:
            fps = len(self.frames) / (self.frames[-1] - self.frames[0])
        else:
            fps = 0
        self.update(fps)
        return self.frames

    def getStat(self):
        return self.datadict

    def __str__(self):
        return self.formatstr % self.datadict


class BaseNN():

    def __init__(self, base=36, numerals="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        if len(numerals) != base:
            raise Exception("base not match numerals ")
            return

        self.base = base
        self.numerals = numerals

        rightstr = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:base]
        self.tostr = string.maketrans(rightstr, numerals)
        self.fromstr = string.maketrans(numerals, rightstr)

    def encode(self, remains):
        b = self.base
        numerals = self.numerals
        rtns = []
        while remains >= b:
            rtns.append(numerals[remains % b])
            remains = remains // b
        rtns.append(numerals[remains])
        rtns.reverse()
        return "".join(rtns)

    def decode(self, strs):
        return int(strs.translate(self.fromstr), self.base)


# generic util
FILTER = ''.join([(len(repr(chr(
    x))) == 3) and chr(x) or '.' for x in range(256)])


def hexdump(src, length=32):
    N = 0
    result = ''
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02X" % ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
        N += length
    return result


def timeit(count, fn, args):
    st = time.time()
    for i in xrange(count):
        fn(*args)
    ed = time.time()
    return ed - st, count / (ed - st)


class TimeRun():

    def __init__(self, checkdur=1.0, monfn=None):
        self.reset(checkdur, monfn)

    def reset(self, checkdur=1.0, monfn=None):
        self.starttime = time.time()
        self.oldtime = self.starttime
        self.checkcount = 0
        self.overcount = 0
        self.checkdur = checkdur
        if monfn:
            self.monfn = monfn
        else:
            self.monfn = self.prints

    def prints(self, args):
        print(args)

    def is_overdur(self):
        self.checkcount += 1
        if time.time() - self.oldtime >= self.checkdur:
            self.oldtime = time.time()
            self.overcount += 1
            return True
        return False

    def get_dur(self):
        return time.time() - self.starttime

    def timeit(self, count, fn, args):
        for i in range(count):
            fn(*args)
        return self.get_dur(), count / self.get_dur()

    def timeit_mon(self, count, fn, args):
        for i in range(count):
            rtn = fn(*args)
            if self.is_overdur():
                self.monfn((i, rtn, self.get_dur()))
        return self.get_dur(), count / self.get_dur()


class ID32(object):
    F1616 = struct.Struct("HH")
    F8816 = struct.Struct("BBH")
    F32 = struct.Struct("I")

    def __init__(self, i32=0):
        self.f32(i32)

    def __str__(self):
        return "[ID:0x%08X]" % self.t32()

    def fromStr(self, idstr):
        self.f32(int(idstr[4:-1], 16))
        return self

    def __int__(self):
        return self.t32()[0]

    def f8816(self, *args):
        self.id32 = ID32.F8816.pack(*args)
        return self

    def t8816(self):
        return ID32.F8816.unpack(self.id32)

    def f1616(self, *args):
        self.id32 = ID32.F1616.pack(*args)
        return self

    def t1616(self):
        return ID32.F1616.unpack(self.id32)

    def f32(self, *args):
        self.id32 = ID32.F32.pack(*args)
        return self

    def t32(self):
        return ID32.F32.unpack(self.id32)

# _g_Serial = itertools.count()
# def getSerial():
#     return next(_g_Serial)
getSerial = itertools.count().next

# logging


def getLogger(level=logging.DEBUG, appname='noname'):
    # create logger
    logger = logging.getLogger(appname)
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter("%(asctime)s:%(levelno)s: %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


# import Crypto.Cipher.AES
# sessionCodec = Crypto.Cipher.AES.new("1234567890123456")


# def sessionMake(idint, timet=None, int3=None, int4=None):
#     """세션 키 생성기
#     4개의 32bit int를 받아서 128bit hex string을 돌려 주는 함수
#     1개만 주는 경우 나머지는 자동으로 채운다.
#     """
#     timet = int(time.time()) if timet == None else timet
#     int3 = random.getrandbits(32) if int3 == None else int3
#     int4 = random.getrandbits(32) if int4 == None else int4

#     data = struct.pack("<I", idint) + struct.pack(
#         "<I", timet) + struct.pack("<I", int3) + struct.pack("<I", int4)
#     endata = sessionCodec.encrypt(data)
#     enlist = struct.unpack("<IIII", endata)
#     return "%08x%08x%08x%08x" % enlist


# def sessionParse(sessionKey):
#     """세션 키를 분석해서 원래 값을 만드는함수
#     4개의 int 를 돌려준다.
#     makeSessionKey 의 인자 순으로 돌려준다.
#     """
#     if not sessionKey:
#         return None
#     ints = [struct.pack("<I", int(sessionKey[a:a + 8], 16))
#             for a in range(0, 32, 8)]
#     data = "".join(ints)
#     dedata = sessionCodec.decrypt(data)
#     delist = struct.unpack("<IIII", dedata)
#     return delist


def getRnd2():
    return int(random.random() * 0xffffffff)
m_z, m_w = getRnd2(), getRnd2()
# getRnd is 10 times faster then getRnd2


def getRnd():
    global m_z, m_w
    m_z = 36969 * (m_z & 65535) + (m_z >> 16)
    m_w = 18000 * (m_w & 65535) + (m_w >> 16)
    return (m_z << 16) + (m_w & 65535)


def getRandomString(l=16):
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(l))


def osRandom(l=16):
    return long(binascii.hexlify(os.urandom(l)), 16)


def random2pi(m=2):
    return math.pi * m * (random.random() - 0.5)


def getHMSAngle(mst, hands):
    """ clock hands angle
    0 : hour
    1 : minute
    2 : second
    mst = time.time()"""

    lt = time.localtime(mst)
    ms = mst - int(mst)
    if hands == 0:  # hour
        return math.radians(lt[3] * 30.0 + lt[4] / 2.0 + lt[5] / 120.0 + 90)
    elif hands == 1:  # minute
        return math.radians(lt[4] * 6.0 + lt[5] / 10.0 + ms / 10 + 90)
    elif hands == 2:  # second
        return math.radians(lt[5] * 6.0 + ms * 6 + 90)
    else:
        return None

# from wxclock


class memoized(object):

    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

import subprocess
findipre = re.compile(r'inet addr\:(?P<ipaddr>\d+\.\d+\.\d+\.\d+)')


def getMyIPAddress():
    rtn = findipre.findall(subprocess.check_output(["ifconfig"]))
    return [a for a in rtn if a != '127.0.0.1']


def myHostname():
    return socket.gethostname()


def getUsername():
    return pwd.getpwuid(os.getuid())[0]


def CPUTemp():
    if not sys.platform.startswith('linux'):
        return 0
    cpu_temp = "/sys/class/thermal/thermal_zone0/temp"
    for line in open(cpu_temp):
        return float(line) / 1000


def CPUClock():
    if not sys.platform.startswith('linux'):
        return 0
    cpu_freq = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    for line in open(cpu_freq):
        return float(line)

re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')


def meminfo():
    """-> dict of data from meminfo (str:int).
    Values are in kilobytes.
    """
    if not sys.platform.startswith('linux'):
        return {}
    result = dict()
    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if not match:
            continue  # skip lines that don't parse
        key, value = match.groups(['key', 'value'])
        result[key] = int(value)
    return result


def cpuusage():
    """-> dict of cpuid : (usertime, nicetime, systemtime, idletime)
    cpuid "cpu" means the total for all CPUs.
    cpuid "cpuN" means the value for CPU N.
    """
    if not sys.platform.startswith('linux'):
        return {'cpu': [0, 0, 0, 0]}
    wanted_records = [line for line in open(
        '/proc/stat') if line.startswith('cpu')]
    result = {}
    for cpuline in wanted_records:
        fields = cpuline.split()[:5]
        data = map(int, fields[1:])
        result[fields[0]] = list(data)
    return result


def loadavg():
    """-> 5-tuple containing the following numbers in order:
    - 1-minute load average (float)
    - 5-minute load average (float)
    - 15-minute load average (float)
    - Number of threads/processes currently executing (<= number of
    CPUs) (int)
    - Number of threads/processes that exist on the system (int)
    - The PID of the most recently-created process on the system (int)
    """
    if not sys.platform.startswith('linux'):
        return [0, 0, 0, 0, 0, 0]
    loadavgstr = open('/proc/loadavg', 'r').readline().strip()
    data = loadavgstr.split()
    avg1, avg5, avg15 = map(float, data[:3])
    threads_and_procs_running, threads_and_procs_total = map(int,
                                                             data[3].split('/'))
    most_recent_pid = int(data[4])
    return avg1, avg5, avg15, threads_and_procs_running, threads_and_procs_total, most_recent_pid

oldpct = cpuusage()['cpu']


def getCpuPer():
    global oldpct
    nowpct = cpuusage()['cpu']
    dt = []
    for i in range(len(nowpct)):
        dt.append(nowpct[i] - oldpct[i])
    oldpct = nowpct
    try:
        cpupct = 100 - (dt[-1] * 100.00 / sum(dt))
    except:
        cpupct = 0
    return cpupct


class worldTime():
    clocks = [
        # name , diff gmt , dst
        ["UTC",        0, 0],
        ["Seattle",   -8, 1],
        ["Berlin",     1, 1],
    ]
    datetimeformatstring = "%H:%M %a %Y-%m-%d"

    @staticmethod
    def getCount():
        return len(worldTime.clocks)

    @staticmethod
    def gettime(h, dst):
        td = datetime.timedelta(hours=h + dst)
        return datetime.datetime.utcnow() + td

    @staticmethod
    def getStr(i):
        return "%8s%s:%s" % (
            worldTime.clocks[i][0],
            '*' if worldTime.clocks[i][2] else ' ',
            worldTime.gettime(
                worldTime.clocks[i][1],
                worldTime.clocks[i][2]
            ).strftime(worldTime.datetimeformatstring)
        )


def testme():
    a = ID32(0xf0000054)
    b = ID32()
    print(a, int(a), str(a), b.fromStr(str(a)))
    pass

    for i in range(10):
        print(getSerial())
    a = Statistics()
    a.update(10.0)
    print(a)
    a.update(11)
    print(a)

    a = DictAsProperty2()
    # a[5] = 6
    print('cpu', cpuusage())

    b26 = BaseNN(26, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    # b26 = BaseNN( 36)
    for a in range(1024):
        ss = b26.encode(a)
        print(a, ss, b26.decode(ss))

    print(getMyIPAddress())


def test3():
    class myDict(DictAsProperty2):
        validFields = {
            'a': 0,
            'b': 1
        }

    a = myDict()
    a.b = 4
    a['c'] = 5
    print a.b


if __name__ == "__main__":
    print CPUClock()
    print CPUTemp()
    # test3()
    # for i in range(10) :
    #    print( getSerial() )
