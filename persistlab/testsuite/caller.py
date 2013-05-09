#!/usr/bin/env python

import os
import unittest

def test_method(TestClass, str_method):
    """Unittests a test method."""
    suiteFew = unittest.TestSuite()
    suiteFew.addTest(TestClass(str_method))
    unittest.TextTestRunner(verbosity=2).run(suiteFew)
    
def test_class(Class):
    """Unittests a test class."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Class))
    unittest.TextTestRunner(verbosity=2).run(suite)

def test_module(module):
    """Unittests a test module"""
    unittest.main(module)
    
def test_package(package=None):
    """Unittests a test package"""
    if not package:
        m = os.path.split(os.path.abspath(__file__))[0]
    else:
        m = os.path.dirname(package.__file__)
    testsuite = unittest.TestLoader.discover(unittest.defaultTestLoader, m)
##    unittest.TextTestRunner(verbosity=2).run(testsuite)
    unittest.TextTestRunner().run(testsuite)

