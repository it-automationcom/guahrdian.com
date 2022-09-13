#!/usr/bin/python3

import dgm
import utm

mesh=dgm.grid(25)
mesh.flood_zone()
alt=mesh.alt_from_utm(3574,5595)
flood_zone=mesh.flood_zone_from_utm(357300.0,5595000.0)
flood_zone_deg=[]
for i in flood_zone:
    E=i[0]
    N=i[1]
    deg=utm.to_latlon(N,E,32,"U")
    print(deg)
    flood_zone_deg.append(deg)
print(flood_zone_deg)

