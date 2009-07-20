from kml import KML, description_from_text, Placemark
    
def make_KML_from_ensemble_list(ensemble_list, designator=None):
    kml = KML()
    for en in ensemble_list:
        kml.addPlacemark(make_Placemark(ensemble))
    des = str(designator) if designator else ""
    kml.output("../data/transects%s.kml" % des)

def make_KML_at_depths(averages_dict, depths=(3,6,9)):
    kmls = {}
    for depth in depths:
        kmls[depth] = KML()
        for point, aves in averages_dict.items():
            vel = aves[depth]["vel"]
            azimuth = aves[depth]["azm"]
            desc = description_from_text("Velocity: %0.3f<br/>Azimuth: %0.3f" % (velocity, azimuth))
            pt = Placemark(int(azimuth), point.point, desc)
            kmls[depth].addPlacemark(pt)
    for key in kmls.keys():
        kmls[key].output("../data/depth%i.kml" % key)

def make_KML_average_columns(averages_dict):
    kml = KML()
    aves = {}
    for point, bucket in averages_dict.items():
        aves[point] = {"vel": [], "azm": []}
        vel = Mean() + point.velocity
        azm = Mean() + point.azimuth
        for en in ens:
            vel += en.velocity
            azm += en.azimuth
        aves[point]["vel"] = vel
        aves[point]["azm"] = azm
    
    f = open("../data/column_averages.xml",'w')
    f.write("latitude, longitude, velocity_mean, v_std, v_n, azimuth_mean, a_std, a_n\n")
    mkstr = lambda x: ("%s" % x).replace(", ","<br/>").replace("=",": ")
    for point, ave in aves.items():
        vel = ave["vel"]
        azm = ave["azm"]
        text = "<h2>Velocity:</h2><p>%s</p>" % mkstr(vel)
        text += "<h2>Azimuth:</h2><p>%s</p>" % mkstr(azm)
        desc = description_from_text(text)
        pt = Placemark(int(azm), point.point, desc)
        kml.addPlacemark(pt)
        line = list(point.point)
        line.append(vel())
        line.append(azm())
        f.write(",".join(line) + "\n")
    f.close()

    kml.output("../data/column_averages.kml")
    

def make_KML(transects):
    f = open("../data/transects.kml" % number,'w')
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>""")
    for i in [1,3,5,7]:
#        for trans in transects[i]
        location, bucket = location_list[i], bucket_list[i]
#        if location.value in excludes[number]: ex += location.id,
        if excludes:
            if location.id in excludes: continue
        f.write("""
    <Placemark><name>%i</name>
        <Point>
            <coordinates>%f, %f</coordinates>
        </Point>
        <description>
            <![CDATA[<h1>Ensembles</h1><ul>""" % (location.id, location.point[1], location.point[0]))
        for en in bucket:
            f.write("""
                    <li>%s</li>""" % en)
        f.write("""
                </ul>]]>
            </description>\n</Placemark>""")
    f.write("</Document>\n</kml>")
    f.flush()
    f.close()
#    print(number, ": ", ex)
