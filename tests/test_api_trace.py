#!/usr/bin/python3

import osm
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
river_trace=osm.trace("http://localhost:8000/osm",318372)
#river_trace=osm.trace("http://localhost:8000/osm",3314649)
#river_trace=osm.trace("http://localhost:8000/osm",318375)
points=river_trace.get_points()
traced=river.river(points)
alts=traced.get_altitudes()
dist=traced.get_distance()
dists=traced.get_distances()
bears=traced.get_bearings()
#plt.plot(alts)
smooth=savgol_filter(alts,51,3)
#plt.plot(dist,alts)
plt.plot(dist,smooth)
plt.plot(dist,bears)
#plt.plot(dist,dists)
plt.show()

result(returncode)
