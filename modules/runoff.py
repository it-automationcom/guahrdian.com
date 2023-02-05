#{{{import
import numpy as np
import pandas as pd
import math
import gc
import time
from scipy.interpolate import griddata
#}}}
#{{{class flow_paths
class flow_paths:
#{{{__init__
  def __init__(self,mesh,steps):
    self.mesh=mesh
    self.steps=steps
    self.name=None
    self.dataframe=None
    self.df_fixed=None
    self.trace=None
    self.weights=None
    self.steps=None
    self.gradient=None
    self.dips=None
    self.traces=dict()
    self.meta=dict()
    self.debug=False
    self.width=None
    self.height=None    
#}}}
#{{{ inject_dataframe
  def inject_dataframe(self,dataframe):
      self.dataframe=dataframe
#}}}
#{{{ fix_dips   
  def fix_dips(self):
      self.df_fixed=self.dataframe.copy()   
#{{{ calculate size of dataframe
      cols=self.df_fixed.columns.values.tolist()
      idx=self.df_fixed.index.values.tolist()
      length_cols=len(cols)
      length_idx=len(idx)
#}}}
#{{{loop)
      while True:   
          dips=0
          for i in range(1,length_cols-1): 
              for j in range(1,length_idx-1):   
                  df_slice=self.df_fixed.iloc[j-1:j+2,i-1:i+2]
                  root_alt=self.df_fixed.iloc[j,i]
                  min_alt=df_slice.min().min()
                  if root_alt == min_alt:
                      self.df_fixed.iloc[j,i]=math.nan
                      dips+=1
          # Fix: change to 2d interpolation using scipy.griddata
          print(dips)
          self.df_fixed.interpolate()
          if dips==0:
              break
#}}}
#}}}
#{{{ simulate
  def simulate(self):
#{{{ calculate size of dataframe
      cols=self.dataframe.columns.values.tolist()
      idx=self.dataframe.index.values.tolist()
      length_cols=len(cols)
      length_idx=len(idx)
#}}}
      #{{{ create a work copy of the dataframe
      # create a trace_dataframe (we work with a copy because we change data during the trace simulation)
      #}}}
      trace_dataframe=self.dataframe.copy()
      #trace_dataframe=self.df_fixed.copy()
#{{{ debug
      if self.debug:
        print("run simulation")
#}}}
#{{{ self.trace: "empty dataframe for trace"
      self.trace=pd.DataFrame().reindex_like(trace_dataframe)
#}}}
#{{{ self.weight: "empty dataframe for weights (size of flow)"
      self.weights=pd.DataFrame().reindex_like(trace_dataframe)
#}}}
#{{{ self.dips: "empty dataframe for dips"
      self.dips=pd.DataFrame().reindex_like(trace_dataframe)
#}}}
#{{{ self.steps: "empty dataframe for steps (length of flow)"
      self.steps=pd.DataFrame().reindex_like(trace_dataframe)
#}}}
#{{{ self.gradient: "empty dataframe for gradient"
      self.gradient=pd.DataFrame().reindex_like(trace_dataframe)
#}}}
#{{{ calculate size of dataframe
      cols=trace_dataframe.columns.values.tolist()
      idx=trace_dataframe.index.values.tolist()
      length_cols=len(cols)
      length_idx=len(idx)
#}}}
#{{{ count variables for features and weights
      # distinct naming of trace
      stream_feature=0
      stream_weight=0
#}}}
#{{{loop through start points ("spring") of traces (i: cols, j: index)
      for i in cols[1:length_cols-1:10]:
          for j in idx[1:length_idx-1:10]:
      #for i in cols[0:800:40]:
      #    for j in idx[0:700:40]:
#}}}
#{{{ set start vertex and write it to traces
            idx_loc=trace_dataframe.index.get_loc(j)
            col_loc=trace_dataframe.columns.get_loc(i)
            current_z=trace_dataframe.iloc[idx_loc,col_loc]
            if math.isnan(current_z):
                continue
            current_vertex=(i,j,current_z)
            self.traces[stream_feature]=list()
            self.traces[stream_feature].append(current_vertex)
            self.meta[stream_feature]=dict()
            surrounding=1
#}}}
             #{{{ loop through vertices
             # while True:
            trace_idx=j
            trace_col=i
            trace_dataframe=self.dataframe.copy()
            for m in range(2000):
             #}}}
                  #{{{ get index location
                  if math.isnan(trace_idx):
                      print("Error: trace_idx is NaN")
                      continue
                  idx_loc=trace_dataframe.index.get_loc(trace_idx)
                  col_loc=trace_dataframe.columns.get_loc(trace_col)
                  #}}}
                  #{{{ get z value from dataframe
                  current_z=trace_dataframe.iloc[idx_loc,col_loc]
                  #}}}
                  #{{{ set current vertex to nan, we do not want to visit it again)
                  trace_dataframe.iloc[idx_loc,col_loc]=np.nan
                  #}}} 
                  # {{{ write stream feature to trace dataframe
                  if not math.isnan(self.trace.iloc[idx_loc,col_loc]):
                      break
                  else:
                      self.trace.iloc[idx_loc,col_loc]=stream_feature
                  # }}}
                  # {{{ write weight to weight dataframe
                  self.weights.iloc[idx_loc,col_loc]=stream_weight
                  #}}}
#{{{detect edges of dataframe
                  edge=False
                  if idx_loc==0:
                      idx_loc=1
                      edge=True
                      print("reached edge of dataframe")
                  if col_loc==0:
                      col_loc=1
                      edge=True
                      print("reached edge of dataframe")
#}}}
#{{{get slice and find next vertex
                  #df_slice=trace_dataframe.iloc[idx_loc-1:idx_loc+2,col_loc-1:col_loc+2]
                  df_slice=trace_dataframe.iloc[idx_loc-surrounding:idx_loc+surrounding+1,col_loc-surrounding:col_loc+surrounding+1]
                  next_z=df_slice.min().min()
                  try:
                      next_x=df_slice.min().idxmin()
                      next_y=df_slice.min(axis=1).idxmin()
                      next_vertex=(next_x,next_y,next_z)
                  except:
                      print(Exception)
                      print(df_slice)
                      print("idx_loc",idx_loc)
                      print("col_loc",col_loc)
                      print(idx_loc,col_loc)
#}}}
#{{{check for dips
                  if current_z < next_z:
                     self.dips.iloc[idx_loc,col_loc]=True
                     print(surrounding)
                     # FIX
                     if surrounding > 6:
                        break
                    
                     surrounding+=1
                  else:
                     self.dips.iloc[idx_loc,col_loc]=False
#}}}
#{{{ save findings
                  self.traces[stream_feature].append(next_vertex)
#}}}
#{{{go to next vertex
                  current_vertex=next_vertex
                  trace_idx=next_y
                  trace_col=next_x
                  #current_z=next_z
                  if self.debug:
                      print("Slice")
                      print(df_slice)
                      print("next_z:", next_z)
                      print("next_y:", next_y)
                      print("next_x:", next_x)
                  # increment weight by 1
                  stream_weight+=1
                  if edge:
                      stream_feature+=1
                      stream_weight=0
                      # reset trace dataframe for new run 
                      trace_dataframe=self.dataframe.copy()
                      break
            stream_feature+=1
            stream_weight=0
#}}}
#}}}
#{{{get_traces
  def get_traces(self):
      return(self.traces)
#}}}
#{{{ print
  def print(self):
      print("self.mesh:", self.mesh)
      print("self.steps:", self.steps)
      print("self.name:", self.name)
      print("self.dataframe:\n", self.dataframe)
      print("self.trace:\n", self.trace)
      print("self.dips:\n", self.dips)
      print("self.weights:\n", self.weights)
#      print("self.traces:\n", self.traces)
      print("self.debug:", self.debug)
      print("self.width:", self.width)
      print("self.height:", self.height)
#}}}
#}}} 
#}}}  
# vim:foldmethod=marker:foldlevel=0
