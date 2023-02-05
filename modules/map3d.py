#{{{import
import requests
import tempfile
import os
import shutil
from pathlib import Path
#}}}
#{{{class map3d
class map3d:
#{{{__init__
  def __init__(self,map):
    self.name=None
    self.map=map
    self.tiles=self.map.get_tiles()
    self.zoom=self.map.get_zoom()
    self.debug=True
    dirpath=tempfile.mkdtemp()
    vcount=0
    vfiles=[]
    for i in (self.tiles):
        vtempfile=tempfile.mkstemp()
        hcount=0
        hfiles=[]
        for j in (self.tiles[i]):
            url="http://localhost:8000/tiles/"+str(self.zoom)+"/"+str(j)+"/"+str(i)+".png"
            for z in range(2):
                try:
                    outputfile=dirpath+"/"+str(hcount)
                    headers={'user-agent': 'Mozilla/5.0 (X11; Linux i686; rv:105.0) Gecko/20100101 Firefox/105.0'}
                    r=requests.get(url, headers=headers)
                    if r.status_code == 404:
                        raise ValueError("Not found locally")
                        
                    with open(outputfile, 'wb') as f:
                        f.write(r.content)
                    f.close
                except:

                    Path("/var/www/html/tiles/"+str(self.zoom)+"/"+str(j)).mkdir(parents=True, exist_ok=True)
                    cachefile="/var/www/html/tiles/"+str(self.zoom)+"/"+str(j)+"/"+str(i)+".png"
                    headers={'user-agent': 'Mozilla/5.0 (X11; Linux i686; rv:105.0) Gecko/20100101 Firefox/105.0'}
                    url="https://tile.openstreetmap.org/"+str(self.zoom)+"/"+str(j)+"/"+str(i)+".png"
                    r=requests.get(url, headers=headers)
                    with open(cachefile, 'wb') as f:
                        f.write(r.content)
                f.close
            hfiles.append(outputfile)
            hcount=hcount+1
        string=" ".join(hfiles)
        os.system("convert "+string+" +append "+vtempfile[1])
        vfiles.append(vtempfile[1])
    string=" ".join(vfiles)
    os.system("convert "+string+" -append /var/www/html/cache/map.png")
#}}}
# vim:foldmethod=marker:foldlevel=0
