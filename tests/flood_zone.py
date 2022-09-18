#!/usr/bin/python3

import dgm
import utm

mesh=dgm.grid(25)
mesh.zones(-170)
alt=mesh.alt_from_utm(3574,5595)
zones=mesh.zones_from_utm(357300.0,5595000.0)
#print(flood_zone_deg)
#print(zones[0])
