#!/usr/bin/python3

import osm
import dgm
import pbf

map0=osm.map()
map0.set_boundaries(3,3,3,3)
map0.from_deg(6.98,50.51,12)
maplayer0=osm.maplayer(map0)
maplayer1=osm.maplayer(map0)
maplayer2=osm.maplayer(map0)
maplayer3=osm.maplayer(map0)
#point0=osm.point(7,50.2,maplayer0)
point1=osm.point(maplayer0)
point1.from_deg(7,50.2)
#points=osm.trace.nodes()
#
#for i in points:
#  lon=float(i[0])
#  lat=float(i[1])
#  point0=osm.point(maplayer0)
#  point0.from_deg(lat,lon)

#polyline0=osm.polyline(points,maplayer1)
#shadow0=osm.shadow(points,maplayer1)
#mesh=dgm.grid(25)
#mesh.flood_zone()
#alt=mesh.alt_from_utm(3574,5595)
#flood_zone=mesh.flood_zone_from_utm(357300.0,5595000.0)
#for i in flood_zone:
#    point2=osm.point(maplayer0)
#    point2.from_utm(i[0],i[1],32,"U")

#for i in (3309646,3314649,3244913,318372,3151697,3251441,318375):
for i in (3251005,3309646):
    obj1=pbf.trace(i)
    pbf1=obj1.get()
    for j in pbf1:
        lon=float(j[0])
        lat=float(j[1])
        point3=osm.point(maplayer2)
        point3.from_deg(lat,lon)
    polyline1=osm.polyline(pbf1,maplayer3)

print("<html><head><link rel=\"stylesheet\" href=\"style.css\"/></head><body>")
for i in range(1,10,1):
    print("<button type=\"button\" onclick=\"alert(\'No Function!\')\">Disable/Enable Layer",i,"</button>")
print("<div class=\"mapcontainer\">")
print("<div class=\"map\" style=\"position:relative\">")

#maplayer0.display()
#maplayer1.display()
maplayer2.display()
maplayer3.display()
map0.display()
print("Map")
print("<br>")
map0.print()
print("<br>")
print("Maplayer")
print("<br>")
maplayer0.print()
print("<br>")
print("Point")
print("<br>")
#point0.print()
print("<br>")
#point1.print()
print("</div>")
print("</div>")
print("</body></html>")
