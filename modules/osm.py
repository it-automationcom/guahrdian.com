#{{{import
import math
import utm
import xml
import xml.etree.ElementTree as et
import urllib.request
import api
import wget
import configparser
import os
#}}}
#{{{read config
config=configparser.ConfigParser()
configfile=os.path.dirname(__file__)+'/../config.ini'
config.read(configfile)
#}}}
#{{{tile
class tile:
#{{{ __init__
    def __init__(self,zoom):
      self.meta={"x":None,"y":None,"zoom":zoom,"link":None}
      self.deg={"NW":{"lat":None,"lon":None},
                "NE":{"lat":None,"lon":None},
                "SE":{"lat":None,"lon":None},
                "SW":{"lat":None,"lon":None},
                "C":{"lat":None,"lon":None}
                }
      self.utm={"NW":None,
                "NE":None,
                "SE":None,
                "SW":None,
                 "C":None
                }
      self.size={"x":256,"y":256}
#}}}
#{{{from_deg
    def from_deg(self,lon,lat):
      self.meta["x"]=self.lon2x(lon,self.meta["zoom"])
      self.meta["y"]=self.lat2y(lat,self.meta["zoom"])
      self.from_tile(self.meta["x"],self.meta["y"])
#}}}
#{{{from_utm
    def from_utm(self,n,e,zone,hemi):
      deg=utm.to_latlon(n,e,zone,hemi)
      self.from_deg(deg[0],deg[1])
#}}}
#{{{from_tile
    def from_tile(self,x,y):
      self.meta["x"]=x
      self.meta["y"]=y
      self.meta["link"]="https://tile.openstreetmap.org/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      #self.meta["link"]="http://tile.stamen.com/terrain-background/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      #self.meta["link"]="http://tile.stamen.com/terrain/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      #self.meta["link"]="http://tile.stamen.com/toner/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      #self.meta["link"]="http://tile.stamen.com/toner-lines/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      #self.meta["link"]="http://tile.stamen.com/toner-hybrid/"+str(self.meta["zoom"])+"/"+str(self.meta["x"])+"/"+str(self.meta["y"])+".png"
      self.deg["NW"]["lat"]=self.y2lat(y,self.meta["zoom"])
      self.deg["NW"]["lon"]=self.x2lon(x,self.meta["zoom"])
      self.deg["NE"]["lat"]=self.y2lat(y,self.meta["zoom"])
      self.deg["NE"]["lon"]=self.x2lon(x+1,self.meta["zoom"])
      self.deg["SE"]["lat"]=self.y2lat(y-1,self.meta["zoom"])
      self.deg["SE"]["lon"]=self.x2lon(x+1,self.meta["zoom"])
      self.deg["SW"]["lat"]=self.y2lat(y-1,self.meta["zoom"])
      self.deg["SW"]["lon"]=self.x2lon(x,self.meta["zoom"])
      self.deg["C"]["lat"]=self.y2lat(y-0.5,self.meta["zoom"])
      self.deg["C"]["lon"]=self.x2lon(x+0.5,self.meta["zoom"])
      self.utm["NW"]=utm.from_latlon(self.deg["NW"]["lat"],self.deg["NW"]["lon"])
      self.utm["NE"]=utm.from_latlon(self.deg["NE"]["lat"],self.deg["NE"]["lon"])
      self.utm["SE"]=utm.from_latlon(self.deg["SE"]["lat"],self.deg["SE"]["lon"])
      self.utm["SW"]=utm.from_latlon(self.deg["SW"]["lat"],self.deg["SW"]["lon"])
      self.utm["C"]=utm.from_latlon(self.deg["C"]["lat"],self.deg["C"]["lon"])
      self.utm["C"]=utm.from_latlon(self.deg["C"]["lat"],self.deg["C"]["lon"])
#}}}
#{{{get_root_lat
    def get_root_lat(self):
      root_lat=self.deg["NW"]["lat"]
      return(root_lat)
#}}}
#{{{get_root_lon
    def get_root_lon(self):
      root_lon=self.deg["NW"]["lon"]
      return(root_lon)
#}}}
#{{{get_corner_deg
    def get_corner_deg(self,corner):
      deg=self.deg[corner]
      return(deg)
#}}}
#{{{get_corner_utm
    def get_corner_utm(self,corner):
      utm=self.utm[corner]
      return(utm)
#}}}
#{{{get_tile
    def get_tile(self,axis):
      tile=self.meta[axis]
      return(tile)
#}}}
#{{{get_zoom
    def get_zoom(self):
        return(self.meta["zoom"])
#}}}
#{{{lon2x
    def lon2x(self,lon,zoom):
      n = 2.0 ** zoom
      x=int((lon+180)/360*n)
      return(x)
#}}}
#{{{lon2xpos
    def lon2xpos(self,lon,zoom):
      n = 2.0 ** zoom
      x=(lon+180)/360*n
      return(x)
#}}}
#{{{lat2y
    def lat2y(self,lat,zoom):
      n = 2.0 ** zoom
      lat_rad = math.radians(lat)
      x = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
      return(x)
#}}}
#{{{lat2ypos
    def lat2ypos(self,lat,zoom):
      n = 2.0 ** zoom
      lat_rad = math.radians(lat)
      x = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
      return(x)
#}}}
#{{{x2lon
    def x2lon(self,x,zoom):
      n = 2.0 ** zoom
      lon = x / n * 360.0 - 180.0
      return(lon)
#}}}
#{{{y2lat
    def y2lat(self,y,zoom):
      n = 2.0 ** zoom
      lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
      lat= math.degrees(lat_rad)
      return(lat)
#}}}
#{{{print
    def print(self):
      print("<pre>")
      print("Tile")
      print("   self.meta:",self.meta)
      print("   self.deg:",self.deg)
      print("   self.utm:",self.utm)
      print("   self.size:", self.size) 
      print("</pre>")
      #}}}
#}}}
#{{{map
class map:
#{{{__init__
  def __init__(self):
    self.zoom=None
    self.size={"x":None,"y":None}
    self.offset={"NW":{"dist":{"x":1,"y":1}},"tile":None,
                "NE":{"dist":{"x":1,"y":1}},"tile":None,
                "SE":{"dist":{"x":1,"y":1}},"tile":None,
                "SW":{"dist":{"x":1,"y":1}},"tile":None,
                "C":{"dist":{"x":0,"y":0}},"tile":None}
    self.bbox_deg=[]
    self.bbox_utm=[]
#}}}
#{{{from_deg
  def from_deg(self,lat,lon,zoom):
    #c
    self.c=tile(zoom)
    self.c.from_deg(lat,lon)
    self.offset["C"]["tile"]=self.c
    self.zoom=zoom
    #nw
    self.nw=tile(zoom)
    x=self.offset["C"]["tile"].meta["x"]-self.offset["NW"]["dist"]["x"]
    y=self.offset["C"]["tile"].meta["y"]-self.offset["NW"]["dist"]["y"]
    self.nw.from_tile(x,y)
    self.offset["NW"]["tile"]=self.nw
    #ne
    self.ne=tile(zoom)
    x=self.offset["C"]["tile"].meta["x"]+self.offset["NE"]["dist"]["x"]
    y=self.offset["C"]["tile"].meta["y"]-self.offset["NE"]["dist"]["y"]
    self.ne.from_tile(x,y)
    self.offset["NE"]["tile"]=self.ne
    #se
    self.se=tile(zoom)
    x=self.offset["C"]["tile"].meta["x"]+self.offset["SE"]["dist"]["x"]
    y=self.offset["C"]["tile"].meta["y"]+self.offset["SE"]["dist"]["y"]
    self.se.from_tile(x,y)
    self.offset["SE"]["tile"]=self.se
    #sw
    self.sw=tile(zoom)
    x=self.offset["C"]["tile"].meta["x"]-self.offset["SW"]["dist"]["x"]
    y=self.offset["C"]["tile"].meta["y"]+self.offset["SW"]["dist"]["y"]
    self.sw.from_tile(x,y)
    self.offset["SW"]["tile"]=self.sw
    # create map
    self.size["x"]=(self.offset["SE"]["tile"].meta["x"]-self.offset["NW"]["tile"].meta["x"]+1)*256
    self.size["y"]=(self.offset["SE"]["tile"].meta["y"]-self.offset["NW"]["tile"].meta["y"]+1)*256
#}}}
#{{{get_root_lat
  def get_root_lat(self):
    root_lat=self.nw.get_root_lat()
    return(root_lat)
#}}}
#{{{get_root_lon
  def get_root_lon(self):
    root_lon=self.nw.get_root_lon()
    return(root_lon)
#}}}
#{{{get_root_tile
  def get_root_tile(self,axis):
    root_tile=self.nw.get_tile(axis)
    return(root_tile)
#}}}
#{{{get_bbox_deg
  def get_bbox_deg(self):
    return(self.bbox_deg)
#}}}
#{{{get_bbox_utm
  def get_bbox_utm(self):
    return(self.bbox_utm)
#}}}
#{{{get_zoom
  def get_zoom(self):
    return(self.zoom)
#}}}
#{{{display
  def display(self):
    self.tiles={}
    for i in range(self.offset["NW"]["tile"].meta["y"],self.offset["SE"]["tile"].meta["y"]+1,1):
      self.tiles[i]={}
      for j in range(self.offset["NW"]["tile"].meta["x"],self.offset["SE"]["tile"].meta["x"]+1,1):
        newtile=tile(self.offset["C"]["tile"].meta["zoom"])
        newtile.from_tile(j,i)
        if i == self.offset["NW"]["tile"].meta["y"] and j == self.offset["NW"]["tile"].meta["x"]:
                #print("Found the NW corner of the map")
                #newtile.print()
                self.bbox_deg.append(newtile.get_corner_deg("NW"))
                self.bbox_utm.append(newtile.get_corner_utm("NW"))
        if i == self.offset["SE"]["tile"].meta["y"] and j == self.offset["SE"]["tile"].meta["x"]:
                #print("Found the SE corner of the map")
                #newtile.print()
                self.bbox_deg.append(newtile.get_corner_deg("SE"))
                # FIXME: need to get all 4 corners because UTM may be slanted in regards to WGS84
                self.bbox_utm.append(newtile.get_corner_utm("SE"))
        self.tiles[i][j]=newtile
    print("<table>")
    for y,value in self.tiles.items():
      print("<tr>")
      for x in self.tiles[y]:
        print("<td>")
        print("<a href=\""+self.tiles[y][x].meta["link"]+"\">")
        print("<img src=\""+self.tiles[y][x].meta["link"]+"\"></img>")
        print("</a>")
        print("</td>")
      print("<tr>")
    print("</table>")
#}}}
#{{{set_boundaries
  def set_boundaries(self,n,e,s,w):
    self.offset["NW"]["dist"]["x"]=w
    self.offset["NW"]["dist"]["y"]=n
    self.offset["NE"]["dist"]["x"]=e
    self.offset["NE"]["dist"]["y"]=n
    self.offset["SE"]["dist"]["x"]=e
    self.offset["SE"]["dist"]["y"]=s
    self.offset["SW"]["dist"]["x"]=w
    self.offset["SW"]["dist"]["y"]=s
#}}}
#{{{print
  def print(self):
    print("<pre>")
    print("Map:")
    print("  self.zoom:",self.zoom)
    print("  self.size:",self.size)
    print("  self.offset:",self.offset)
    print("  self.tiles:",self.tiles)
    print("  self.bbox_deg:",self.bbox_deg)
    print("  self.bbox_utm:",self.bbox_utm)
    print("</pre>")
#}}}
#}}}
#{{{maplayer
class maplayer:
#{{{__init__
  def __init__(self,map):
    self.zoom=map.get_zoom()
    self.size={"x":map.size["x"],"y":map.size["y"]}
    self.root={"deg":{"lon":map.get_root_lon(),"lat":map.get_root_lat()},"utm":None,"tile":{"x":map.get_root_tile("x"),"y":map.get_root_tile("y")}}
    self.points=[]
    self.polylines=[]
    self.polygons=[]
#}}}  
#{{{get_zoom
  def get_zoom(self):
    return(self.zoom)
#}}}
#{{{get_root_tile
  def get_root_tile(self,axis):
    return(self.root["tile"][axis])
#}}}
#{{{add_point
  def add_point(self,x,y):
    self.points.append({"x":x,"y":y})
#}}}
#{{{add_polyline
  def add_polyline(self,polyline):
    self.polylines.append(polyline)
#}}}
#{{{add_polygon
  def add_polygon(self,polygon):
    self.polygons.append(polygon)
#}}}
#{{{display
  def display(self):
     print("<svg width=\""+str(self.size["x"])+"\" height=\""+str(self.size["y"])+"\" style=\"position:absolute; left:0; top:0\" z-index:100>")
     for i in self.points:
       x=i["x"]
       y=i["y"]
       #cross=str(str(x-10)+","+str(y-10)+" "+str(x+10)+","+str(y+10)+" "+str(x)+","+str(y)+" "+str(x+10)+","+str(y-10)+" "+str(x-10)+","+str(y+10))
       cross=str(str(x-5)+","+str(y-5)+" "+str(x+5)+","+str(y+5)+" "+str(x)+","+str(y)+" "+str(x+5)+","+str(y-5)+" "+str(x-5)+","+str(y+5))
       print("<polyline points=\""+cross+"\" style=\"fill:none;stroke:blue;stroke-width:1.5\"/>")
     for i in self.polylines:
       polyline=""
       for j in i:
         x=str(j["x"])
         y=str(j["y"])
         polyline=polyline+" "+x+","+y
       print("<g id=\"polyline\">")
       print("<polyline points=\""+polyline+"\" style=\"fill:none;stroke:blue;stroke-opacity:40%\"/>")
       print("</g>")
     for i in self.polygons:
       polygon=""
       for j in i:
         x=str(j["x"])
         y=str(j["y"])
         polygon=polygon+" "+x+","+y
       print("<g id=\"polyline\">")
       print("<polyline points=\""+polygon+"\" style=\"fill:blue;fill-opacity:30%;stroke:none;stroke-width:1\"/>")
       print("</g>")
     print("</svg>")
#}}}
#{{{print
  def print(self):
    print("<pre>")
    print("Maplayer:")
    print("  self.size:",self.size)
    print("  self.root:",self.root)
    print("  self.points:",len(self.points))
    print("  self.polylines:",len(self.polylines))
    print("  self.polygons:",len(self.polygons))
    print("</pre>")

#}}}
#}}}
#{{{trace
# get ways from relation
class trace:
#{{{ __init__
    def __init__(self,url,relation):
        self.url=url
        self.relation=str(relation)
        self.startway=None
        self.ordered_points=None
        request_url=self.url+"/relation/"+self.relation
        # get relation xml
        opener=urllib.request.build_opener()
        for i in range(2):
          try:
            relation_xml = et.parse(opener.open(request_url))
          except:
            fallback_url="https://www.openstreetmap.org/api/0.6/relation/"+self.relation
            output_directory="/var/www/html/osm/relation/"
            wget.download(fallback_url, out=output_directory)   
        # create a dict for the trace
        # refactor: add multiple relations 
        trace=dict()
        trace={"relations":{self.relation:None}}
        trace["relations"][self.relation]=dict()
        trace["relations"][self.relation]["ways"]=dict()
        for member in relation_xml.findall('relation/member'):
            if member.get('type') == "way" and member.get('role') != "side_stream":
                way=member.get('ref')
                trace["relations"][self.relation]["ways"][way]=dict()
                request_url=self.url+"/way/"+way
                opener=urllib.request.build_opener()
                for i in range(2):
                    try:
                      way_xml=et.parse(opener.open(request_url))
                    except:
                      fallback_url="https://www.openstreetmap.org/api/0.6/way/"+way
                      output_directory="/var/www/html/osm/way/"
                      wget.download(fallback_url, out=output_directory)   
                trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"]=dict()
                for node in way_xml.findall('way/nd'):
                    node=node.get('ref')
                    trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]=dict()
                    request_url=self.url+"/node/"+node
                    opener=urllib.request.build_opener()
                    for i in range(2):
                        try:
                            node_xml=et.parse(opener.open(request_url))
                        except:
                            fallback_url="https://www.openstreetmap.org/api/0.6/node/"+node
                            output_directory="/var/www/html/osm/node/"
                            wget.download(fallback_url, out=output_directory)   

                    trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["location"]=dict()
                    trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["location"]["lat"]=None
                    trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["location"]["lon"]=None
                    trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["tags"]=dict()
                    for node_tag in node_xml.findall('node'):
                        lat=node_tag.get('lat')
                        lon=node_tag.get('lon')
                        trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["location"]["lon"]=lon
                        trace["relations"][self.relation]["ways"][member.get('ref')]["nodes"][node]["location"]["lat"]=lat
                    for tag_tag in node_xml.findall('node/tag'):
                        key=tag_tag.get("k")
                        value=tag_tag.get("v")
                        if key=="natural" and value=="spring":
                            self.startway=way
        ways_set=set(trace["relations"][self.relation]["ways"].keys())
#        print(ways_set)
        # Fallbacks if natural:spring is not defined
        # read first way from config
        if self.startway == None:
            self.startway=config[self.relation]['startway']
        # Use the first way in the list
        if self.startway == None:
            self.startway=list(trace["relations"][self.relation]["ways"])[0]
        ordered_ways=list()
        ordered_ways.append(self.startway)
        ordered_nodes=list()
        node_list=(list(trace["relations"][self.relation]["ways"][self.startway]["nodes"].keys()))
        ordered_nodes.append(node_list)
        ordered_points=list()
        for i in node_list:
            lat=trace["relations"][self.relation]["ways"][self.startway]["nodes"][i]["location"]["lat"]
            lon=trace["relations"][self.relation]["ways"][self.startway]["nodes"][i]["location"]["lon"]
            ordered_points.append([lat,lon])
        start_node=list(trace["relations"][self.relation]["ways"][self.startway]["nodes"].keys())[0]
        end_node=list(trace["relations"][self.relation]["ways"][self.startway]["nodes"].keys())[-1]
        ways_set.remove(self.startway)
        for i in range(200):
            #find next way 
            #for j in trace["relations"][self.relation]["ways"]:
            for j in trace["relations"][self.relation]["ways"]:
                if j in ways_set:
                    start_node=list(trace["relations"][self.relation]["ways"][j]["nodes"].keys())[0]
                    node_list=list(trace["relations"][self.relation]["ways"][j]["nodes"].keys())
                    if end_node in node_list:
    #                if start_node == end_node:
                        ordered_ways.append(j)
                    #    print("append and remove",j)
                        ways_set.remove(j)

                        node_list=list(trace["relations"][self.relation]["ways"][j]["nodes"].keys())
                        ordered_nodes.append(list(trace["relations"][self.relation]["ways"][j]["nodes"].keys()))
                        ordered_nodes.append(node_list)
                        for i in node_list:
                            lat=trace["relations"][self.relation]["ways"][j]["nodes"][i]["location"]["lat"]
                            lon=trace["relations"][self.relation]["ways"][j]["nodes"][i]["location"]["lon"]
                            ordered_points.append([lat,lon])
                        end_node=list(trace["relations"][self.relation]["ways"][j]["nodes"].keys())[-1]
#        print(ordered_nodes)
       # print(ordered_ways)
        self.ordered_points=ordered_points
#}}}
#{{{get_points
    def get_points(self):
      return(self.ordered_points)
#}}}
#}}}
#{{{point
class point:
#{{{__init__
  def __init__(self,maplayer):
    self.zoom=maplayer.get_zoom()
    self.deg={"lon":None,"lat":None}
    self.utm=None
    self.maplayer=maplayer
#}}}
#{{{from_deg
  def from_deg(self,lon,lat):
    self.deg={"lon":lon,"lat":lat}
    self.x=int((tile.lon2xpos(None,self.deg["lon"],self.zoom)-self.maplayer.get_root_tile("x"))*256)
    self.y=int((tile.lat2ypos(None,self.deg["lat"],self.zoom)-self.maplayer.get_root_tile("y"))*256)
    self.maplayer.add_point(self.x,self.y)
    self.utm=utm.from_latlon(lat,lon)
#}}}
#{{{from_utm
  def from_utm(self,e,n,zone,hemi):
    deg=utm.to_latlon(n,e,zone,hemi)
    self.utm={"N":n,"E":e}
    self.from_deg(deg[1],deg[0])
#}}}
#{{{print
  def print(self):
    print("<pre>")
    print("Point")
    print("  self.deg:",self.deg)
    print("  self.utm:",self.utm)
    print("  self.x:", self.x)
    print("  self.y:",self.y)
    print("</pre>")
#}}}
#}}}
#{{{polyline
class polyline:
  def __init__(self,list,maplayer):
    self.zoom=maplayer.get_zoom()
    self.polyline=[]
    for i in list:
      lon=float(i[1])
      lat=float(i[0])
      self.x=int((tile.lon2xpos(None,lon,self.zoom)-maplayer.get_root_tile("x"))*256)
      self.y=int((tile.lat2ypos(None,lat,self.zoom)-maplayer.get_root_tile("y"))*256)
      self.polyline.append({"x":self.x,"y":self.y})
    maplayer.add_polyline(self.polyline)
  def print(self):
    print(self.zoom)
    print(self.polylines)
#}}}
#{{{polygon
class polygon:
  def __init__(self,list,maplayer):
    self.zoom=maplayer.get_zoom()
    self.polygon=[]
    for i in list:
      lon=float(i[1])
      lat=float(i[0])
      self.x=int((tile.lon2xpos(None,lon,self.zoom)-maplayer.get_root_tile("x"))*256)
      self.y=int((tile.lat2ypos(None,lat,self.zoom)-maplayer.get_root_tile("y"))*256)
      self.polygon.append({"x":self.x,"y":self.y})
    maplayer.add_polygon(self.polygon)
  def print(self):
    print(self.zoom)
    print(self.polygon)
#}}}
#{{{shadow
class shadow:
  def __init__(self,list,maplayer):
    self.zoom=maplayer.get_zoom()
    self.shadow=[]
    for i in list:
      lon=float(i[1])
      lat=float(i[0])
      self.x=int((tile.lon2xpos(None,lon,self.zoom)-maplayer.get_root_tile("x"))*256)
      self.y=int((tile.lat2ypos(None,lat,self.zoom)-maplayer.get_root_tile("y"))*256)
      self.shadow.append({"x":self.x,"y":self.y})
    maplayer.add_shadow(self.shadow)
  def print(self):
    print(self.zoom)
    print(self.polylines)
#}}}
# vim:foldmethod=marker:foldlevel=0
