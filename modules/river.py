#{{{import
import numpy as np
import geopy.distance
from geographiclib.geodesic import Geodesic as glc
import utm
import dgm
import itertools
import pandas as pd
from scipy.interpolate import griddata
import sys
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
    self.debug=False

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
    if self.debug:
        print("River bbox_utm")
        print(self.bbox_utm)
    self.mesh.load_from_bbox_utm(self.bbox_utm)
    self.altitudes=[]
    for i in self.points:
        alt=self.mesh.alt_from_deg(i)
        self.altitudes.append(alt)
  #}}}
#{{{load_dataframe
  def load_dataframe(self):
   if self.debug:
       print("  ### dgm.river.load_dataframe ###")
   #d create dataframe with altitude values (grid)
   self.dataframe=self.mesh.get_dataframe()  
   if self.debug:
       print("self.dataframe:")
       print(self.dataframe)
   #d create empty dataframe for relative values with the (same size as the default dataframe)
   alt_rel=pd.DataFrame().reindex_like(self.dataframe)
   if self.debug:
       print("alt_rel (empty dataframe)")
       print(alt_rel)
   #Bug: N and E are swapped
   idx_N=[]
   idx_E=[]
#{{{ interpolation (x-direction)
   Z=[]
   #d: the river describes a strictly monotonically decreasing function
   #d: the geolocation of the single nodes do not fit the grid exactly, thus introducting some noise (rising river). In order to fix that we interpolate all of those points
   previous_alt=self.altitudes[0]
   if self.debug:
       print("DEBUG")
       print("River dataframe")
       print(self.dataframe)
       print("Slice")
       print(self.dataframe.loc[5584000.0:5600025.0,:])
   for i in self.points:
       lat=float(i[0])
       lon=float(i[1])
       point_utm=utm.from_latlon(lat,lon)
       N=float(self.fit_grid(point_utm[0]))
       E=float(self.fit_grid(point_utm[1]))
       idx_N.append(N)
       idx_E.append(E)
       try:
           alt=self.dataframe.loc[E,N]
       except:
           print("Exception: can not find altitude for point",i)
           print("East:",E)
           print("North:",N)
           print("does not exist in dataframe")
           print(self.dataframe)
           sys.exit(1)
       if alt <= previous_alt:
           Z.append(alt)
           previous_alt=alt
       elif np.isnan(previous_alt):
           #d in case there is no altitude value for the spring or previous node
           Z.append(np.nan)
           previous_alt=alt
       else:
           Z.append(previous_alt)
#}}}
   N=self.dataframe.columns.values
   E=self.dataframe.index.values
   mesh_n,mesh_e=np.meshgrid(N,E)
   zi=griddata((idx_N,idx_E),Z,(mesh_n,mesh_e),method='nearest')
   z1=self.dataframe.to_numpy()
   rel=z1.__sub__(zi)
   alts_rel=pd.DataFrame(rel,columns=[N.tolist()],index=[E.tolist()])
   self.dataframe=alts_rel
   alts_rel.set_axis(E.tolist(),axis=0)
   alts_rel.reindex_like(self.dataframe)
  #}}}
  #{{{fit_grid
  def fit_grid(self,x):
    return self.meshsize * round(x/self.meshsize)
  #}}}
  #{{{get_altitudes
  def get_altitudes(self):
     # desc: the river describes a strictly monotically decreasing function
     # the geolocation of the single nodes do not fit the grid exactly, thus introducing some noise (rising river). In order to fix that we interpolate all of those points
     alts_smooth=list()
     previous_alt=self.altitudes[0]
     for alt in self.altitudes:
         if alt <= previous_alt:
             alts_smooth.append(alt)
             previous_alt=alt
         elif np.isnan(previous_alt):
             # in case that there is no altitude value for the spring or previous node
             previous_alt=alt
         else:
             alts_smooth.append(previous_alt)
     #return(self.altitudes)
     return(alts_smooth)
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
