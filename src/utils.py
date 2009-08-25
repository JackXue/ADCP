from kml import Placemark, KML, description_from_list, description_from_text
from os import path
from math import radians, degrees
      
def outputData(name, collection, atDepth=None):
    kml = KML(name)
    file = open("../data/%s.csv" % name.replace(" ","_"), "w")
    file.write("number, latitude, longitude, v_mean, v_dev, v_n, v_err, v_min, v_max, a_mean, a_dev, a_n, a_err, a_min, a_max, d_mean, d_dev, d_n, d_err, d_min, d_max\n")
    for lst in collection.values():
        for col in lst:
            point = col.point
            if atDepth: 
                velocity, azimuth = col.averageAtDepth(atDepth)
            else: 
                velocity, azimuth = col.velocity, col.azimuth
                vlst = velocity.list
                alst = azimuth.list
                olst = azimuth.original_list
                pass
            name = int(degrees(azimuth)) # Cast to a Python int b/c MeanAzimuth has a long string representation
            depth = col.depth
            style = int(velocity)
            if style == 0: style = "O"
            elif ((name < 0) or (style < 0)): 
                style = "red-diamond"
                name = ""
            PL = Placemark(name, point, velocity, azimuth, depth, style)
            kml.addPlacemark(PL)
            file.write("%i, %f, %f," % (PL.id, point[0], point[1]))
            for val in [velocity, azimuth, depth]:
                for v in val():
                    file.write(" %0.3f," % v)
            file.write("\n")
    kml.output()
    file.close()
def filter_list(lst, bad_value=-32768):
    "Return new list with bad_value filtered out"
    return list(filter(lambda x: x != bad_value, lst))

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