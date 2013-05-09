#! python

import os
import glob

DATADIR = os.path.dirname(os.path.abspath(__file__))

# !!! SOME TESTS MIGHT BE CREATING FIGURES IN mydata directory
LIFNTRANSIENT = glob.glob(os.path.join(DATADIR,'*transient*.txt'))

LIFNPROFILE = glob.glob(os.path.join(DATADIR,'*profile*'))
LIFNCV = glob.glob(os.path.join(DATADIR,'*cv*'))

# OCP
LIFN_OCP_CHI = glob.glob(os.path.join(DATADIR,'ocp_chi*'))
LIFN_OCP_NI = glob.glob(os.path.join(DATADIR,'ocp_ni*'))
LIFN_OCP_C = glob.glob(os.path.join(DATADIR,'ocpc*'))
