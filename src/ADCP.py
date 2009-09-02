
__author__="John"
__date__ ="$Jun 11, 2009 8:13:11 AM$"

from utils import *
from kml_utils import *
from heapq import heapify, heappush, heappop
import os
from Classes import EnsembleCollection, Stack, Ensemble, Bin

def importTraverseFile(file):
    "Take a single traverse file and build a list filled with ensembles of bins"

    # Safely open and read the file
    with open(file, 'r') as f: lines = [i[:-1] for i in f.readlines()]
    # Functional programming FTW! Take the file path, pull off the file name
    # throw away the extension, then throw away the "t" that comes at the end
    # of all ADCP files, then just take the last 3 values. Result, the traverse number.
    value = int(path.split(file)[1].split('.')[0][:-1][3:])
    # Now we have our transect name, initialize our parent Stack instance with it
    # This is mostly just a temporary list
    traverse = Stack(value)
    # First two lines are comments
    traverse.comment = lines.pop(0) + "\n" + lines.pop(0)

    # Grab third line in the file (Line "C" in RDI ASCII docs)
    # Line C describes this traverse, store info as attributes in Stack instance
    attrs = "depth_cell_length", "blank_after_transmit", "depth_from_config", \
        "number_depth_cells", "pings_per_ensemble", "time_per_ensemble", \
        "profiling_mode"

    vals = split_line(lines.pop(0))
    for i in range(len(attrs)):
        setattr(traverse, attrs[i], vals[i])

    num = 1
    while len(lines):
        # Build the ensemble
        En = Ensemble(num)
        num += 1
        ensemble_attrs = {1: ("year", "month", "day", "hour","minute","second","hundredths",
                              "number", "num_ensembles","pitch","roll","corrected_heading","temp"),
                          2: ("velocity_east","velocity_west","velocity_up","velocity_error",\
                              "bottom_depth", "altitude","delta_altitude","HDOP",
                              "depth1","depth2","depth3","depth4"),
                          3: ("elapsed_distance","elapsed_time","distance_north","distance_east",\
                              "distance_good"),
                          4: ("latitude","longitude","invalid","unused"),
                          5: ("discharg_mid","discharge_top","discharge_bot", \
                              "start_discharge","start_dist","end_discharge","end_dist",\
                              "start_depth","end_depth"),
                          6: ("num_bins","unit","velocity_ref","intensity_units",\
                              "intensity_scale","sound_absorbtion")
                        }
        for attr_tup in ensemble_attrs.values():
            vals = split_line(lines.pop(0))
            for i in range(len(attr_tup)):
#                if attr_tup[i][:-1] == "depth": 
#                    if vals[i] == 0: print (num, value, vals[i])
                setattr(En, attr_tup[i], vals[i])
#        if num == 2: print(os.path.split(file)[-1], ",start,", En.latitude, ",", En.longitude)
        for i in range(En.num_bins):
            En.push(Bin(*split_line(lines.pop(0))))
        En.calcAverages()
        traverse.push(En)
    return value, traverse

def parse_transect(transect, start=0):
    location = transect[start]
    collection_list = () 
    whole_list = list(transect)
    while whole_list:
        collection = EnsembleCollection(location)
        this_list, next_ensemble = find_nearest(whole_list, location)
        for en in this_list: collection.push(en)
        whole_list = list(filter(lambda x: x not in this_list, whole_list))
        collection_list += collection,
        if not next_ensemble: break
        location = next_ensemble
    return collection_list


if __name__ == "__main__":
    # Change directory if on *nix/Mac boxes
    if os.name == 'posix': os.chdir('/Users/John/Dropbox/Carroll/adcp/src')

    # Initialize a list of transects
    traverse_list = []

    # Grab each trasect file and push them onto the list
    for i in range(26):
#    for i in range(20):
        file = 'C:\\Documents and Settings\\John\\Desktop\\june_data\\LWG%03it.000' % i
#        file = 'C:\\Documents and Settings\\John\\Desktop\\august_data\\LWG%03it.000' % i
        value, traverse = importTraverseFile(file)
        # We use the Heap module to build the transect, so we keep it ordered.
        heappush(traverse_list, (value, traverse))

    # Each transect is a group of traverses, these are start and stop slices for each 
    # transect.
    trans_slices = [(0,4),(4,7),(7,12),(12,15),\
                    (15,19),(19,21),(21,25),(25)]
#    trans_slices = [(0,4),(4,8),(8,12),(12,16),\
#                    (16,20),(20,23)]
    # Build a dictionary of transects so we can access them by number
    Trans = dict([(i,()) for i in range(1,9)])
#    Trans = dict([(i,()) for i in range(1,7)])
    # And add Ensemble Collections to the new dictionary for later consumption
    n = 1
    for start, stop in trans_slices[:-1]:
        for i in range(start, stop): #This is a single list of ensembles
            trans = heappop(traverse_list)[1]
            for en in trans:
                Trans[n] += en,
        n += 1

    # make a KML file of everything we have:
#    kml = KML("all_transects")
#    for i in range(1,6):
#        trans = Trans[i]
#        for en in trans:
#            name = int(en.azimuth)
#            point = en.point
#            velocity, azimuth = en.velocity, en.azimuth
#            depth = en.depth
#            style = int(velocity)
#            if style == 0: style = "O"
#            elif ((name < 0) or (style < 0)): 
#                style = "red-diamond"
#                name = ""
#            kml.addPlacemark(Placemark(name, point, velocity, azimuth, depth, style))
#    kml.output()
        
#    collections = {1: None, 2: None, 3: None, 4: None, 5:None}
    collections = {1:None, 3:None, 5: None, 7: None}
    for i in collections.keys(): 
        collections[i] = parse_transect(Trans[i], -1)
    # This is where we strip out any parts of the final transect that we don't want
#    collections[3] = collections[3][:14]
    collections[1] = collections[1][:12]    

    outputData("Column Averaged", collections)
    for dep in [6,12,18,24]:
        depth = int(dep * 3.2808399)
        outputData("%i Feet Depth" % dep, collections, atDepth=dep)

    print("Done")