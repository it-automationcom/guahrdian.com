#!/usr/bin/python3
import api

cache=api.cache("192.168.2.4:8000","/var/www/html/osm","https://www.openstreetmap.org/api/0.6")
cache.get("relation/318372")
