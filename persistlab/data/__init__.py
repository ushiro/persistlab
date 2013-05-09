#!/usr/bin/env python

import os
import glob

##DATADIR = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.dirname(__file__)

# Flat files
LI_FLATFILE_ALL = glob.glob(os.path.join(DATADIR,'flatfile_*.txt'))
LI_FLATFILE_ALL.sort()

for i, fn in enumerate(LI_FLATFILE_ALL):
    globals()['FLATFILE_'+str(i)] = fn

# Multiple segments
LI_FN_XSEG = glob.glob(os.path.join(DATADIR,'*multi*'))

