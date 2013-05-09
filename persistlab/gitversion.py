#!/usr/bin/env python

"""
    gitversion.py
    ~~~~~~~~

    :copyright: (c) 2013 Stephane Henry.
    :license: BSD, see LICENSE for more details.
    
    inspired from
    https://github.com/fancycode/pylzma/blob/master/version.py
"""
import os
from os import linesep as ls
from subprocess import Popen, PIPE

VAR_VERSION = "__version__"


def call_git_describe():
    p = Popen(['git', 'describe', '--tags' ], stdout=PIPE, stderr=PIPE)
    p.stderr.close()
    return p.stdout.read().strip()

class GitVersion:
    
    def __init__(self, fn='VERSION.py', 
                    content_version = "{he}{ls}{ls}{vv} = '{rv}'", 
                    str_unversionned = "Unversionned", 
                    hash_excl = '#!/usr/bin/env python',
                    var_version = VAR_VERSION, 
                    verbose=0, 
                    **kwargs):
        
        self.verbose = verbose
        self.he = hash_excl
        self.cv = content_version
        self.str_unversionned = str_unversionned
        self.vv= var_version
        
        # Define version file path
        global __package__
        if __package__ == None:
            __package__ = os.path.basename(os.path.dirname(__file__))
            if not isinstance(__package__, type(u'')):
                __package__ = ''
        self.fn = os.path.join(__package__,fn)
    
    def parse_release_version(self):
        with open(self.fn) as f: 
            for l in f.readlines() :
                if self.vv in l:
                    return l.split('=')[1].strip().replace("'","") 
    
    def update_release_version(self, **kwargs):
        # Fetch git version
        rv = call_git_describe() or self.str_unversionned
        str_version = self.cv.format(he=self.he, ls=ls, vv=self.vv, rv=rv)
        
        # Write version to file
        with open(self.fn, 'w') as fo:
            fo.write(str_version)
        if self.verbose:
            print "release version : " + rv,  
            print 'written to ' + self.fn

def setup_version(**kwargs):
    gv = GitVersion(**kwargs)
    gv.update_release_version()
    return gv.parse_release_version()

def get_version_from_pkg_resources(module):
    try:
        return pkg_resources.get_distribution(module).version
    except pkg_resources.ResolutionError:
        return None

