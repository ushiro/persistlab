README file for persistlab package

==========
PersistLab
==========
Persistant data processing, visualisation and publishing.

It performs the following operations:

- data from files is loaded into Pandas dataframe;
- processed;
- plotted, with some interactivity facilities;
- the results are published into reStructuredText/latex.pdf/html documents;
- the parameters involved are logged into a settings file 
  that can then be manually edited and used to run the code 
  encore et encore

The code can be run through the command line or by common python import

Comments (and contributions!) are more than welcome, see
github.com/ushiro/persistlab/

Usage
=====

From the command line::
    
    $ persistlab --help

From the python interpreter, allowing for direct customisation::

    from persistlab import batlab
    plab = batlab.persistlab(
                    # Data files
                    data_files=['data_a.txt','data_b.txt']
                    # Integrate
                    data_process='numpy.trapz',
                    # Publish into html document through reStructuredText
                    self.publish = 1,
                    self.publish_formats=['html']
                    )
 

Extend persistlab with your own plugins
=======================================
An example is given in the PersistLabPlugins directory,
with a setup.py file providing the usual installation means.
This demo adds two figure types: cyclic voltammetry and transient.
Commit your own to the repo!


Requirements
============

System
------

- python 2.7

Python
~~~~~~

- matplotlib (>=1.0  to be able to use draggable legend and tightlayout)
- pandas
- numpy
- rubber and latex building tools for pdf output 
  (had to install 'texlive-fonts-recommended' on debian)
- ConfigObj4
- setuptools, used for 'develop' option at install and entry points
- pkg_resources, this package is useful 
  for entry points and eventually release versioning

Recommended Python packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- stdeb for debian package installation



Installation
============

Debian package installation 
---------------------------

create the deb package with::

    $python setup.py --command-packages=stdeb.command bdist_deb


then to install (with superuser privilege)::

    dpkg -i deb_dist/python-persistlab_*.deb
    

and to un-install ::

    dpkg --purge python-persistlab


or::

    apt-get remove python-persistlabplugins
    
    
more infos at http://pypi.python.org/pypi/stdeb


Alternate install
-----------------

::
    
    $ python setup.py install

In debian/ubuntu this will install the packages in 
/usr/local/lib/python/dist-package.
'runner' scripts will be in /usr/local/bin

Alternativelly, to be able to un-install, use the following options
::
    
    $ python setup.py install --record files.txt
    
Then the un-install can be performed by
::

    $ cat files.txt | xargs sudo rm -rf
    
this will not delete the directories...


Develop install
---------------
::
    
    $ python setup.py develop

    

ACKNOWLEDGMENT
==============

Acknowledgments for funding go to 
Engineering & Physical Sciences Research Council
(http://www.epsrc.ac.uk) and 
National Physical Laboratory(http://www.npl.co.uk).

