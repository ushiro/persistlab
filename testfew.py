#!/usr/bin/env python

"""Edit this file to select unittest to perform"""

import os
import sys
import unittest

from persistlab import data
from persistlab.testsuite import caller
from persistlab.testsuite import test_figitem
from persistlab.testsuite import test_measfile
from persistlab.testsuite import test_persist
from persistlab.testsuite import test_batlab

def main():
    0 and caller.test_method(test_persist.TestPersist,'test_load')
    0 and caller.test_method(test_batlab.BatLab,'test_config_write')
    0 and caller.test_method(test_measfile.FlatFile,'test_parse')
    
    0 and caller.test_class(test_measfile.FlatFile)    
    0 and caller.test_class(test_measfile.Selection)    
    0 and caller.test_class(test_figitem.Offset)    
    0 and caller.test_class(test_batlab.BatLab_config_setup)
    
    0 and caller.test_module(test_persist)    
    0 and caller.test_module(test_figitem)    
    1 and caller.test_module(test_measfile)
    0 and caller.test_module(test_batlab)

    0 and caller.test_package()
    
if __name__ == "__main__":
    main()
    sys.exit(0)

#


