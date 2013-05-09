#!/usr/bin/env python
"""
    persistlab.testsuite.test_figuremanager
    ~~~~~~~~~~~~~~~

    Tests the figitem module

    :copyright: (c) 2013 by Stephane Henry..
    :license: BSD, see LICENSE for more details.

"""

import sys
import unittest

from matplotlib import pyplot as plt

from persistlab import figitem

class Item(unittest.TestCase):
    
    str_item = ''
    value = None
    
    def setUp(self):
        fm = figitem.FigureManager()
        line = fm.ax.plot([2, 3], [4e-6, 9e-6], label='line 1')
        fm.legend = fm.ax.legend()
        if self.str_item:
            self.item = fm.add_item(self.str_item, self.value)
    
    def test(self):
        self.str_item and self.assertEqual(self.item.get(), self.value)

class ItemMultiVal(Item):
    
    def test(self):
        if self.str_item:
            self.assertEqual(list(self.item.get()), list(self.value))
#
class AxPowerLimits(ItemMultiVal):
    str_item = 'ax.y.powerlimits'
    value = (3, 3)

class LegendLoc(Item):
    str_item = 'legend.legendloc'
    value = 3

class LagendPos(ItemMultiVal):
    str_item ='legend.legendpos'
    value= (0.5, 0.5)
    
class MaxNLocator(Item):
    str_item ='ax.y.maxnlocator'
    value= 5

class FigureSize(ItemMultiVal):
    str_item ='figure.size_inches'
    value= (10, 12)

class Grid(Item):
    str_item ='ax.grid'
    value= 1

class LabelText(Item):
    str_item = 'ax.y.label_text'
    value= 'Some label'


class LabelPos(ItemMultiVal):
    str_item = 'ax.y.label_pos'
    value= (-0.02, 0.5)
    
class AxisLimit(ItemMultiVal):
    str_item = 'ax.ylim'
    value= [4e-6, 10e-6]

class AxMaxnLocator(Item):
    str_item = 'ax.y.maxnlocator'
    value = 5

class useOffset(Item):
    str_item  = 'ax.y.useOffset'
    value = 0


class Offset(Item):
    str_item  = 'ax.y.offset'
    value =  ''

class SubplotADjust(Item):
    str_item = 'figure.left.subplot_adjust'
    value = 0.5

class TighthLayout(Item):
    str_item = 'figure.tight_layout'
    value = 0
    

    
    
