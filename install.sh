#!/bin/bash
rm -rf deb_dist/
python setup.py --command-packages=stdeb.command bdist_deb
dpkg -i deb_dist/python-persistlab*.deb

cd PersistLabPlugins
python setup.py --command-packages=stdeb.command bdist_deb
dpkg -i deb_dist/python-persistlabplugins*.deb
