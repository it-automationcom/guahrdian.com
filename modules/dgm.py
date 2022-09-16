#{{{import
import numpy as np
import osm
import os
import pandas as pd
import utm
from skimage import feature
import math
from scipy import ndimage
from scipy.ndimage import label, generate_binary_structure

#}}}
#{{{class grid
class grid:
#{{{__init__
  def __init__(self,mesh):
    self.mesh=mesh
    self.name=None
    self.file=None
    self.dataframe=None
#}}}
#{{{alt_from_utm
  def alt_from_utm(self,n,e):
    for i in range(len(str(n)),6,1):
      n=int(str(n)+str(0))
    for i in range(len(str(e)),7,1):
      e=int(str(e)+str(0))
    grid_n=round(n)
    grid_e=round(e)
    self.name=str(grid_n)[:2]+str(0)+str(grid_e)[:3]+str(0)
    self.file="/var/www/html/dgm/"+str(self.mesh)+"/DGM"+str(self.mesh)+"_"+str(self.name)+".xyz"
    file_location=os.path.join('data',self.file)
    xyz_file = np.genfromtxt(fname=file_location, dtype='unicode')
    coordinates = (xyz_file[:,:])
    self.xyz={}
    for x in coordinates:
      self.xyz[float(x[0])]={}
    for y in coordinates:
      self.xyz[float(y[0])][float(y[1])]=float(y[2])
    self.dataframe=pd.DataFrame.from_dict(self.xyz)
    return self.xyz[float(grid_n)][float(grid_e)]
  def round(self,x):
    return self.mesh * round(x/base)
#}}}
#{{{alt_from_deg
  def alt_from_deg(self,lat,lon):
    print("Altitude from deg")
    print(lat)
    print(lon)
    # convert lat lon to utm
    node_utm=utm.from_latlon(lat,lon)
    print(node_utm)
    # convert lat lon to utm and invoke self.alt_from_utm
    N=node_utm[1]
    print(N)
    E=node_utm[0]
    print(E)
    alt=self.alt_from_utm(N,E)
    print(alt)

#}}}
#{{{generate_stl
  def generate_stl(self):
    length_x=len(self.dataframe.axes[1])
    length_y=len(self.dataframe.axes[0])
    print(self.dataframe.iloc[0:length_x,0:length_y])
    print("solid",self.name)
    df=self.dataframe
    scale=1
    mesh=self.mesh
    for x in range(length_x-1):
        for y in range(length_y-1):
            print("facet normal 0 0 0")
            print("   outer loop")
            print("     vertex", x*25, y*25 , scale*df.iloc[x,y])
            print("     vertex", x*25+25, y*25 , scale*df.iloc[x+1,y])
            print("     vertex", x*25, y*25+25 , scale*df.iloc[x,y+1])
            print("  endloop")
            print("endfacet")
            print("facet normal 0 0 0")
            print("   outer loop")
            print("     vertex", x*25+25, y*25 , scale*df.iloc[x+1,y])
            print("     vertex", x*25+25, y*25+25 ,scale*df.iloc[x+1,y+1])
            print("     vertex", x*25, y*25+25 ,scale*df.iloc[x,y+1])
            print("  endloop")
            print("endfacet")
    print("endsolid",self.name)
#}}}
#{{{flood_zone
#{{{flood_zone
  def flood_zone(self):
    self.level=None
    self.utm={"E":None,"N":None}
#}}}
#{{{flood_zone_from_utm
  def flood_zone_from_utm(self,E,N):
    #{{{setup
    self.utm["E"]=E
    self.utm["N"]=N
    zone=self.dataframe.loc[N-10000:N+10000,E-10000:E+10000].gt(500)
    self.zones_utm=[]
    self.zones_deg=[]
    #}}} 
    #{{{find edges with canny filter)
    # calculate edges
    edges=feature.canny(zone.to_numpy())
    polygon=pd.DataFrame(edges)
    polygon.set_axis(list(zone.axes[0]), axis=0, inplace=True)
    polygon.set_axis(list(zone.axes[1]), axis=1, inplace=True)
    #}}}
    #{{{label features (find distinct zones)
    # set ajacency
    s=[[1,1,1],
       [1,1,1],
       [1,1,1]]
    labeled_array, num_features = label(polygon, structure=s)
    # create a pandas dataframe from labeled features
    features=pd.DataFrame(labeled_array)
    features.set_axis(list(zone.axes[0]), axis=0, inplace=True)
    features.set_axis(list(zone.axes[1]), axis=1, inplace=True)
    #}}}
    #{{{debug
    #print(features)
    #loc=obj1[0]
    #print(labeled_array[loc])
    #print(features.iloc[loc])
    #loc=obj1[1]
    #print(labeled_array[loc])
    #print(features.iloc[loc])
    #labeled_array, num_features = label(polygon)
    #print("Found Features:",num_features)
    #print("Labeled Array:",labeled_array)
    #}}}
    #{{{loop over zones (find features)
    objects=ndimage.find_objects(features)
    #print("Found Objects:",len(objects))
    for i in range(len(objects)):
        loc=objects[i]
        #print(i)
        #print(loc)
        polygon_slice=polygon.iloc[loc]
        #print(polygon_slice)
        # Currently feature is represented as Bool (can result in overlapping) change to labels FIXME
        stack=polygon_slice[polygon_slice.isin([1])].stack()
        zone=[]
        for index,value in (stack.iteritems()):
            zone.append(index)
            # sort by plolar coordinates around center (this only works if the center is within the area: FIXME)
            center=sum(p[0] for p in zone)/len(zone),sum(p[1] for p in zone)/len(zone)
            zone.sort(key=lambda p: math.atan2(p[1]-center[1],p[0]-center[0]))
        self.zones_utm.append(zone)
        #print("Zone",i,":",zone)

    #loc=objects[5]
    # output as point cloud
    #stack=zone[zone.isin([True])].stack()
    # output as outline
    #stack=polygon[polygon.isin([True])].stack()
    # only first object
    stack=polygon_slice[polygon_slice.isin([1])].stack()
    #print(stack)
    flood_zone=[]
    for index,value in (stack.iteritems()):
        flood_zone.append(index)
    # sort points by polar coordinates
    center=sum(p[0] for p in flood_zone)/len(flood_zone),sum(p[1] for p in flood_zone)/len(flood_zone)
    flood_zone.sort(key=lambda p: math.atan2(p[1]-center[1],p[0]-center[0]))
    #return(flood_zone)
    #{{{translate utm to deg
    for i in range(len(self.zones_utm)):
        self.zones_deg.append([])
        #print(self.zones_deg)
        for j in range(len(self.zones_utm[i])):
                E=self.zones_utm[i][j][0]
                N=self.zones_utm[i][j][1]
                deg=utm.to_latlon(N,E,32,"U")
                self.zones_deg[i].append(deg)
    #}}}
    return(self.zones_deg)
#}}}
#}}}
#{{{print
  def print(self):
    print("Mesh:",self.mesh)
    print("Name:",self.name)
    print("File:",self.file)
    print(self.dataframe)
#}}}
#}}}
# vim:foldmethod=marker:foldlevel=0
