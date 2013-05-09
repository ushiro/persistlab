#!/usr/bin/env python

"""Plugins system for persistlab - Not debugged.

This code is separated for debugging purpose, 
as pkg_resources takes a while to import"""

from pkg_resources import iter_entry_points

import batlab

class PersistLabPlugins(batlab.PersistLab):
    
    def __init__(self, grpc='plab_processor', 
                    grpf='plab_figure', grpp='plab_parser'):
        super(PersistLabPlugins, self).__init__()
        self.load_plugins(container=self.plotter.figtypes, group=grpf)
        self.load_plugins(container=self.dataparser.fileformats,group = grpp)
        self.load_plugins(container=self.dataproc.processors, group=grpc)
    
    def load_plugins(self, container={}, group=''):
        for ep in iter_entry_points(group=group):
            # Load plugins
            try:
                container[ep.name] = ep.load()
            except:
                print "error loading plugins " + str(ep)
            self.plugins_versions[ep.dist.project_name] = ep.dist.version
    
    def populate_settings(self):
        super(PersistLabPlugins, self).populate_settings()
        self.sm.config['versions'].update(self.plugins_versions)

def persistlab(*args, **kwargs):
    return batlab.persistlab(PLab=PersistLabPlugins, **kwargs)
