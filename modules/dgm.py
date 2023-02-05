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
import geopy.distance
import math
from scipy.interpolate import griddata
import gzip
import gumath 
#}}}
#{{{class grid
class grid:
#{{{__init__
  def __init__(self,mesh):
    self.mesh=mesh
    self.name=None
    self.file=None
    self.dataframe=None
    self.debug=False
#}}}
#{{{alt_from_utm
  def alt_from_utm(self,utm):
      # fix: interpolate
      N1=float(self.mesh * math.floor(utm[0]/self.mesh))
      N2=float(self.mesh * math.ceil(utm[0]/self.mesh))
      E1=float(self.mesh * math.floor(utm[1]/self.mesh))
      E2=float(self.mesh * math.ceil(utm[1]/self.mesh))
      N1_loc=self.dataframe.columns.get_loc(N1)
      N2_loc=self.dataframe.columns.get_loc(N2)
      E1_loc=self.dataframe.index.get_loc(E1)
      E2_loc=self.dataframe.index.get_loc(E2)
      NW_alt=self.dataframe.loc[E1,N1]
      NE_alt=self.dataframe.loc[E2,N1]
      SE_alt=self.dataframe.loc[E2,N2]
      SW_alt=self.dataframe.loc[E1,N2]
      # use griddata for the interpolation https://scipython.com/book/chapter-8-scipy/examples/two-dimensional-interpolation-with-scipyinterpolategriddata/      
      x_coord=np.linspace(1,2,2)
      y_coord=np.linspace(1,2,2)
      x_grid,ygrid=np.meshgrid(x_coord,y_coord)
      N=float(self.fit_grid(utm[0]))
      E=float(self.fit_grid(utm[1]))
      #alt=self.dataframe.loc[E,N]
      #print("###")
      #print(alt)
      n=[(E1,N1,NW_alt),
         (E2,N1,NE_alt),
         (E2,N2,SE_alt),
         (E1,N2,SW_alt)]
      alt=gumath.bilinear_interpolation(utm[1],utm[0],n) 
      #print(alt)
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
      bbox=list(map(float,bbox))
      nw_lat=bbox[1]
      nw_lon=bbox[3]
      se_lat=bbox[0]
      se_lon=bbox[2]
      nw_utm=utm.from_latlon(nw_lat,nw_lon)
      se_utm=utm.from_latlon(se_lat,se_lon)
      self.load_from_bbox_utm([nw_utm,se_utm])
#}}}
#{{{load_from_bbox_utm
  def load_from_bbox_utm(self,bbox):
      # ensure dataframe is big enough (add 1 step on either side)
      max_e=self.fit_grid(max(bbox,key=lambda item:item[1])[1])+self.mesh
      max_n=self.fit_grid(max(bbox,key=lambda item:item[0])[0])+self.mesh
      min_e=self.fit_grid(min(bbox,key=lambda item:item[1])[1])-self.mesh
      min_n=self.fit_grid(min(bbox,key=lambda item:item[0])[0])-self.mesh
      self.xyz={}
      missing25=list()
      for i in range(int(str(min_n)[:2]),int(str(max_n)[:2])+1):
          for j in range(int(str(min_e)[:3]),int(str(max_e)[:3])+1):
            name=str(i)+str(0)+str(j)+str(0)
            dgmfile="/var/www/html/dgm/"+str(self.mesh)+"/DGM"+str(self.mesh)+"_"+str(name)+".xyz"
            file_location=os.path.join('data',dgmfile)
            if self.debug:
                print(dgmfile)
                print(os.system("wc -l "+dgmfile))
            try:
                xyz_file = np.genfromtxt(fname=file_location, dtype='unicode')
            except:
                print(file_location,"not found")
                print("not found E:",j)
                print("not found N:",i)
                missing25.append((i,j))
                os.system("scripts/create_dgm25 "+str(i)+" "+str(j))
                continue
            coordinates = (xyz_file[:,:])
            for x in coordinates:
              if float(x[0]) not in self.xyz:
                  self.xyz[float(x[0])]={}
            for y in coordinates:
              self.xyz[float(y[0])][float(y[1])]=float(y[2])
      # add missing values from dgm1 dataframes
      if self.debug:
          print("missing25")
          print(missing25)
      #for n in missing25:
      #    for m in range(9):
      #        for o in range(9):
      #            dgmfile="/var/www/html/dgm/1/dgm1_32_"+str(n[0])+str(m)+"_"+str(n[1])+str(o)+"_1_nw.xyz.gz"
      #            file_location=os.path.join('data',dgmfile)
      #            print(np.genfromtxt(file_location, dtype='unicode'))
      self.dataframe=pd.DataFrame.from_dict(self.xyz)
      df_min_e=int(self.dataframe.index[0])
      df_max_e=int(self.dataframe.index[-1])
      df_min_n=int(self.dataframe.columns[0])
      df_max_n=int(self.dataframe.columns[-1])
      if df_min_e > min_e:
          min_e=df_min_e
      if df_max_e < max_e:
        max_e=df_max_e
      if df_min_n > min_n:
          min_n=df_min_n
      if df_max_n < max_n:
        max_n=df_max_n
      self.dataframe=self.dataframe.loc[min_e:max_e,min_n:max_n]
#}}}
#{{{inject_dataframe
  def inject_dataframe(self,dataframe):
      self.dataframe=dataframe
      # FIXME: index gets injected as Multiindex
      # BUGFIX: flatten index
      self.dataframe.index=self.dataframe.index.get_level_values(0)
      self.dataframe.columns=self.dataframe.columns.get_level_values(0)
      if self.debug:
          print("Dataframe")
          print(self.dataframe)
#}}}
#{{{get_dataframe
  def get_dataframe(self):
      return(self.dataframe)
#}}}
#{{{fit_grid
  def fit_grid(self,x):
    return self.mesh * round(x/self.mesh)
#}}}
#{{{generate_stl_utm
  def generate_stl(self):
    length_x=len(self.dataframe.axes[0])
    length_y=len(self.dataframe.axes[1])
    print("solid",self.name)
    df=self.dataframe
    scale=1
    mesh=self.mesh
    for x in (range(length_x+1)):
        for y in (range(length_y+1)):
            print("facet normal 0 0 0")
            print("   outer loop")
            print("     vertex", x*self.mesh, y*self.mesh , scale*df.iloc[x,y])
            print("     vertex", x*self.mesh+self.mesh, y*self.mesh , scale*df.iloc[x+1,y])
            print("     vertex", x*self.mesh, y*self.mesh-self.mesh , scale*df.iloc[x,y+1])
            print("  endloop")
            print("endfacet")
            print("facet normal 0 0 0")
            print("   outer loop")
            print("     vertex", x*self.mesh+self.mesh, y*self.mesh , scale*df.iloc[x+1,y])
            print("     vertex", x*self.mesh-x*self.mesh+self.mesh, y*self.mesh-self.mesh ,scale*df.iloc[x+1,y+1])
            print("     vertex", x*self.mesh, y*self.mesh-self.mesh ,scale*df.iloc[x,y+1])
            print("  endloop")
            print("endfacet")
    print("endsolid",self.name)
#}}}
#{{{generate_stl_deg
  def generate_stl_deg(self,osmmap):
      nw=[osmmap.get_bbox_deg()[0]["lat"],osmmap.get_bbox_deg()[0]["lon"]]
      ne=[osmmap.get_bbox_deg()[1]["lat"],osmmap.get_bbox_deg()[1]["lon"]]
      se=[osmmap.get_bbox_deg()[2]["lat"],osmmap.get_bbox_deg()[2]["lon"]]
      sw=[osmmap.get_bbox_deg()[3]["lat"],osmmap.get_bbox_deg()[3]["lon"]]
      xdiff=(osmmap.get_bbox_deg()[1]["lon"]-osmmap.get_bbox_deg()[0]["lon"])
      ydiff=(osmmap.get_bbox_deg()[0]["lat"]-osmmap.get_bbox_deg()[2]["lat"])
      xdist=geopy.distance.geodesic(nw,ne).km
      ydist=geopy.distance.geodesic(nw,sw).km
      xsteps=math.ceil(xdist/0.025)
      ysteps=math.ceil(ydist/0.025)
      xstep=xdiff/xsteps
      # fix: use np.linspace(start,end,xteps) instead of calculating steps
      xstep_dist=1000*xdist/xsteps
      ystep_dist=1000*ydist/ysteps
      columns=np.arange(nw[1],ne[1],xstep)
      ystep=ydiff/ysteps
      index=np.arange(nw[0],sw[0],-ystep)
      df_deg=pd.DataFrame(columns=columns, index=index)
      for i in columns:
        for j in index:
          location=[j,i]
          df_deg[i][j]=self.alt_from_deg(location)
      length_x=len(df_deg.axes[0])
      length_y=len(df_deg.axes[1])
      scale=1
      print("solid",self.name)
      for x in (range(length_x-1)):
        for y in (reversed(range(length_y-1))):
              print ("facet normal 0 0 0") 
              print ("  outer loop")
              print ("    vertex", x*xstep_dist, y*ystep_dist, scale*df_deg.iloc[x,y])
              print ("    vertex", x*xstep_dist+xstep_dist, y*ystep_dist, scale*df_deg.iloc[x+1,y])
              print ("    vertex", x*xstep_dist, y*ystep_dist+ystep_dist, scale*df_deg.iloc[x,y+1])
              print ("  endloop")
              print ("endfacet")
              print ("facet normal 0 0 0") 
              print ("  outer loop")
              print ("    vertex", x*xstep_dist+xstep_dist, y*ystep_dist, scale*df_deg.iloc[x+1,y])
              print ("    vertex", x*xstep_dist+xstep_dist, y*ystep_dist+ystep_dist, scale*df_deg.iloc[x+1,y+1])
              print ("    vertex", x*xstep_dist, y*ystep_dist+ystep_dist, scale*df_deg.iloc[x,y+1])
              print ("  endloop")
              print ("endfacet")
      print("endsolid")
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
#{{{get_point_cloud_deg
  def get_point_cloud_deg(self):
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
#{{{zones_from_utm
  def zones_from_utm(self,E,N):
    #{{{setup
    self.utm["E"]=E
    self.utm["N"]=N
    if self.debug:
        print("Zones Dataframe")
        print(self.dataframe)
        print("Level")
        print(self.level)
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
                        # if Multindex
                        #E=E0[0]+idx*self.mesh
                        #N=N0[0]+col*self.mesh
                        # if flat index
                        E=E0+idx*self.mesh
                        N=N0+col*self.mesh
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
#}}} 
#{{{class altitude
class altitude:
    def from_deg(lat,lon):
        loc_utm=utm.from_latlon(float(lat),float(lon))
        return altitude.from_utm(loc_utm)
    def from_utm(utm):
        n=int(str(utm[0])[:2])
        e=int(str(utm[1])[:3])
        name=str(n)+str(0)+str(e)+str(0)
        dgmfile="/var/www/html/dgm/25/DGM25_"+str(name)+".xyz"
        file_location=os.path.join('data',dgmfile)
        try: 
            xyz_file = np.genfromtxt(fname=file_location, dtype='unicode')
        except:
            print(file_location,"not found")
        altitudes=dict()
        for i in xyz_file:
            altitudes[float(i[0])]=dict()
        for i in xyz_file:
            altitudes[float(i[0])][float(i[1])]=float(i[2])
        ## FIX: add interpolation rather than fitting to the grid
        n=float(25*round(utm[0]/25))
        e=float(25*round(utm[1]/25))
        alt=altitudes[n][e]
        return alt
#}}}
# vim:foldmethod=marker:foldlevel=0
