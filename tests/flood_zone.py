#!/usr/bin/python3

import dgm
import utm

mesh=dgm.grid(25)
mesh.flood_zone()
alt=mesh.alt_from_utm(3574,5595)

zones=mesh.flood_zone_from_utm(357300.0,5595000.0)
flood_zone_deg=[]
#print(flood_zone_deg)
#print(zones[0])
print(mesh.get_edges())
