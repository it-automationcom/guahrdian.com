#!/usr/bin/python3

import osm
import geopy.distance

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
river=osm.trace("http://localhost:8000/osm",318372)
#print(ahr.get_points())
distance=0
points=river.get_points()
previous=points[0]
total=0
for i in points:
    distance=geopy.distance.geodesic(previous,i).km
    total=total+distance
    print(total)
    previous=i



result(returncode)
