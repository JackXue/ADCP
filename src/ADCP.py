
__author__="John"
__date__ ="$Jun 11, 2009 8:13:11 AM$"

from utils import *
from kml_utils import *
from heapq import heapify, heappush, heappop
import os
from Classes import EnsembleCollection, Stack, Ensemble, Bin

def importTransectFile(file):
    "Take a transect file and build a transect list filled with ensembles of bins"

    lines = [i[:-1] for i in open(file,'r').readlines()]
    # Functional programming FTW! Take the file path, pull off the file name
    # throw away the extension, then throw away the "t" that comes at the end
    # of all ADCP files, then just take the last 3 values. Result, the transect number.
    value = int(path.split(file)[1].split('.')[0][:-1][3:])
    # Now we have our transect name, initialize our parent Stack instance with it
    transect = Stack(value)
    # First two lines are comments
    transect.comment = lines.pop(0) + "\n" + lines.pop(0)

    # Grab third line in the file (Line "C" in RDI ASCII docs)
    # Line C describes this transect, store info as attributes in Transect
    attrs = "depth_cell_length", "blank_after_transmit", "depth_from_config", \
        "number_depth_cells", "pings_per_ensemble", "time_per_ensemble", \
        "profiling_mode"

    vals = split_line(lines.pop(0))
    for i in range(len(attrs)):
        setattr(transect, attrs[i], vals[i])

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

        for i in range(En.num_bins):
            En.push(Bin(*split_line(lines.pop(0))))
        En.calcAverages()
        transect.push(En)
    return value, transect

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
    transect_list = []

    # Grab each trasect file and push them onto the list
    for i in range(26):
        file = '../data/LWG%03it.000' % i
        value, transect = importTransectFile(file)
        heappush(transect_list, (value, transect))

    # Start and stop slices for each transect. True is a transect, False is a
    # group of readings taken while holding stationary. 
    # (i.e. not used in transect calculations, we ignore the later in this program).
    trans_slices = [(True,0,4),(False,4,7),(True,7,12),(False,12,15),\
                    (True,15,19),(False,19,21),(True,21,25),(False,25)]
    # Build a dictionary of transects 1-9 so we can access them by number
    Trans = dict([(i,()) for i in range(1,9)])
    # And add Ensemble Collections to the new dictionary for later consumption
    n = 1
    for is_t, start, stop in trans_slices[:-1]:
        for i in range(start, stop): #This is a single list of ensembles
            trans = heappop(transect_list)[1]
            for en in trans:
                Trans[n] += en,
        n += 1

    # make a KML file of everything we have:
#    kml = KML()
#    for i in range(1,9):
#        trans = Trans[i]
#        for en in trans:
#            kml.addPlacemark(make_Placemark(en))
#    kml.output("../data/all_transects.kml")
        
    collections = {1: None, 3: None, 5: None, 7: None}
    for i in collections.keys(): # beginning of transect 5 was messed up, so start at the end
        collections[i] = parse_transect(Trans[i], -1)
    collections[1] = collections[1][:12]

    outputData("Column Averaged", collections)
    for dep in [6,12,18,24]:
#        depth = int(dep * 3.2808399)
        outputData("%i Feet Depth" % dep, collections, atDepth=dep)

    print("Done")