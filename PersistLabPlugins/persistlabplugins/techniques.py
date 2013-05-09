#!/usr/bin/env python

import time
import re
import math
from collections import OrderedDict as OD

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from persistlab import measfile
##from persistlab import figitem
from persistlab import batlab

__version__ = '0.0'

class FigTransient(batlab.DefaultFigure):
    
    def __init__(self, *args, **kwargs):
        super(FigTransient, self).__init__(*args, **kwargs)
        self.figure_items ['ax.xlabel'] = 'Time (s)'
        self.figure_items ['ax.ylabel'] = 'Current (A)'


class FigCV(batlab.DefaultFigure):
    
    di_settings = {'arrow_size' : 4, 
##                'arrow_xpos' : 0.005, 
##                'seg_start':3, 
##                'seg_stop':4, 
                }
    
    def __init__(self, *args, **kwargs):
        super(FigCV, self).__init__(*args, **kwargs)
        self.figure_items ['ax.xlabel'] = 'Potential (V)'
        self.figure_items ['ax.ylabel'] = 'Current (A)'
    
    def plot_series(self, series, verbose=0, *args, **kwargs):
        super(FigCV, self).plot_series(series, *args, **kwargs)
        
        # Plot an arrow
        if kwargs['i'] == 0:
            xlim = self.ax.get_xlim()
            if xlim[0]>xlim[1]:
                xlim = tuple(reversed(xlim))
            if verbose > 1:
                print str(xlim)
            x0 = xlim[1]-(1./4)*(xlim[1]-xlim[0])
            x_arrow = x0 + kwargs['i']*0.005
            if verbose > 1:
                print '{}'.format(x_arrow)
            
            X = series.index[series.index.searchsorted(x_arrow)]
            plt.plot (X, series[X][0], '>', 
                                markersize = self.di_settings['arrow_size'], 
                                color = "k")
    
    def adorn(self, **kwargs):
        self.ax.axes.invert_xaxis()


#


