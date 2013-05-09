#!/usr/bin/env python
import sys
import os
import glob


from setuptools import setup

from persistlab import gitversion 

NAME = 'persistlab'
DESCRIPTION = ("Data file processing and visualisation "
                "with persistance of the settings")

def main():
    setup(name=NAME, 
                    version=gitversion.setup_version(verbose=1), 
                    description=DESCRIPTION, 
                    author='Stephane Henry',
                    author_email='stef.henry@gmail.com', 
                    packages=['persistlab',
                                    'persistlab.data', 
                                    'persistlab.testsuite'], 
                    license='LICENSE.txt',
                    long_description=open('README.txt').read(), 
                    package_data= {'persistlab':['data/*.txt']}, 
                    scripts=[  'bin/persistlab','bin/persistlab_testall'], 
                )

if __name__ == "__main__":
    main()
