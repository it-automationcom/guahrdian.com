import wget
from os.path import exists
class cache:
  def __init__(self,url,localpath,remote):
    self.url=url
    self.localpath=localpath
    self.remote=remote
  def get(self,path):
    local_path=(self.localpath+"/"+path)
    file_exists=exists(local_path)
    if not file_exists:
      print("file does not exist")
      remotefile=(self.remote+"/"+path)
      print(remotefile)
      wget.download(remotefile, local_path)
