#{{{import
import osmium
import sys
import numpy as np
#}}}
#{{{trace
class trace:
    def __init__(self,relation):
        #{{{extract ways from relations
        self.relations = RelationFilter(relation)
        self.relations.apply_file("ahr.pbf")
        #}}}
        #{{{extract nodes from ways
        self.ways = WayFilter(self.relations.ways)
        self.ways.apply_file("ahr.pbf")
        #}}}
        #{{{extract points from nodes
        self.nodes = NodeFilter(self.ways.nodes)
        self.nodes.apply_file("ahr.pbf")
        #}}}
    #{{{get_points
    def get_points(self): 
        return(self.nodes.points)
    #}}}
    #{{{get_ways
    def get_ways(self):
        return(self.relations.ways)
    #}}}
    #{{{get_nodes
    def get_nodes(self):
        return(self.ways.nodes)
    #}}}
#}}}
#{{{RelationFilter
class RelationFilter(osmium.SimpleHandler):
    def __init__(self,relationid):
        super(RelationFilter,self).__init__()
        self.ways=list()
        self.relationid=relationid
    def relation(self, relation):
        if relation.tags.get('type') == 'waterway' and relation.id == self.relationid:
            for way in relation.members:
                self.ways.append(way.ref)
#}}}
#{{{WayFilter
class WayFilter(osmium.SimpleHandler):
    def __init__(self, ways):
        super(WayFilter,self).__init__()
        self.ways = ways
        self.nodes=list()
    def way(self, way):
        if way.id in self.ways:
            for node in way.nodes:
                self.nodes.append(node.ref)
#}}}
#{{{NodeFilter
class NodeFilter(osmium.SimpleHandler):
    def __init__(self, nodes):
        super(NodeFilter,self).__init__()
        self.nodes=nodes
        self.points=[]
    def node(self,node):
        if node.id in self.nodes:
            location=str(node.location)
            lon=location.split("/")[0]
            lat=location.split("/")[1]
            self.points.append([lat,lon])
#}}}
# vim:foldmethod=marker:foldlevel=0
