#!/usr/bin/env python
"""
    persistlab.persist.py
    ~~~~~~~~~~~~~~~

    Type casting for configobj instance,
    
    :copyright: 2013 Stephane Henry.
    :license: BSD, see LICENSE for more details.
    
"""

from __future__ import print_function

import os
from collections import OrderedDict as OD

import numpy

import configobj 
import validate 

TYPES = {
                bool:'boolean', 
                int:'integer', 
                float:'float', 
                str:'string', 
                numpy.float64:'float', 
                }

LIST_TYPES = {
                'integer': 'int_list', 
                'boolean': 'bool_list',
                'mixed': 'mixed_list', 
                'float': 'float_list',
                'string': 'string_list', 
                }

SUFFIX_CS = '.spec'

def populate_configspec(config_section,  section_spec):
    """ Populates config spec.
    
    This function is modified/inspired/? from the function add_configspec()
    from the ConfigPersist.py module at
    www.voidspace.org.uk/cgi-bin/voidspace/downman.py?file=ConfigPersist.py
    (BSD licenced at http://www.voidspace.org.uk/documents/BSD-LICENSE.txt),
    to allow for the following:
        * Values can be added to or removed from list items 
    in the settings file without breaking the type casting,
    as only one type is used for list items;
        * Type casting of numpy.float64
    """
    for entry, val in config_section.iteritems():
        if isinstance(val, tuple(TYPES.keys())):
            # an item
            section_spec[entry] = TYPES[type(val)]
        elif isinstance(val, dict):
            # a subsection
            section_spec[entry] = {}
            populate_configspec(config_section[entry], section_spec[entry])
        elif isinstance(val, (list, tuple)):
            # a multiple value, set to string if empty
            if len(val) == 0:
                section_spec[entry] = 'string_list'
            else:
                section_spec[entry] = LIST_TYPES[TYPES[type(val[0])]]


class SettingsManager:
    
    """ConfigObj wrapper"""
    
    def __init__(self, config_filename = 'settings.ini', 
                    settings_spec_suffix='_spec', verbose=0, **kwargs):
        self.verbose = verbose
        self.fn_spec_suffix = settings_spec_suffix
        self.config = configobj.ConfigObj()
        # the configuration filename is not given directly at instantiation
        # as the file would be parsed if existing
        self.fn = config_filename
    
    def fn_spec(self):
        return self.fn_spec_suffix.join(os.path.splitext(self.fn))
    
    def write(self):
        # Write the config to a file
        self.config.filename = self.fn
        self.config.write()
        # Make and write the configspec to a file
        config_spec = configobj.ConfigObj()
        config_spec.filename = self.fn_spec()
        populate_configspec(self.config, config_spec)
        config_spec.write()
        # Verbose
        fn = self.config.filename
        self.verbose and print ("written settings to {}".format(fn))
        fnspec = config_spec.filename
        self.verbose and print ("written settings specs to {}".format(fnspec))
    
    def load(self, fn=None):
        """ Load the parameters from the config file with type casting"""
        fn = fn or self.fn
        self.config = configobj.ConfigObj(fn, configspec=self.fn_spec())
        v = self.config.validate(validate.Validator())
        self.verbose and print ("Loaded settings, validation = {}".format(v))
    
    def check_section(self, section_name):
        if not self.config.has_key(section_name):
            self.config[section_name] = {}
    
    def fill_section(self, params, section_name='settings'):
        """Adds/update the items in sorted order from params.__dict__ to 
        the section section_name. The section is created if it doesn't exist.
        
        Params:
            @params: object with __dict__  attribute
            @section_name: string
        """
        # Check that the section exists
        self.check_section(section_name)
        # Update
        self.config[section_name].update(OD(sorted(vars(params).items())))
        # Alternate way for update:
        # for i, v in sorted(vars(params).items()):
        #     self.config[section_name][i] = v
    
    def cleanup(self):
        os.remove(self.fn)
        os.remove(self.fn_spec())   
    

# DEBUG
def debug():
    
    class Params:
        
        def __init__(self, params=None):
            params and vars(self).update(params)
    
    
    # Settings instance
    d = dict(an_integer = 1 , a_boolean = True, a_string ='a_string', 
                    c=True,  d=2,  a_list_of_floats=[234., 234.])
    p = Params(d)
    
    # Settings manager
    sm = SettingsManager(verbose=1)
    sm.fill_section(p)
    sm.write()
    sm.load()
    print (sm.config)
    os.remove(sm.config.filename)
    os.remove(sm.settings_spec_fn)
    
if __name__ == "__main__":
    debug()
#


