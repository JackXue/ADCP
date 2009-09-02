from GChartWrapper import *
from math import pi, radians, degrees, sin, cos, atan2
 
class Rose(object):
    def __init__(self, lst, bad_value=-32768, color='red', size=200):
        self.color = color
        lst = [i for i in filter(lambda x: x != bad_value, lst)]
        coding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        bins = {0:0} # Initialize with a zero value at due north
        self.size = size
        ####################################################
        # Separate values into bins of 10 degree increments. The values
        # Are the number of azimuth readings within each 10 degree increment
        # where 10 degrees includes all readings in the range (5,15], 20
        # degrees includes all readings in the range (15,25], and 0 degrees
        # includes all readings in the range (355,5].
        a = 0
        for b in range(5,360,10):
            rng = lambda x: (x >= a) and (x < b)
            bins[b+5] = len([i for i in filter(rng, lst)])
            a = b
        ############################################
        # Move values at 360 to zero and copy the full set of values
        # to 360. This is so that we can have a full circle of data
        # rather than having the data end at 355.
        try:
            bins[0] += bins[360]
            bins[360] = bins[0]
        except KeyError:
            pass

        ############################################
        # Grab the highest value so that we can have a max and
        # percentages of the max for the histogram bar heights
        # and set up some convenience variables for use in the
        # loops
        highest = max(bins.values())
        vals = [] # String of values for use in the URL
        # The outer loop looks only at values at increments
        # of ten. This is a variable to help build the inner
        # loop (values 1-9)
        a = 0 
        ############################################
        # Go through all of our values at ten degree increments
        # if the degrees are 5 (25, 255, etc) then we set the
        # value equal to 'A' (i.e. zero). Otherwise, set all the
        # values from 6-9 and 0-4 to whatever percentage we have.
        # This ends up creating a zero point at 5, values at some
        # magnitude centered on a ten degree increment, and then
        # another zero point at 15. The result is something that
        # visually resembles a bar extending from zero
        ###
        # NOTE: We have so many points only because we want a single
        # zero point at each 5, 15, 25... degree interval in order
        # to make the bars. Because of that, and because we want a
        # flat bar top, we have have to have values at 1 degree increments
        # so we fill it up with data. It makes a long URL, but I'll
        # accept that until Google gets a more functional API
        for i in range(5,360,10):
            num = bins[i+5]
            try:
                key = int((bins[i+5]/highest) * (len(coding)-1))
                val = coding[key]
            except ZeroDivisionError:
                val = 'A'
            for j in range(a,i):
                if (j%10 == 5): 
                    vals.append('A')
                else:
                    vals.append(val)
            a = i
        # Copy the first 5 values to the end of the dataset to complete
        # the circle (otherwise, 355-360 is blank)
        vals += vals[:5]
        # There's a slight gap between 359 and 0, so we add whatever
        # value is at 0 to fully close that circle. This north bar is
        # the hackiest bar of all, because the radar diagram WANTS to
        # go to 361 and higher.
        vals += vals[0]
        ######################################################
        # Now we generate labels. We need as many labels as we have
        # datapoints, but most of them we fill with blank strings.
        # Here, we make N,S,E,W labels as well as labels at every
        # ten degrees.
        labels = [0]
        mod = 0
        for i in ['N','E','S','W']:
            labels.append(i)
            for j in range(1,90):
                if not j%10: labels.append(j+mod)
                else: labels.append('')
            mod += 90


        if not len(lst): mean = 0 # We're blank, throw up a placeholder chart
        else:
            #########################################
            # Calculate the average azimuth
            rads = [radians(i) for i in lst] #Convert to radians
            # Convenience functions
            ave = lambda x: sum(x)/len(x)
            rotate = lambda x: x+(2*pi) if x<0 else x # bring back to positive angle values
    
            sa = ave([sin(i) for i in rads])
            ca = ave([cos(i) for i in rads])
            # Take the arctan of this, using atan2 to preserve the quadrant information
            # We divide this (in degrees) by ten because there are only 36 values
            # around our rose diagram
            self.mean = mean = degrees(rotate(atan2(sa,ca)))
            ########################################
        
        ########################################
        # Create the pseudo-rose diagram using Google's Radar
        self.G = Radar([vals],encoding='simple')
        self.G.size(size,size)
        self.G.color(self.color)
        self.G.line(1,2,0)
        self.G.axes('x')
        self.G.axes.label(*labels)
        self.G.axes.range(0, 0.0,360.0)
        self.G.marker('h','aaaaaa',0,1.0,2)
        self.G.marker('h','aaaaaa',0,0.5,2)
        self.G.marker('h','dddddd',0,0.25,1)
        self.G.marker('h','dddddd',0,0.75,1)
        self.G.marker('V','008000',0,mean,5)
        self.G.marker('B','FF000080',0,1.0,5.0)

    @property
    def URL(self):
        return self.G.url
    def tag(self, imgid='chart'):
        return self.G.img(height=200,id=imgid)
