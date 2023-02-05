#{{{import
import osm
import dgm
from geopy.geocoders import Nominatim
import geopy.distance
import urllib.request
import xml
import xml.etree.ElementTree as et
import wget
import ujson as json
import os
import sys
import time
import random
#}}}
#{{{class building
class building:
    #{{{__init__
    def __init__(self):
        self.id=None
        self.location=None
        self.altitude=None
        self.city=None
        self.street=None
        self.housenumber=None
        self.postcode=None
        self.mesh=None
        self.meshsize=25
        self.points=list()
        self.river=None 
        self.distance_from_river=None
        self.river_closest_node=None
        self.river_zero_level=None
        self.danger_level1=None
        self.danger_level2=None
        self.danger_level3=None
        self.danger_level4=None
        self.danger_level5=None 
        self.flood_level=None
        self.water_level=None
        self.debug=False
    #}}}
    #{{{from_nominatim
    def from_nominatim(self,building):
        nominatim = Nominatim(user_agent="tutorial")
        try:
            location=nominatim.geocode(building).raw
        except NoneType:
            print("Can not find building")
            sys.exc_clear()
            pass
        lat=location["lat"]
        lon=location["lon"]
        self.mesh=dgm.grid(self.meshsize)   
        self.mesh.load_from_bbox_deg(location["boundingbox"])
        self.altitude=self.mesh.alt_from_deg([lat,lon])
        self.location=location
        self.osm_type=location["osm_type"]
        self.osm_id=location["osm_id"]
        self.display_name=location["display_name"]
        self.object_class=location["class"]
        self.type=location["type"]
        if self.object_class=="building" and self.type=="yes":
            opener=urllib.request.build_opener()
            request_url="http://localhost:8000/osm/way/"+str(self.osm_id)
            for i in range(2):
              try:
                way_xml = et.parse(opener.open(request_url))
              except:
                fallback_url="https://www.openstreetmap.org/api/0.6/way/"+str(self.osm_id)
                output_directory="/var/www/html/osm/way/"
                wget.download(fallback_url, out=output_directory)
            for node in way_xml.findall('way/nd'):
              node=node.get('ref')
              request_url="http://localhost:8000/osm/node/"+node
              for j in range(2):
                try:
                  node_xml=et.parse(opener.open(request_url))
                except:
                  fallback_url="https://www.openstreetmap.org/api/0.6/node/"+str(node)
                  output_directory="/var/www/html/osm/node/"
                  wget.download(fallback_url, out=output_directory)
              for node_tag in node_xml.findall('node'):
                  lat=node_tag.get('lat')
                  lon=node_tag.get('lon')
                  self.points.append((lat,lon))
        else:
            print("this is not a building")
        self.from_way_id(location["osm_id"])
      #}}}
    #{{{from_way_id
    def from_way_id(self,way_id):
        self.id=way_id
        file1="/var/www/html/cache/building/ways/"+str(way_id)
        if os.path.isfile(file1):
                ts=time.time()
                with open(file1,'r') as f:
                    data = json.load(f)
                ts=time.time()
                ts=time.time()
                self.id=data["building_id"]
                self.location=data["location"]
                self.altitude=data["altitude"]
                self.city=data["city"]
                self.street=data["street"]
                self.housenumber=data["housenumber"]
                self.postcode=data["postcode"]
                self.distance_from_river=data["distance_from_river"]
                self.danger_level1=data["danger_level1"]
                self.danger_level2=data["danger_level2"]
                self.danger_level3=data["danger_level3"]
                self.danger_level4=data["danger_level4"]
                self.danger_level5=data["danger_level5"]
                self.river_zero_level=data["river_zero_level"]
                self.river_closest_node=data["river_closest_node"]
                self.points=data["points"]
        else:
            opener=urllib.request.build_opener()
            request_url="http://localhost:8000/osm/way/"+str(way_id)
            for i in range(2):
              try:
                way_xml = et.parse(opener.open(request_url))
              except:
                fallback_url="https://www.openstreetmap.org/api/0.6/way/"+str(way_id)
                output_directory="/var/www/html/osm/way/"
                wget.download(fallback_url, out=output_directory)
            for node in way_xml.findall('way/nd'):
              node=node.get('ref')
              request_url="http://localhost:8000/osm/node/"+node
              for j in range(2):
                try:
                  node_xml=et.parse(opener.open(request_url))
                except:
                  fallback_url="https://www.openstreetmap.org/api/0.6/node/"+str(node)
                  output_directory="/var/www/html/osm/node/"
                  wget.download(fallback_url, out=output_directory)
              for node_tag in node_xml.findall('node'):
                  lat=node_tag.get('lat')
                  lon=node_tag.get('lon')
                  self.points.append((lat,lon))
            for m in way_xml.findall('way/tag'):
                k=m.get('k')
                v=m.get('v')
                if k=="addr:city":
                    self.city=v
                if k=="addr:street":
                    self.street=v
                if k=="addr:postcode":
                    self.postcode=v
                if k=="addr:housenumber":
                    self.housenumber=v
            #{{{ boundingbox
            min_lat=min(self.points,key=lambda item:item[0])[0]
            max_lat=max(self.points,key=lambda item:item[0])[0]
            min_lon=min(self.points,key=lambda item:item[1])[1]
            max_lon=max(self.points,key=lambda item:item[1])[1]
            bbox=[min_lat,max_lat,min_lon,max_lon]
            #}}}
            self.mesh=dgm.grid(self.meshsize)   
            self.mesh.load_from_bbox_deg(bbox)
            self.location=[min_lat,min_lon]
            self.altitude=self.mesh.alt_from_deg([max_lat,max_lon])
            # calculate closest distance to river
            spring=self.river.get_points()[0]
            self.distance_from_river=geopy.distance.geodesic(self.location,spring).km
            for i in self.river.get_points():
                distance=(geopy.distance.geodesic(self.location,i).km)
                if distance <= self.distance_from_river:
                    self.distance_from_river=distance
                    self.river_closest_node=i
            lat=self.river_closest_node[0]
            lon=self.river_closest_node[1]
            self.river_zero_level=dgm.altitude.from_deg(lat,lon)
            self.danger_level1=self.altitude-self.river_zero_level-2.5
            self.danger_level2=self.altitude-self.river_zero_level
            self.danger_level3=self.altitude-self.river_zero_level+2.5
            self.danger_level4=self.altitude-self.river_zero_level+5
            self.danger_level5=self.altitude-self.river_zero_level+7.5
            try:
                self.water_level=self.flood_level-self.danger_level2
            except:
                self.water_level=None
            orig_stdout=sys.stdout
            f=open("/var/www/html/cache/building/ways/"+str(way_id),'w')
            sys.stdout=f
            self.to_json()
            sys.stdout=orig_stdout
            f.close
    #}}}
    #{{{add_river
    def add_river(self,river):
       self.river=(river)
    #}}}
    #{{{add_flood_level
    def add_flood_level(self,flood_level):
        self.flood_level=-flood_level
    #}}}
    #{{{get_altitude
    def get_altitude(self): 
        return self.altitude
    #}}}
    #{{{get_id
    def get_id(self): 
        return self.id
    #}}}
    #{{{get_points
    def get_points(self): 
        return self.points
    #}}}
    #{{{get_location
    def get_location(self):
        return self.location
    #}}}
    #{{{get_danger_level1
    def get_danger_level1(self):
        return self.danger_level1
    #}}}
    #{{{get_danger_level2
    def get_danger_level2(self):
        return self.danger_level2
    #}}}
    #{{{get_danger_level3
    def get_danger_level3(self):
        return self.danger_level3
    #}}}
    #{{{get_danger_level4
    def get_danger_level4(self):
        return self.danger_level4
    #}}}
    #{{{create_page
    def create_page(self,directory):
        orig_stdout=sys.stdout
        f=open(directory+self.id,'w')
        sys.stdout=f
        print("<pre>")
        print("Building Id:",self.id)
        print("River closest Node:", self.river_closest_node)
        print("River zero Level:", self.river_zero_level)
        print("Distance from River:", self.distance_from_river)
        print("Location:",self.location)
        print("Altitude:",self.altitude)
        print("Street:",self.street)
        print("Housenumber:",self.housenumber)
        print("Postcode:",self.postcode)
        print("City:",self.city)
        print("Points:",self.points)
        print("Danger Level 1:",self.danger_level1)
        print("Danger Level 2:",self.danger_level2)
        print("Danger Level 3:",self.danger_level3)
        print("Danger Level 4:",self.danger_level4)
        print("</pre>")
        sys.stdout=orig_stdout
        f.close
    #}}}
    #{{{print
    def print(self):
        print("Building Id:",self.id)
        print("River closest Node:", self.river_closest_node)
        print("River zero Level:", self.river_zero_level)
        print("Distance from River:", self.distance_from_river)
        print("Location:",self.location)
        print("Altitude:",self.altitude)
        print("Street:",self.street)
        print("Housenumber:",self.housenumber)
        print("Postcode:",self.postcode)
        print("City:",self.city)
        print("Points:",self.points)
        print("Danger Level 1:",self.danger_level1)
        print("Danger Level 2:",self.danger_level2)
        print("Danger Level 3:",self.danger_level3)
        print("Danger Level 4:",self.danger_level4)
        print("Danger Level 5:",self.danger_level5)
    #}}}
    #{{{to_json
    def to_json(self):
        print ("{\"building_id\": \""+str(self.id)+"\",\
 \"points\":",json.dumps(self.points),",\
 \"river_closest_node\":",json.dumps(self.river_closest_node),",\
 \"river_zero_level\":",self.river_zero_level,",\
 \"distance_from_river\":",self.distance_from_river,",\
 \"location\":",json.dumps(self.location),",\
 \"altitude\":",self.altitude,",\
 \"street\":\""+str(self.street)+"\",\
 \"housenumber\":\""+str(self.housenumber)+"\",\
 \"postcode\":\""+str(self.postcode)+"\",\
 \"city\":\""+str(self.city)+"\",\
 \"danger_level1\":",self.danger_level1,",\
 \"danger_level2\":",self.danger_level2,",\
 \"danger_level3\":",self.danger_level3,",\
 \"danger_level4\":",self.danger_level4,",\
 \"danger_level5\":",self.danger_level5,\
 "}")
    #}}}
#}}}
#{{{class objects_list
class objects_list:
    #{{{__init__
    def __init__(self):
        self.objects=list()
        self.tagfilter=None
        self.pbf="/var/www/html/pbf/tmp.pbf"
        self.type=None
        self.debug=False
    #}}} 
    #{{{ set_filter
    def set_tagfilter(self,tagfilter):
        self.tagfilter=tagfilter
    #}}}
    #{{{ set_type
    def set_type(self,filter_type):
        if filter_type=="relation":
            self.type="r"
        elif filter_type=="way":
            self.type="w"
        elif filter_type=="node":
            self.type="n"
        elif filter_type=="area":
            self.type="a"
        else:
            print("Error: Type", filter_type,"does not exist")
    #}}}
    #{{{ get_objects
    def get_objects(self):
        #{{{ get xml from pbf file
        run_command="osmium tags-filter "+self.pbf+" "+self.type+"/"+self.tagfilter+" -f osm"
        objects_raw=os.popen(run_command).read()
        objects_xml=et.fromstring(objects_raw)
        #}}}
        #{{{ type relation
        if self.type=="r":
            for relation in objects_xml.findall('relation'):
                object_id=relation.get('id')
                self.objects.append(object_id)
        #{}}}
        #{{{ type area
        if self.type=="a":
            for relation in objects_xml.findall('relation'):
                object_id=relation.get('id')
                self.objects.append(object_id)
        #{}}}
        #{{{ type way
        if self.type=="w":
            for way in objects_xml.findall('way'):
                object_id=way.get('id')
                self.objects.append(object_id)
        #}}}
        #{{{type node
        if self.type=="n":
            for way in objects_xml.findall('node'):
                object_id=way.get('id')
                self.objects.append(object_id)
        #}}}
        return self.objects
   #}}}
    #{{{ tag_filter
    def tag_filter(self, key_filter, value_filter):
        #{{{ initialize variables
        objects=self.objects
        self.objects=list()
        #}}}
        #{{{ get xml from pbf file
        for object_id in objects:
            if self.type == "a":
                self.type="r"
            run_command="osmium getid -f osm "+self.pbf+" "+self.type+object_id
            object_raw=os.popen(run_command).read()
            object_xml=et.fromstring(object_raw)
        #}}}
            #{{{ type relation
            if self.type=="r":
                for relation in object_xml.findall('relation'):
                    for tag in object_xml.findall('relation/tag'):
                        key=tag.get('k')
                        value=tag.get('v')
                        if str(key)==str(key_filter) and str(value)==str(value_filter):
                            self.objects.append(object_id)
            #}}} 
            #{{{ type way
            if self.type=="w":
                for way in object_xml.findall('way'):
                    object_id=way.get('id')
                    for tag in object_xml.findall('way/tag'):
                        key=tag.get('k')
                        value=tag.get('v')
                        if str(key)==str(key_filter) and str(value)==str(value_filter):
                            self.objects.append(object_id)
            #}}}
            #{{{ type node
            if self.type=="n":
                for node in object_xml.findall('node'):
                    object_id=node.get('id')
                    for tag in object_xml.findall('node/tag'):
                        key=tag.get('k')
                        value=tag.get('v')
                        if str(key)==str(key_filter) and str(value)==str(value_filter):
                            self.objects.append(object_id)
            #}}}
        return self.objects
   #}}}
#}}}
#{{{ class relation
class relation:
    #{{{ __init__
    def __init__(self,object_id):
        self.members=list()
        self.tags=dict()
        self.id=object_id
        self.type="relation"
        self.type_filter=None
        self.role_filter=None
        self.pbf="/var/www/html/pbf/tmp.pbf"
        self.type="r"
        self.debug=True
#}}}
    #{{{ get_members
    def get_members(self):
        #{{{ get xml from pbf file
        run_command="osmium getid -f osm "+self.pbf+" "+self.type+str(self.id)
        object_raw=os.popen(run_command).read()
        object_xml=et.fromstring(object_raw)
        for member in object_xml.findall('relation/member'):
            member_type=member.get('type')
            member_ref=member.get('ref')
            member_role=member.get('role')
            self.members.append(member_ref) 
        #}}}
        return self.members
    #}}}
#}}}
#{{{ class way
class way:
    #{{{ __init__
    def __init__(self,object_id):
        self.nodes=list()
        self.tags=dict()
        self.id=object_id
        self.pbf="/var/www/html/pbf/tmp.pbf"
        self.type="w"
        self.reversed=False
        self.debug=True
#}}}
    #{{{ set_reversed
    def set_reversed(self,order):
        if order:
            self.reversed=True
            self.get_nodes()
        if not order:
            self.revered=False
    #}}}
    #{{{ get_reversed_status
    def get_reversed_status(self):
        return self.reversed
    #}}}
    #{{{ get_nodes
    def get_nodes(self):
        #{{{ get xml from pbf file
        run_command="osmium getid -f osm "+self.pbf+" "+self.type+str(self.id)
        object_raw=os.popen(run_command).read()
        object_xml=et.fromstring(object_raw)
        #}}}
        #{{{ get nodes
        self.nodes=list()
        for node in object_xml.findall('way/nd'):
            node_type=node.get('type')
            node_ref=node.get('ref')
            node_role=node.get('role')
            self.nodes.append(node_ref) 
            # reverse if self.reversed:
        #}}}
        if self.reversed:
            self.nodes.reverse()
        return self.nodes
    #}}}
    #{{{ get_first
    def get_first(self):
        if not self.nodes:
            self.get_nodes()
        length=len(self.nodes)
        try:
            return self.nodes[0]
        except:
            print("Exception: Node list is empty")
            return None
    #}}}
    #{{{ get_last
    def get_last(self):
        if not self.nodes:
            self.get_nodes()
        length=len(self.nodes)
        try:
            return self.nodes[length-1]
        except:
            print("Exception: Can not find last node in list")
            return None
    #}}}
#}}}
#{{{ class node
class node:
    #{{{ __init__
    def __init__(self,object_id):
        self.lat=None
        self.lon=None
        self.tags=dict()
        self.id=object_id
        self.pbf="/var/www/html/pbf/tmp.pbf"
        self.type="n"
        self.debug=True
    #}}}
    #{{{ get_location
    def get_location(self):
        #{{{ get xml from pbf file
        run_command="osmium getid -f osm "+self.pbf+" "+self.type+str(self.id)
        object_raw=os.popen(run_command).read()
        object_xml=et.fromstring(object_raw)
        #}}}
        #{{{ get location
        for location in object_xml.findall('node'):
            self.lat=float(location.get('lat'))
            self.lon=float(location.get('lon'))
        #}}}
        return (self.lat, self.lon)
    #}}}
#}}}
#{{{ class sorted_ways
class sorted_ways:
    #{{{ __init__
    def __init__(self):
        self.ways_unsorted=list()
        self.ways_sorted=list()
        self.ways_reversed=list()
        self.debug=True
    #}}}
    #{{{ way_add
    def way_add(self,way_id):
        self.ways_unsorted.append(way_id)
    #}}}
    #{{{ sort
    def sort(self):
        # start with random element from way_set
        random_index=random.choice(range(len(self.ways_unsorted)))
        way1=way(self.ways_unsorted[random_index])
        way1_start_node=way1.get_first()
        way1_end_node=way1.get_last()
        self.ways_sorted.append(self.ways_unsorted[random_index])
        debug=list()
        debug.append((way1_start_node, way1_end_node))
        self.ways_reversed.append(False)
        del self.ways_unsorted[random_index] 
        iteration=0
        for j in range(len(self.ways_unsorted)-1):
        #for j in range(7):
            if self.debug:
                print("Iteration:", iteration)
                print("############")
            for i in self.ways_unsorted:
                if self.debug:
                    print("ways unsorted", self.ways_unsorted)
                    print("ways sorted", self.ways_sorted)
                    print("ways reversed", self.ways_reversed)
                    print("debug",debug)
                    print(" ")
                #{{{ get first node of list
                list_first_way=way(self.ways_sorted[0])
                if self.ways_reversed[0]:
                    if self.debug:
                        print("set",i,"reversed")
                    list_first_way.set_reversed(True)
                list_start_node=list_first_way.get_first()
                #}}}
                #{{{ get last node of list
                length=len(self.ways_sorted)
                list_last_way=way(self.ways_sorted[length-1])
                if self.ways_reversed[length-1]:
                    list_first_way.set_reversed(True)
                list_end_node=way1.get_last()
                #}}}
                #{{{ get boundaries of next way
                way2=way(i)
                way2_start_node=way2.get_first()
                way2_end_node=way2.get_last()
                if self.debug:
                    print("way id:", i)
                    print("way2_start:", way2_start_node)
                    print("way2_end:", way2_end_node)
                    print("list_start", list_start_node)
                    print("list_end", list_end_node)
                #}}}
                #{{{append
                if way2_start_node == list_end_node:
                    if self.debug:
                        print("append", i)
                    self.ways_sorted.append(i)
                    debug.append((way2_start_node,way2_end_node))
                    self.ways_reversed.append(False)
                    self.ways_unsorted.remove(i)
                    break
                #}}}
                #{{{ prepend
                elif way2_end_node == list_start_node:
                    if self.debug:
                        print("prepend", i)
                    self.ways_sorted.insert(0,i)
                    debug.insert(0,(way2_start_node,way2_end_node))
                    self.ways_reversed.insert(0,False)
                    self.ways_unsorted.remove(i)
                    break
                #}}}
                #{{{ reverse and append
                elif way2_end_node == list_end_node:
                    if self.debug:
                        print("reverse and append",i)
                    way2.set_reversed(True)
                    self.ways_sorted.append(i)
                    debug.append((way2_end_node,way2_start_node))
                    self.ways_reversed.append(True)
                    self.ways_unsorted.remove(i)
                    break
                #}}}
                #{{{ reverse and prepend
                elif way2_start_node == list_start_node:
                    if self.debug:
                        print("reverse and append",i)
                    way2.set_reversed(True)
                    self.ways_sorted.insert(0,i)
                    debug.insert(0,(way2_end_node,way2_start_node))
                    self.ways_reversed.insert(0,True)
                    self.ways_unsorted.remove(i)
                    break
                else:
                    print("does not match",i)
                #{}}}
                if len(self.ways_unsorted)==0:
                        break
            iteration+=1
        return self.ways_sorted,self.ways_reversed
    #}}}
    #{{{ get_polygon
    def get_polygon(self):
        # BUGFIX: start node and end node have to be the same
        length=len(self.ways_sorted)
        if length==0:
            print("use sort first")
        nodes=list()
        for i in range(length-1):
            way1=way(self.ways_sorted[i])
            if self.ways_reversed[i]: 
                way1.set_reversed(True)
            elif not self.ways_reversed[i]:
                way1.set_reversed(False)
            nodes.append(way1.get_nodes())
        flat_list = [num for sublist in nodes for num in sublist]
        locations=list()
        for j in flat_list:
            node1=node(j)
            location=node1.get_location()
            locations.append(location)
        if self.debug:
            print(nodes[0])
            print(self.ways_reversed[0])
            print("number of points", len(locations))
        return(locations)

    #}}}
    #{{{ get_line 
    def get_line(self):
        # similar to get_polygon except that start and end node do not neccessarily have to be identical (no closed loop)
        
        return self.ways_sorted,self.ways_reversed
    #}}}
#}}}
# vim:foldmethod=marker:foldlevel=0
