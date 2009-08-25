from math import degrees
from itertools import count

def description_from_list(lst):
    t = "<![CDATA[<h1>%i Ensembles</h1><ul>" % len(lst)
    for item in lst:
        t += "<li>%s</li>" % item
    t += "</ul>]]>"
    return t

def description_from_text(text):
    t = "<![CDATA[<h1>Values:</h1>\n"
    t += text + "]]>"
    return t

class Placemark(object):
    id = count()
    def __init__(self, name, point, velocity, azimuth, depth, style="O", description = None):
        self.name = name
        self.point = point
        self.description = description
        self.style = style
        self.velocity = velocity
        self.azimuth = azimuth
        self.depth = depth
        self.id = next(Placemark.id)
    def output(self):
        #TODO: Really look at abstracting this. Placemark shouldn't need to know about ensemble
        point = self.point
        vel = self.velocity()
        azm = self.azimuth()
        spread = int(degrees(self.azimuth.spread))
        dep = self.depth()
        data = {"velocity": vel[0],"v_dev": vel[1],"v_num": vel[2],"v_err": vel[3], "v_min": vel[4], "v_max": vel[5],
                "azimuth": int(azm[0]),"a_dev": azm[1],"a_num": azm[2],"a_err": azm[3], "a_min": azm[4], "a_max": azm[5], "a_spread": spread,
                "depth": dep[0],"d_dev": dep[1],"d_num": dep[2],"d_err": dep[3], "d_min": dep[4], "d_max": dep[5]}
        title = "Point #%i<br />" % self.id
        title += "\t" + ", ".join([str(i) for i in point])
        self.text = """
        <Placemark>
            <name>%s</name>
            <styleUrl>#paddle_%s</styleUrl>
            <ExtendedData>
                <Data name="point">
                    <value>%s</value>
                </Data>\n""" % (self.name, self.style, title)
        for name, value in data.items():
            if isinstance(value,int):
                val = "<value>%i</value>" % value
            else:
                val = "<value>%0.3f</value>" % value
            self.text += """
                <Data name="%s">%s</Data>\n""" % (name, val)
        
        self.text += """
            </ExtendedData>
            <Point>
                <coordinates>%f, %f</coordinates>
            </Point>
        </Placemark>""" % (point[1], point[0])
        return self.text

class KML(object):
    def __init__(self, name):
        self.text = self.header(name)
        self.name = name
        self.text += self.style()
        self.placemarks = []
        
    def addPlacemark(self, placemark):
        self.placemarks.append(placemark)
        
    def output(self, filepath="../data/"):
        name = self.name.replace(" ","_") + ".kml"
        file = filepath + name
        f = open(file, 'w')
        f.write(self.text)
        f.write(self.style())
        for pl in self.placemarks:
            f.write(pl.output())
        f.write("</Document></kml>")
        f.flush()
        f.close()
        
    def header(self, name):
        return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>%s</name>""" % name
    
    def style(self):
        txt = ""
        for i in ["O",1,2,3,4,5,6,7,8,9,"red-diamond"]:
            txt += """
      <Style id="paddle_%s">
        <BalloonStyle>
          <text>
            <![CDATA[
              <h3>$[point]</h3>
              <h4>Velocity</h4>
              Mean velocity: $[velocity]<br />
              Standard error: $[v_err]<br />
              Standard deviation:  $[v_dev]<br />
              $[v_num] samples in range ($[v_min], $[v_max])
              
              <h4>Azimuth</h4>
              Mean azimuth: $[azimuth]<br />
              Standard error: $[a_err]<br />
              Standard deviation:  $[a_dev]<br />
              $[a_num] samples in range ($[a_min], $[a_max])<br />
              Samples distributed over $[a_spread] degrees

              <h4>Depth</h4>
              Mean depth: $[depth]<br />
              Standard error: $[d_err]<br />
              Standard deviation:  $[d_dev]<br />
              $[d_num] samples in range ($[d_min], $[d_max])
            ]]>
          </text>
        </BalloonStyle>
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/%s.png</href>
        </Icon>
      </IconStyle>
        <LabelStyle>
            <color>ff7faaff</color>
            <scale>0.7</scale>
        </LabelStyle>
      </Style>
""" % (str(i), str(i))
        return txt