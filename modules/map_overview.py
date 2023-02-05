#{{{imports
import folium as fo
#}}}
#{{{ class map
class map:
    #{{{ __init___
    def __init__(self):
        self.location=None
        self.zoom_min=0
        self.zoom_max=20
        self.min_lon=None
        self.max_lon=None
        self.min_lat=None
        self.max_lat=None
        self.dragging=False
        self.max_bounds=False
        self.tiles="Stamen terrain"
        self.markers=list()
    #}}}
    #{{{ set_location
    def set_location(self,location):
        self.location=location
    #}}}
    #{{{ set_zoom
    def set_zoom(self,min,max):
        self.zoom_min=min
        self.zoom_max=max
    #}}}
    #{{{ add_marker
    def add_marker(self,marker):
        self.markers.append(marker)
    #}}}
    #{{{ generate
    def generate(self,file):
        map1=fo.Map(location=self.location,tiles=self.tiles, min_zoom=self.zoom_min, max_zoom=self.zoom_max )
        for i in self.markers:
            fo.Marker(i).add_to(map1)
        map1.save(file)
    #}}}
    #{{{ print
    def print(self):
        print("self.location:",self.location)
        print("self.zoom_min:",self.zoom_min)
        print("self.zoom_max:",self.zoom_max)
        print("self.min_lon:",self.min_lon)
        print("self.max_lon:",self.max_lon)
        print("self.min_lat:",self.min_lat)
        print("self.max_lat:",self.max_lat)
        print("self.max_bounds:",self.max_bounds)
        print("self.dragging:",self.dragging)
        print("self.tiles:",self.tiles)
    #}}}
#}}}
