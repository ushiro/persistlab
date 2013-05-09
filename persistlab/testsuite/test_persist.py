#!/usr/bin/env python
"""
    persistlab.testsuite.persist
    ~~~~~~~~~~~~~~~

    Tests the persistlab.persist module

    :copyright: (c) 2013 by Stephane Henry..
    :license: BSD, see LICENSE for more details.
"""

import os
from os import linesep as ls

import unittest

from persistlab import persist

class Settings:
    
    def __init__(self):
        an_integer = 1
        a_float = 2
        a_boolean = False
        a_boolean = 'some text'

class TestPersist(unittest.TestCase):
    
    def setUp(self):
        self.sm = persist.SettingsManager()
        
    def test_write(self):
        #Add some items
        self.sm.config['Section'] = {}
        self.sm.config['Section']['item'] = 'value'
        self.sm.write()
        # The test will fail if the files don't exist
        self.sm.cleanup()
    
    def test_load(self):
        """
        TO CODE:
        
        test all types:
                    {bool:'boolean', 
                    int:'integer', 
                    float:'float', 
                    str:'string', 
                    numpy.float64:'float'}
                    
                    and lists of them
                    
                    and types that can fail, e.g. # a multiple value"""
        with open(self.sm.fn, 'w') as t:
            t.write('[section]' + ls)
            t.write('item = 1' + ls)
        with open(self.sm.fn_spec(), 'w') as ss:
            ss.write("[section]" + ls)
            ss.write("item = integer" + ls)
        self.sm.load()
        self.sm.cleanup()
        self.assertEqual(self.sm.config['section']['item'] ,1)
    
    def test_fill_section(self):
        self.sm.fill_section(Settings())

