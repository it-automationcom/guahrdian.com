#!/usr/bin/python3

import osm
import dgm
import geopy.distance
import river
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

returncode=0
def check(name,expected,got):
    print("\033[4;30;37m",name,"\033[0;0m")
    print("Expected:",expected)
    print("Got:", got)
    if expected == got:
        print("\033[1;30;42m Passed \033[0;0m", flush=True)
        sys.stdout.flush()
    else:
        print("\033[1;30;41m Failed \033[0;0m", flush=True)
        global returncode
        returncode=1

def result(returncode):
    if returncode==0:
        print("\033[4;30;37m Overall Result: \033[0;0m")
        print("\033[1;30;42m Passed \033[0;0m", flush=True)
        return(0)
    else:
        print("\033[4;30;37m Overall Result: \033[0;0m")
        print("\033[1;30;41m Failed \033[0;0m", flush=True)
        return(1)

#liersbach=osm.trace("http://localhost:8000/osm",3251441)
#Ahr
#river_trace=osm.trace("http://localhost:8000/osm",318372)
# Vischelbach
river_trace=osm.trace("http://localhost:8000/osm",3251005)
#river_trace=osm.trace("http://localhost:8000/osm",3314649)
#river_trace=osm.trace("http://localhost:8000/osm",318375)
points=river_trace.get_points()
traced=river.river(points)
traced.load_dataframe()
print("Dataframe")
print(traced.get_dataframe())
print(traced.get_dataframe().loc[352800:352825,5603500:5603525])


mesh=dgm.grid(25)
mesh.load_from_bbox_utm([(354446.42925326736, 5607050.979783189, 32, 'U'), (369995.93224680924, 5606642.575225855, 32, 'U'), (354015.93088344054, 5591520.967194721, 32, 'U'), (369611.4512380557, 5591112.175551541, 32, 'U'), (354446.42925326736, 5607050.979783189, 32, 'U'), (369995.93224680924, 5606642.575225855, 32, 'U'), (354015.93088344054, 5591520.967194721, 32, 'U'), (369611.4512380557, 5591112.175551541, 32, 'U')])
mesh.inject_dataframe(traced.get_dataframe())
mesh.zones(-10)

zones=mesh.zones_from_utm(357300.0,5595000.0)
#alts=traced.get_altitudes()
#dist=traced.get_distance()
#dists=traced.get_distances()
#bears=traced.get_bearings()
#plt.plot(alts)
#smooth=savgol_filter(alts,51,3)
#plt.plot(dist,alts)
#plt.plot(dist,smooth)
#plt.plot(dist,bears)
#plt.plot(dist,dists)
#plt.show()

result(returncode)
