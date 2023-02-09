# {{{import
import pandas as pd
import numpy as np
# }}}
# {{{ class radar
class radar:
    # {{{__init__
    def __init__(self):
        self.id=None
        self.inputfile=None
        self.dataframe=None
        self.nan=-1
    # }}}
    # {{{set_inputfile
    def set_inputfile(self,inputfile):
        self.inputfile=inputfile
    # }}}
    # {{{ get_dataframe
    def get_dataframe(self):
        self.dataframe=(pd.read_csv(self.inputfile,sep=' ', skiprows=6, header=None))
        self.dataframe.dropna(inplace=True,axis=1)
        self.dataframe.replace(to_replace=-1,value=np.nan,inplace=True)
        print(self.dataframe)
    # }}}
# }}}
# vim:foldmethod=marker:foldlevel=0
