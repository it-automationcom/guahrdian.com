#!/usr/bin/python3
#{{{imports
from geopy.geocoders import Nominatim
#}}}

class geolocation():
#{{{ __init__
  def __init__(self,searchstring):
    self.searchstring=searchstring
    lookup = Nominatim(user_agent="tutorial")
    try:
        location=lookup.geocode(searchstring).raw
    except NoneType:
        print("Can not get information from Nominatim")
        sys.exc_clear()
        pass
    print(location)
  del lookup    
#}}}

