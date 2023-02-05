#!/usr/bin/python3

import osm
import dgm
import geopy.distance
import river
import numpy as np
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
#river_trace=osm.trace("http://localhost:8000/osm",3251005)
# Kesselinger Bach
river_trace=osm.trace("http://localhost:8000/osm",318375)
# Sahrbach
#river_trace=osm.trace("http://localhost:8000/osm",3244913)
# Steinbergsbach
#river_trace=osm.trace("http://localhost:8000/osm",2101082)
points=river_trace.get_points()
traced=river.river(points)
traced.load_dataframe()
print("Dataframe")
df=traced.get_dataframe()
print(df)
print("get level values")
print(df.index.get_level_values(0))
print(df.columns.get_level_values(0))
df.index=df.index.get_level_values(0)
df.columns=df.columns.get_level_values(0)
print(df.index)
print(df.index)
print(traced.get_dataframe().loc[352800:352825,5603500:5603525])

alts=traced.get_altitudes()
print(alts)
previous_alt=alts[0]

alts_smooth=list()
for alt in alts:
    if alt <= previous_alt:
        alts_smooth.append(alt)
        previous_alt=alt
    elif np.isnan(previous_alt):
        alts_smooth.append(np.nan)
        previous_alt=alt
    else:
        alts_smooth.append(previous_alt)
print(alts_smooth)
dist=traced.get_distance()
dists=traced.get_distances()
bears=traced.get_bearings()
#plt.plot(alts)
smooth=savgol_filter(alts,51,3)
smooth1=savgol_filter(alts,21,3)
#plt.plot(dist,alts)
plt.plot(dist,alts_smooth)
#plt.plot(dist,smooth)
#plt.plot(dist,bears)
#plt.plot(dist,dists)
plt.show()

result(returncode)
