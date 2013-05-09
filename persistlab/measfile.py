#!/usr/bin/env python
"""
    persistlab.measfile
    ~~~~~~~~~~~~~

    This module implements the data file parsing.

    :copyright: 2013 Stephane Henry.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

import os
import re
import csv

import pandas 
import numpy

#The regular expression ``[+-]?(\d+(\.\d*)?|\.\d+)`` matches
#floating-point numbers (without exponents).
REGEX_FLOAT = "[-+]?[0-9]*\.?[0-9]+"

def listify(obj):
    """listify(object) -- return object, listified if it is not iterable"""
    return not hasattr(obj, '__iter__') and [obj] or obj

class Selection(list):
    
    def __init__(self, df, columns = [-1]):
        self._ncols = df.shape[1]
        self._set = set([])
        if columns == [-1]:
            self.select_all()
        else:
            self.add(columns)
    
    def select_all(self):
        self.add(range(self._ncols))
    
    def add(self, obj):
        """SEL.add(object) -- add object to selection.""" 
        [self._set.add(v) for v in listify(obj) if 0<=v<self._ncols]
        list.__init__(self, self._set)

    def drop(self, obj):
        """SEL.drop(object) -- drop object from selection."""
        self._set.difference_update(listify(obj))
        list.__init__(self, self._set)


def sniff_delimiter(str_data):
    return csv.Sniffer().sniff(str_data).delimiter

class FlatFile():
    
    """Data file parser with column selection facility"""
    
    def __init__(self, filename, data_channels=[-1], **kwargs):
        self.fn = filename
        self.bn = os.path.basename(filename)
        self._parse_header()
        self.df = self._parse_data(**kwargs)
        self._selection = Selection(df=self.df, columns=data_channels)
        if 0 :
            # Remove index name so it doesn't appear on figure
            df.index.name = None
    
    def _parse_header(self, regex_float=REGEX_FLOAT):
        self.liheader = []
        with open(self.fn) as f :
            for line in f:
                if re.match(regex_float, line):
                    # Store the first line of data
                    self.str_data = line
                    break
                self.liheader.append(line)
    
    def _parse_data(self, **kwargs):
        """reads data from file and remove columns full of Nan values"""
        
        sep=sniff_delimiter(self.str_data)
        names = range(len(self.str_data.strip().split(sep))-1)
        
        # Parse data file
        if int(pandas.__version__.split('.')[1])>10:
            df = pandas.read_csv(self.fn,skiprows=len(self.liheader)-1,
                            header=0,index_col=0,dtype=float, names=names)
        else:
            df = pandas.read_csv(self.fn, 
                            dtype=float, 
                            skiprows=len(self.liheader), 
                            sep=sep, 
                            names=names,
                            header=None, 
                            index_col=0)
        
        # remove empty values
        df = df.dropna(axis=0,how='all')
        df = df.dropna(axis=1,how='all')
        
        # return the dataframe
        return df
    
    def __iter3__(self):
        return self.dfs().iteritems()
    
    
    def __iter2__(self):
        for colname,  series in self.selection().iteritems():
            yield series
        
    def __iter__(self):
        """Iterate over the selected columns from the data dataframe """
        for col in self._selection:
            yield self.df.icol(col)
    
##    def selection(self):
    def dfs(self):
        """return the dataframe of selected columns"""
        return self.df.icol(self._selection)


class XSegFile(FlatFile):
    
    def _parse_data(self, data_segment_range = -1, **kwargs):
        segments = data_segment_range
        with open( self.fn, 'ru') as fo :
            liseg = []
            [fo.readline() for i in range ( len(self.liheader)-2) ]
            reader = csv.reader(fo, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
            while 1 :
                try :
                    n = reader.next()
                except ValueError as er :
                    liseg.append([])
                    continue
                except StopIteration:
                    break
                n and liseg[-1].append(n)
        
        # Select segments
        if not segments == -1:
            if len(segments) == 1:
                segments.append(segments[0])
            if len(segments) == 2:
                liseg = liseg[segments[0]:segments[1]+1]
        
        # All the segments are concatenated here...
        lidf = [pandas.DataFrame(ar).set_index(0) for ar in numpy.array(liseg)]
        return pandas.concat(lidf)



class DataFileParser:
    
    def __init__(self):
        # Data file formats
        self.fileformats = {}
        self.fileformats ['flat' ] = FlatFile
        self.fileformats ['xseg' ] = XSegFile
    
    def parse_files(self, data_files=[], data_format='flat', 
                    verbose=0, **kwargs):
        DFF = self.fileformats[data_format]
        limf = [DFF(fn, **kwargs) for fn in data_files]
        TXT = 'parsed files: {}'
        verbose and print (TXT.format (' '.join([mf.bn for mf in limf])))
        return [mf for mf in limf if mf]

class DataProcessor:
    
    def __init__(self):
        self.processors = {'trapz':numpy.trapz}
    
    def compute(self, limf, data_process='', verbose=0, **kwargs):
        if data_process.startswith('numpy'):
            func = getattr(numpy, data_process.split('.')[1])
        else:
            func = self.processors[data_process]
        df_stats = self.apply_ufunc(limf=limf, ufunc=func)
        
        # Verbose
        if verbose:
                print ('Calculations with {}:'.format(data_process))
                print (df_stats)
        
        return df_stats
    
    def apply_ufunc(self, limf, ufunc):
        res = pandas.concat([mf.dfs().apply(ufunc) for mf in limf], axis=1)
        res.columns = [mf.bn for mf in limf]
        return res

# DEBUG
def debug():
    
    # -------- FlatFile ------ #
    fn =  data.FLATFILE_1
    mf = FlatFile(fn, columns=[0, 3, 4])
    # plot selection
    ax = mf.dfs().plot()
    # Column iterator
    for s in mf:
        print (s)
    
    # -------- Multi-channel ------------- #
    xsegfile = XSegFile(data.LI_FN_XSEG[0])
    xsegfile.df.plot(ax=ax)
    
    plt.show()

if __name__ == "__main__":
    import data
    from matplotlib import pyplot as plt
    debug()

#

