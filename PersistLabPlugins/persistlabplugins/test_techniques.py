#!/usr/bin/env python

import unittest

from persistlab.batlab_plugins import PersistLabPlugins
from persistlabplugins import techniques
from persistlabplugins import data

class Figure:
    
    def setUp(self):
        self.plab = PersistLabPlugins()
    
    def runTest(self, **kwargs):
        self.plab.exec_kwargs(data_files = self.data_files, 
                        figure_type=self.figure_type, 
                        figure_plot = 1, 
                        figure_show = 0, 
                        **kwargs)
        self.assertEqual(self.FigClass, self.plab.plotter.lifm[0].__class__)


class TransientFigure(Figure, unittest.TestCase):
    
    data_files = data.LIFNTRANSIENT
    figure_type = 'transient'
    FigClass = techniques.FigTransient


class CVFigure(Figure, unittest.TestCase):
    
    FigClass = techniques.FigCV
    data_files = data.LIFNCV
    figure_type = 'cv'
    
    def runTest(self, **kwargs):
        super(CVFigure, self).runTest(
                        data_format='xseg', 
                        # FAIL with data_segment_range=[2, 2], 
                        # FAIL with data_segment_range=[2], 
                        data_segment_range=[2, 3], 
                        data_channels = [0, 1])


def debug():
    plab = PersistLabPlugins()
    plab.args_parser().print_help()
    plab.exec_kwargs(data_files = data.LIFNTRANSIENT, 
                     figure_type='transient',
                    figure_plot = 1, figure_show = 1)

if __name__ == "__main__":
    debug()
