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
import rasterio.features as riof

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
  def alt_from_utm(self,utm):
      N=float(self.fit_grid(utm[0]))
      E=float(self.fit_grid(utm[1]))
      try:
          alt=self.dataframe.loc[E,N]
      except:
          alt=None
      return(alt)
#}}}
#{{{alt_from_deg
  def alt_from_deg(self,location):
      lat=float(location[0])
      lon=float(location[1])
      location_utm=utm.from_latlon(lat,lon)
      alt=self.alt_from_utm(location_utm)
      return(alt)
#}}}
#{{{load_from_bbox_deg
  def load_from_bbox_deg(self,bbox):
      print(bbox)
#}}}
#{{{load_from_bbox_utm
  def load_from_bbox_utm(self,bbox):
      max_e=self.fit_grid(max(bbox,key=lambda item:item[1])[1])
      max_n=self.fit_grid(max(bbox,key=lambda item:item[0])[0])
      min_e=self.fit_grid(min(bbox,key=lambda item:item[1])[1])
      min_n=self.fit_grid(min(bbox,key=lambda item:item[0])[0])
      self.xyz={}
      for i in range(int(str(min_n)[:2]),int(str(max_n)[:2])+1):
          for j in range(int(str(min_e)[:3]),int(str(max_e)[:3])+1):
            name=str(i)+str(0)+str(j)+str(0)
            dgmfile="/var/www/html/dgm/"+str(self.mesh)+"/DGM"+str(self.mesh)+"_"+str(name)+".xyz"
            file_location=os.path.join('data',dgmfile)
            try:
                xyz_file = np.genfromtxt(fname=file_location, dtype='unicode')
            except:
                print(file_location,"not found")
                continue
#            print(dgmfile)
            coordinates = (xyz_file[:,:])
#            print(coordinates)
            for x in coordinates:
              if float(x[0]) not in self.xyz:
                  self.xyz[float(x[0])]={}
            for y in coordinates:
              self.xyz[float(y[0])][float(y[1])]=float(y[2])
      self.dataframe=pd.DataFrame.from_dict(self.xyz)
      #print(self.dataframe)
      df_min_e=int(self.dataframe.index[0])
      df_max_e=int(self.dataframe.index[-1])
      df_min_n=int(self.dataframe.columns[0])
      df_max_n=int(self.dataframe.columns[-1])
      #print(df_min_e)
      if df_min_e > min_e:
          min_e=df_min_e
      #print(min_e)
      if df_max_e < max_e:
        max_e=df_max_e
      #print(df_max_e)
      #print(max_e)
      if df_min_n > min_n:
          min_n=df_min_n
      if df_max_n < max_n:
        max_n=df_max_n
      #print(df_min_n)
      #print(min_n)
      #print(df_max_n)
      #print(max_n)
      self.dataframe=self.dataframe.loc[min_e:max_e,min_n:max_n]
#      print(self.dataframe)
#}}}
#{{{inject_dataframe
  def inject_dataframe(self,dataframe):
      self.dataframe=dataframe
#}}}
#{{{get_dataframe
  def get_dataframe(self):
      return(self.dataframe)
#}}}
#{{{fit_grid
  def fit_grid(self,x):
    return self.mesh * round(x/self.mesh)
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
    #zone=self.dataframe.loc[N-10000:N+10000,E-10000:E+10000].gt(520)
    zone=self.dataframe.gt(520)
    self.zones_utm=[]
    self.zones_deg=[]
    self.edges=None
    self.points_utm=zone
    self.stack=None
    #}}} 
    #{{{label features (find distinct zones)
    # set ajacency
    s=[[1,1,1],
       [1,1,1],
       [1,1,1]]
    labeled_array, num_features = label(polygon, structure=s)
    # create a pandas dataframe from labeled features
    print(labeled_array)
    features=pd.DataFrame(labeled_array)
    features.set_axis(list(zone.axes[0]), axis=0, inplace=True)
    features.set_axis(list(zone.axes[1]), axis=1, inplace=True)
    print(features)
    #}}}
    #{{{loop over zones (find features)
    objects=ndimage.find_objects(features)
    print("Found Objects:",len(objects))
    for i in range(len(objects)):
        print("Run algorithm for Object", i)
        loc=objects[i]
        #polygon_slice=polygon.iloc[loc]
        polygon_slice=features.iloc[loc]
        print("Polygon slice")
        print(polygon_slice)

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
#{{{get_edges
  def get_edges(self):
    return(self.stack) 
#}}}
#{{{get_point_cloud
  def get_point_cloud(self):
    stack=self.points_utm[self.points_utm.isin([True])].stack()
    points_cloud=[]
    for index,value in (stack.iteritems()):
        E=index[0]
        N=index[1]
        deg=utm.to_latlon(N,E,32,"U")
        points_cloud.append(deg)
    return(points_cloud)
#}}}
#}}}
#{{{zones
#{{{zone
  def zones(self,level):
    self.level=level
    self.utm={"E":None,"N":None}
    self.zones_utm=[]
    self.zones_deg=[]
    #print(self.level)
#}}}
#{{{zone_from_utm
  def zones_from_utm(self,E,N):
    #{{{setup
    self.utm["E"]=E
    self.utm["N"]=N
    #}}}
    #{{{select zones by altitude 
    if self.level >=0:
        #self.zones=self.dataframe.loc[N-30000:N+30000,E-30000:E+30000].gt(self.level)
        self.zones=self.dataframe.gt(self.level)
    elif self.level <0:
        #self.zones=self.dataframe.loc[N-30000:N+30000,E-30000:E+30000].lt(self.level*-1)
        self.zones=self.dataframe.lt(self.level*-1)
    #print(self.zones)
    #}}}
    #{{{label different zones
    #set adjacency
    s=[[1,1,1],
       [1,1,1],
       [1,1,1]]
    # find labels
    labeled_zones, num_features = label(self.zones, structure=s)
    #print("Found Features:",num_features)
    #print(labeled_zones)
    # create pandas dataframe from labels
    labeled_df=pd.DataFrame(labeled_zones)
    labeled_df.set_axis(list(self.zones.axes[0]), axis=0, inplace=True)
    labeled_df.set_axis(list(self.zones.axes[1]), axis=1, inplace=True)
    #}}} 
    #{{{loop over distinct features
    objects=ndimage.find_objects(labeled_df)
    polygons_utm=[]
    polygons_deg=[]
    for i in range(len(objects)):
        ##{{{get slice
        iloc=objects[i]
        #print("labeled_df")
        #print(labeled_df)
        sliced=labeled_df.iloc[iloc].isin([i+1]).astype(int)
        #print("sliced")
        #print(sliced)
        N0=sliced.columns[0]
        E0=sliced.index[0]
        #print("N",N)
        #print("E",E)
        #}}}
        #{{{create a polygon from the slice 
        sliced_np=sliced.to_numpy()
        #print(sliced_np)
        # identic
        #t_matrix=(1,0,0,0,1,0)
        # 90 deg
        t_matrix=(0,1,0,1,0,0)
        maskshape=riof.shapes(sliced_np.astype('uint8'),connectivity=8,transform=t_matrix)
        for vec in maskshape:
            polygon_utm=[]
            polygon_deg=[]
            if vec[1] == 1:
                # FIXME: subtract inner polygons ([1]to[n]?)
                outer=vec[0]["coordinates"][0]
                #print(outer)
                for i in outer:
                    idx=int(i[0])
                    col=int(i[1])
                    try:
                        #E=sliced.index[idx]
                        #N=sliced.columns[col]
                        E=E0[0]+idx*self.mesh
                        N=N0[0]+col*self.mesh
                        polygon_utm.append([N,E])
                        utm_zone=32
                        utm_hemi="U"
                        deg=utm.to_latlon(N,E,utm_zone,utm_hemi)
                        lat=deg[0]
                        lon=deg[1]
                        polygon_deg.append([lat,lon])
                    except Exception as e: 
                        print(str(e))
            polygons_utm.append(polygon_utm)
            polygons_deg.append(polygon_deg)
    return(polygons_deg)
        #}}}
    #}}}
#}}}
#}}}
#{{{interpolation
  def interpolation(self,step):
      df=self.dataframe
      #df.rename_axis("East", axis=0, inplace=True)
      #df.rename_axis("North", axis=1, inplace=True)
      idx_first=int(df.index[0])
      idx_last=int(df.index[-1])
      col_first=int(df.columns[0])
      col_last=int(df.columns[-1])
      idf=pd.DataFrame(index=range(idx_first,idx_last+1,step),columns=range(col_first,col_last+1,step))
      ndf=df.reindex_like(idf,method=None)
      ndf.interpolate(axis=0,inplace=True)
      ndf.interpolate(axis=1,inplace=True)
      #ndf.rename_axis("East", axis=0, inplace=True)
      #ndf.rename_axis("North", axis=1, inplace=True)
      self.dataframe=ndf
#      print(df)
#      print(ndf)
      self.mesh=step
#}}}
# vim:foldmethod=marker:foldlevel=0
