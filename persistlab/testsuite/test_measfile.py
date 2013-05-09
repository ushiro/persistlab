#!/usr/bin/env python
"""
    persistlab.testsuite.measfile
    ~~~~~~~~~~~~~

    This module tests the data file parsing.

    :copyright: (c) 2013 by Stephane Henry..
    :license: BSD, see LICENSE for more details.
"""

import sys
import unittest

import pandas
import pandas as pd
import numpy as np

from persistlab import measfile
from persistlab import data

def dataframe():
    index = ['a', 'b', 'c', 'd', 'e']
    columns = ['one', 'two', 'three', 'four']
    M = pd.DataFrame(np.random.randn(5,4), index=index, columns=columns)
    return M

class Selection(unittest.TestCase):
    
    def setUp(self, df=dataframe()):
        self.df = df
        self.all = range(len(df.columns))
    
    def add(self, attr, res):
        selection = measfile.Selection(self.df, [])
        selection.add(attr)
        self.assertEqual(selection, res)
    
    def drop(self, attr, res):
        selection = measfile.Selection(self.df)
        selection.drop(attr)
        self.assertEqual(selection, res)
    
    def test_droplist(self):
        self.drop([0, 5], [1, 2, 3])
    
    def test_dropint(self):
        self.drop(0, [1, 2, 3])
    
    def test_add_int(self):
        self.add(0, [0])
    
    def test_add_list(self):
        self.add([0, 1], [0, 1])
    
    def test_add_non_existing(self):
        self.add(range(-3, 5), range(4))
    
    def test_selectall(self):
        selection = measfile.Selection(self.df)
        self.assertEqual(selection, self.all)


class FlatFile(unittest.TestCase):
    
    def setUp(self):
        self.mf = measfile.FlatFile(data.FLATFILE_1)
    
    def test_parse(self):
        # Check shape of the  data
        self.assertEqual(self.mf.df.shape, (3, 4))
    

class XSeg(unittest.TestCase):
    
    def test_no_segment_selection(self):
        mf = measfile.XSegFile(data.LI_FN_XSEG[0])
        # Test shape
        self.assertEqual(mf.df.shape, (320, 3))
        # Test one value
        self.assertEqual(mf.df.ix[0][1] , 3.388e-09)
    
    def test_oneseg(self):
        mf = measfile.XSegFile(data.LI_FN_XSEG[0],  data_segment_range=[1])
        self.assertEqual(mf.df.shape, (80, 3))
    
    def test_twoseg(self):
        mf = measfile.XSegFile(data.LI_FN_XSEG[0],  data_segment_range=[0, 1])
        self.assertEqual(mf.df.shape, (160, 3))
    
    def test_threeseg(self):
        mf = measfile.XSegFile(data.LI_FN_XSEG[0],  data_segment_range=[1, 3])
        self.assertEqual(mf.df.shape, (240, 3))


class DataFileParser(unittest.TestCase):
    
    def setUp(self):
        dfp = measfile.DataFileParser()
        self.limf = dfp.parse_files(data.LI_FLATFILE_ALL)
        
    def test_set_filetype(self):
        self.assertIsNotNone(self.limf[0])

    def test_parse_files(self):
        self.assertEqual(len(self.limf),3)

class DataProcessor(DataFileParser):
    
    def test_process(self):
        dp = measfile.DataProcessor()
        stats = dp.compute(self.limf, data_process='trapz')
        self.assertIsInstance(stats,pandas.DataFrame)



