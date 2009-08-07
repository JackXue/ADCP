__author__="John"
__date__ ="$Jun 11, 2009 8:13:54 AM$"

from bisect import bisect
from heapq import heapify, heappush, heappop
import gislib
from utils import split_line, meanstdv
from math import isnan

class Mean(float):
    "Class to smartly hold magnitude and direction averages and standard deviations"
    def __new__(cls, lst=[]):
        #Unfortunately, we have to run through this twice because we
        # can't store a value in the instance from the __new__() method,
        # only in the class
        if len(lst): value = meanstdv(lst)[0]
        else: value = -9e9 # Allow initialization to a null value.
        return float.__new__(cls, value)
    def __init__(self, lst=[]):
        self.list = lst #Store the list, so we can later do interesting data work
        if len(lst):
            value, self.std, self.n, self.err, self.min, self.max = meanstdv(lst)
        else:
            self.std = float(-9e9)
            self.n = 9e9
            self.err = 9e9
            self.min = 9.e9
            self.max = 9e9
    def __repr__(self):
        return "Mean(%0.3f) at <%i>" % (self, id(self))
    def __call__(self, show_list=False):
        tup = float(self), self.std, self.n, self.err, self.min, self.max
        if show_list: tup += self.list,
        return tup
    def __str__(self):
        return "Mean=%0.3f, Standard deviation=%0.3f, n=%i, Standard Error=%0.3f" %( self, self.std, self.n, self.err)
    def __add__(self, other):
        "Add values together, smartly carrying our mean representation"
        if isinstance(other, Mean):
            #We've initialized null as a placeholder, return the other value in whole
            if self == -9e9: return Mean(other.list)
            lst = self.list + other.list
            return Mean(lst)
        else:
            return super(Mean, self).__add__(other)
    def __iadd__(self, other):
        return self.__add__(other)

class Bin(float):
    def __new__(cls, *args):
        return float.__new__(cls, args[0])
#    def __init__(self, depth, magnitude, azimuth, east, north, up,
#                 error, backscatter0,backscatter1,backscatter2,backscatter3,
#                 percent_good, discharge):
    def __init__(self, *args):
        self.velocity, self.azimuth, self.east, self.north, self.up, self.error, \
            back0, back1, back2, back3, \
            self.percent_good, self.discharge = args[1:]
        self.backscatter = back0, back1, back2, back3
        
    def __repr__(self):
        print("Bin (%0.2f)" %self)

class Stack(list):
    def __init__(self, value):
        list.__init__(self)
        self.value = value
    def append(self, item):
        "We should raise an exception if we try to append, rather than heappush"
        raise Exception("Nope, use push()")
    def push(self, item):
#        if not self.check_item(self, item): raise Exception("Not implemented in subclass")
        heappush(self, item)
    def get(self, value):
        if value in self: return self[self.index(value)]
        else: return self.__get_nearest_index(value)
    def __get_nearest_index(self, index):
        """Get the bin that is closest to any given depth. The boundaries of the
        bins are in between the depths documented in the WinRiver output file,
        therefore, chosing the closest bin depth based on any arbitrary depth
        should be good enough.
        """
        # Kilometer's downstream and upstream
        lower = bisect(self,index)-1 #if bisect(sites,depth)-1 > 0 else 0 # zero is the lowest (protect against value of -1)
        # bisect returns the length of a list when the bisecting number is greater than the greatest value.
        # Here we protect by max-ing out at the length of the list.
        upper = min([bisect(self,index),len(self)-1])
        # Use the indexes to get the kilometers from the sites list
        down = self[lower]
        up = self[upper]
        if index-down < up-index: # Only if the distance to the downstream node is closer do we use that
            return down
        else:
            return up

class Ensemble(Stack):
    def __init__(self, value):
        Stack.__init__(self, value)
        self.id = id(self)
        self.velocity = None # Column averaged velocity
        self.azimuth = None # Column averaged azimuth
        self.year = None #  
        self.month = None #  
        self.day = None #  
        self.hour = None # 
        self.minute = None # 
        self.second = None # 
        self.hundredths = None # 
        self.number = None #  
        self.num_ensembles = None # 
        self.pitch = None # 
        self.roll = None # 
        self.corrected_heading = None # 
        self.temp = None # 
        self.velocity_east = None # 
        self.velocity_west = None # 
        self.velocity_up = None # 
        self.velocity_error = None # 
        self.bottom_depth = None #  
        self.altitude = None # 
        self.delta_altitude = None # 
        self.HDOP = None # 
        self.depth1 = None # 
        self.depth2 = None # 
        self.depth3 = None # 
        self.depth4 = None # 
        self.elapsed_distance = None # 
        self.elapsed_time = None # 
        self.distance_north = None # 
        self.distance_east = None # 
        self.distance_good = None # 
        self.latitude = None # 
        self.longitude = None # 
        self.invalid = None # 
        self.unused = None # 
        self.discharg_mid = None # 
        self.discharge_top = None # 
        self.discharge_bot = None # 
        self.start_discharge = None # 
        self.start_dist = None # 
        self.end_discharge = None # 
        self.end_dist = None # 
        self.start_depth = None # 
        self.end_depth = None # 
        self.num_bins = None # 
        self.unit = None # 
        self.velocity_ref = None # 
        self.intensity_units = None # 
        self.intensity_scale = None # 
        self.sound_absorbtion = None # 

    def __eq__(self, other):
        return self is other
    def __hash__(self):
        return self.id
    def __repr__(self): return "Ensemble <%i>" % self.id
    def check_item(self, bin): return isinstance(bin,Bin)
    def get_point(self): return self.latitude, self.longitude
    point = property(get_point)
    def getDistance(self, other):
        return gislib.getDistanceFt(self.point, other.point)
    def isNear(self, other, radius=50):
        return gislib.km2ft(gislib.isWithinDistance(self.point, other.point, gislib.ft2km(radius)))
    def isAtDistance(self, other, distance=90, radius=10):
        dist = self.getDistance(other)
        return abs(dist - distance) < radius
    def calcAverages(self):
        vel = []
        azm = []
        for bin in self:
            vel.append(bin.velocity)
            azm.append(bin.azimuth)
        self.velocity = Mean(vel)
        self.azimuth = Mean(azm)
        lst = []
        for d in [self.depth1, self.depth2, self.depth3, self.depth4]:
            if d > 0: lst.append(d)
        try:
            self.depth = Mean(lst)
        except ZeroDivisionError:
            pass
            self.depth = Mean()
    def averageAtDepth(self, depth):
        vel = []
        azm = []
        for i in self:
            vel.append(self.get(depth).velocity)
            azm.append(self.get(depth).azimuth)
        return Mean(vel), Mean(azm)

class EnsembleCollection(Stack):
    def __init__(self, ensemble, radius=30):
        value = ensemble.point
        self.radius = radius
        Stack.__init__(self, value)
        self.push(ensemble)
    def __repr__(self): return "EnsembleCollection at (%0.3f, %0.3f)" % self.value
    def calcVelocityAverage(self):
        vel = Mean()
        for en in self:
            vel += en.velocity
        return vel
    def calcAzimuthAverage(self):
        azm = Mean()
        for en in self:
            azm += en.azimuth
        return azm
    def calcDepthAverage(self):
        dep = Mean()
        for en in self:
            dep += en.depth
        return dep
    velocity = property(calcVelocityAverage)
    azimuth = property(calcAzimuthAverage)
    depth = property(calcDepthAverage)
    def getCoordinates(self):
        return self.value
    point = property(getCoordinates)
    def averageAtDepth(self, depth):
        vel = Mean()
        azm = Mean()
        for en in self:
            v, a = en.averageAtDepth(depth)
            vel += v
            azm += a
        return vel, azm
    def push(self, item):
        if not isinstance(item, Ensemble): raise Exception("Cannot add type: %s" % type(item))
        heappush(self, item)
        