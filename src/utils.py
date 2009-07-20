from kml import Placemark, KML, description_from_list, description_from_text
from math import sqrt, isnan
from os import path
      
def outputData(name, collection, atDepth=None):
    kml = KML(name)
    file = open("../data/%s.csv" % name.replace(" ","_"), "w")
    file.write("latitude, longitude, v_mean, v_dev, v_n, v_err, v_min, v_max, a_mean, a_dev, a_n, a_err, a_min, a_max, d_mean, d_dev, d_n, d_err, d_min, d_max\n")
    for lst in collection.values():
        for col in lst:
            name = int(col.azimuth)
            point = col.point
            if atDepth: velocity, azimuth = col.averageAtDepth(atDepth)
            else: velocity, azimuth = col.velocity, col.azimuth
            depth = col.depth
            style = int(velocity)
            if style == 0: style = "O"
            elif ((name < 0) or (style < 0)): 
                style = "red-diamond"
                name = ""
            kml.addPlacemark(Placemark(name, point, velocity, azimuth, depth, style))
            file.write("%f, %f," % point)
            for val in [velocity, azimuth, depth]:
                for v in val():
                    file.write(" %0.3f," % v)
            file.write("\n")
    kml.output()
    file.close()

def filter_list(lst, bad_value=-32768):
    "Return new list with bad_value filtered out"
    return list(filter(lambda x: x != bad_value, lst))
    
def meanstdv(lst, bad_value=-32768):
    "Calculate mean and standard deviation of data in lst:"
    lst = filter_list(lst, bad_value)
    if not len(lst):
        return tuple([bad_value for i in range(6)])
    n, mean, std = len(lst), 0, 0
    for a in lst:
        mean += a
    mean = mean / float(n)
    for a in lst:
        std += (a - mean)**2
    std = sqrt(std / float(n-1))
    err = std/sqrt(n)
    return mean, std, n, err, min(lst), max(lst)
  
def split_line(line):
    # Convert to float or int, as appropriate
    makenum = lambda x: float(x) if x.find('.') != -1 else int(x)
    # Test for string, call makenum if not string
    isstring = lambda x: x if x.isalpha() else makenum(x)
    return [i for i in map(isstring,line.split())]


def make_point_bucket(trans_list):
    bucket = {}
    for T in trans_list:
        for ensemble in T:
            point = ensemble.latitude, ensemble.longitude
            if point in bucket: bucket[point] += ensemble,
            else: bucket[point] = ensemble,
    return bucket

def find_nearest(list, location):
    ensemble = location
    bucket = ()
    next_ensemble = None
    for en in list:
        if en.isNear(ensemble): bucket += en,
        else: 
            if en.isAtDistance(ensemble) and not next_ensemble:
                next_ensemble = en
    return bucket, next_ensemble

def make_bucket(trans_list):
    bucket = []
    for T in trans_list:
        for ensemble in T:
            bucket.append(ensemble)
    return bucket

def error_check(collection):
    velocity, v_sd, v_n, v_err = collection.velocity()
    azimuth, a_sd, a_n, a_err = collection.azimuth()
    if (a_sd > 25.0):
        return "azimuth"
    elif (v_sd > 2):
        return "velocity"
    else: return False