#!/usr/bin/env python

from setuptools import setup

def main():
    
    # plugins
    figures = [
                    'transient = persistlabplugins.techniques:FigTransient',
                    'cv = persistlabplugins.techniques:FigCV' 
                    ]
    
    setup(name='persistlabplugins',
                    version='0.0', 
                    description='persistlab plugins example',
                    packages=['persistlabplugins','persistlabplugins.data'],
                    package_data = {'persistlabplugins':
                                    ['data/*.txt', 'data/*.csv']}, 
                    entry_points = {'plab_figure': figures, 
                                    'plab_parser' : [], 
                                    'plab_processor' : []}, 
                    scripts=[  'persistlabplugins_testall'], 
                                    )

if __name__ == "__main__":
    main()
