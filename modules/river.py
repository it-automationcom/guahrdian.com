#{{{import
import numpy as np
import geopy.distance
from geographiclib.geodesic import Geodesic as glc
import utm
import dgm
import itertools
import pandas as pd
from scipy.interpolate import griddata

#}}}
#{{{class river
class river:
  #{{{__init__
  def __init__(self,points):
    self.points=points
    self.bbox_deg=None
    self.bbox_utm=None
    self.altitudes=None
    self.distances=None
    self.distance=None
    self.bearings=None
    river={}
    self.mesh=None
    self.dataframe=None
    self.meshsize=25

    # Calculate distances and bearing 
    previous=points[0]
    self.distances=[]
    self.distance=[]
    self.bearings=[]

    total_distance=0
    for i in self.points:
        i=(list(map(float,i)))
        distance=geopy.distance.geodesic(previous,i).km
        self.distances.append(distance)
        total_distance=total_distance+distance
        self.distance.append(total_distance)
        bear=glc.WGS84.Inverse(float(previous[0]),float(previous[1]),float(i[0]),float(i[1]))
        previous=i
        azi=bear["azi1"]
        self.bearings.append(azi)
    self.length=total_distance

    # bbox deg
    lat_max=float(max(points,key=lambda item:item[0])[0])
    lon_min=float(min(points,key=lambda item:item[1])[1])
    lat_min=float(min(points,key=lambda item:item[0])[0])
    lon_max=float(max(points,key=lambda item:item[1])[1])
    self.bbox_deg=[(lat_max,lon_min),(lat_min,lon_max)]

    # bbox utm
    utm_nw=utm.from_latlon(lat_max,lon_min)
    utm_ne=utm.from_latlon(lat_max,lon_max)
    utm_se=utm.from_latlon(lat_min,lon_max)
    utm_sw=utm.from_latlon(lat_min,lon_min)
    self.bbox_utm=(utm_nw,utm_ne,utm_se,utm_sw)
   
    # get altitudes
    self.mesh=dgm.grid(self.meshsize)
    self.mesh.load_from_bbox_utm(self.bbox_utm)
    self.altitudes=[]
    for i in self.points:
        alt=self.mesh.alt_from_deg(i)
        self.altitudes.append(alt)
  #}}}
#{{{load_dataframe
  def load_dataframe(self):
   self.dataframe=self.mesh.get_dataframe()  
   alt_rel=pd.DataFrame().reindex_like(self.dataframe)
   idx_N=[]
   idx_E=[]
   Z=[]
   for i in self.points:
       lat=float(i[0])
       lon=float(i[1])
       point_utm=utm.from_latlon(lat,lon)
       N=float(self.fit_grid(point_utm[0]))
       E=float(self.fit_grid(point_utm[1]))
       idx_N.append(N)
       idx_E.append(E)
       alt=self.dataframe.loc[E,N]
       Z.append(alt)
   #print(len(idx_N))
   #print(len(idx_E))
   #print(len(Z))
   #print("")
   #print("Dataframe")
   #print(self.dataframe.unstack())
   N=self.dataframe.columns.values
   E=self.dataframe.index.values
   #print(N)
   #print(E)
   mesh_n,mesh_e=np.meshgrid(N,E)
   #print(mesh_n)
   #print(mesh_e)
   zi=griddata((idx_N,idx_E),Z,(mesh_n,mesh_e),method='nearest')
   #print(zi)
   z1=self.dataframe.to_numpy()
   #print(z1)
   rel=z1.__sub__(zi)
   #print(rel)
   #print(rel)
   print(E)
   print(type(E.tolist()))
   alts_rel=pd.DataFrame(rel,columns=[N.tolist()],index=[E.tolist()])
   #print(self.dataframe)
   self.dataframe=alts_rel
   print("alts_rel")
   print(alts_rel.axes[0])
   alts_rel.set_axis(E.tolist(),axis=0)
   print(alts_rel.axes[0])
   alts_rel.reindex_like(self.dataframe)
   print(alts_rel.axes[0])
  #}}}
  #{{{fit_grid
  def fit_grid(self,x):
    return self.meshsize * round(x/self.meshsize)
  #}}}
  #{{{get_altitudes
  def get_altitudes(self):
     return(self.altitudes)
  #}}}
  #{{{get_dataframe
  def get_dataframe(self):
     return(self.dataframe)
  #}}}
  #{{{get_points
  def get_points(self):
     return(self.points)
  #}}}
  #{{{get_distances
  def get_distances(self):
     return(self.distances)
  #}}}
  #{{{get_distance
  def get_distance(self):
     return(self.distance)
  #}}}
  #{{{get_bearings
  def get_bearings(self):
     return(self.bearings)
  #}}}
  #{{{print  
  def print(self):
      print("River")
      print("  self.length=",self.length)
      print("  self.bbox_deg=",self.bbox_deg)
      print("  self.bbox_utm=",self.bbox_utm)
      print("  self.points=",self.points[:2],"...",self.points[-2:])
      print("  self.altitudes=",self.altitudes[:2],"...",self.altitudes[-2:])
      print("  self.distances=",self.distances[:2],"...",self.distances[-2:])
      print("  self.distance=",self.distance[:2],"...",self.distance[-2:])
      print("  self.bearings=",self.bearings[:2],"...",self.bearings[-2:])
   #}}}
#}}}
# vim:foldmethod=marker:foldlevel=0
