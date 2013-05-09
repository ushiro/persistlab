#!/usr/bin/env python
"""
    persistlab.fileutils
    ~~~~~~~~~~~~~

    filename and path operations

    :copyright: (c) 2013 by Stephane Henry.
    :license: BSD, see LICENSE for more details.

"""

import os
import glob
import re


def check_dir(d):
    """Create a directory if it doesn't exist"""
    not os.path.isdir(d) and os.mkdir(d)

def get_basename(fn):
    return os.path.splitext(os.path.basename(fn))[0]

def incr(matchobj):
    matchgrp = matchobj.group()
    if matchgrp:
        try:
            return "{}".format(int(matchgrp) + 1).zfill(2)
        except:
            pass
    else:
        return '_00'

def find_non_existing_file(folder='', fn=''):
    while os.path.isfile(os.path.join(folder, fn)):
        bn, ext = os.path.splitext(fn)
        bn = incr_num_in_string(bn)
        fn = bn+ext
    return fn
    
def find_non_existing_dir(dn):
    """Increase the number in the directory name given as input,
    until a non-existing one is found."""
    while os.path.isdir(dn):
        dn = incr_num_in_string(dn)
    return dn

def add_num(str_):
    """add number at the end of a string if there isn't any."""
    if not re.search('\d*$',str_).group():
        str_ += '_00'
    return str_


def incr_num_in_string(_string):
    """Increments the number at the end of the string given as argument, then 
    returns the string. Append '_00' to the string if no number is found 
    inside the string.
    
    >>> incr_num_in_string('input_string')
    'input_string_00'
    
    >>> incr_num_in_string('input_string_42')
    'input_string_43'
    
    >>> incr_num_in_string('input_00string')
    'input_00string_00'
    """
    return re.sub('\d*$',incr,_string)

if __name__ == "__main__":
    #incr_num_in_string has docstrings
    import doctest
    print doctest.testmod()

# Other utilitary functions

def list_flatten(list_of_list):
    """have a look at from matplotlib.cbook import flatten"""
    return [i for j in list_of_list for i in j if i]
