#!/usr/bin/python3

import xml
import xml.etree.ElementTree as et
import urllib.request

# Ahr: way 122654675

url='http://localhost:8000/osm/way/122654675'
opener = urllib.request.build_opener()
way = et.parse(opener.open(url))
nodes=[]
for node in way.findall('way/nd'):
  for ref in node.iter():
    node=ref.get('ref')
    nodeurl="http://localhost:8000/osm/node/"+node
    opener = urllib.request.build_opener()
    node = et.parse(opener.open(nodeurl))
    for node in node.findall('node'):
      nodes.append([node.get('lat'),node.get('lon')])
print(nodes)

