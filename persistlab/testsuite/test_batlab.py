#!/usr/bin/env python

"""
    persistlab.testsuite.batlab
    ~~~~~~~~~~~~~~~

    Tests the persistlab.batchlab module

    :copyright: (c) 2013 by Stephane Henry..
    :license: BSD, see LICENSE for more details.
    """

import unittest
import glob
import os
import shutil

import configobj

from persistlab import batlab
from persistlab import measfile
from persistlab import data

class BatLabPlotter(unittest.TestCase):
    
    def setUp(self):
        self.plotter = batlab.Plotter()
        lifn = data.LI_FLATFILE_ALL
        self.limf =  measfile.DataFileParser().parse_files(lifn)
    
    def assert_len_lifm(self, l):
        self.assertEqual(len(self.lifm), l)
    
    def assert_nb_lines(self, nb_lines):
        self.assertEqual([len(fm.ax.lines) for fm in self.lifm], nb_lines)
    
    def visualise(self):
        self.lifm = self.plotter.visualise(limf=self.limf, figure_mode=self.m)
    
    def test_mode_a(self):
        self.m = 'a'
        self.visualise()
        self.assert_len_lifm(1)
        self.assert_nb_lines([6])
    
    def test_mode_s(self):
        self.m = 's'
        self.visualise()
        self.assert_len_lifm(1)
        self.assert_nb_lines([4])
    
    def test_mode_o(self):
        self.m = 'o'
        self.visualise()
        self.assert_len_lifm(3)
        self.assert_nb_lines([1, 4, 1])
    

class BatLabBase(object):
##class BatLabBase:
    
    def setUp(self):
        batlab.clean_output()
        self.plb = batlab.PersistLab()
    
    def tearDown(self):
        batlab.clean_output()


class BatLab(BatLabBase, unittest.TestCase):
    
    item = 'data_process'
    item_new_val = 'some_process'
    
    def change_a_config_value(self):
        # Change some value
        config = configobj.ConfigObj(self.plb.sm.fn)
        
        section = 'Configuration'
        config[section][self.item] = self.item_new_val
        config.write()
    
    def test_config_write(self):
        self.plb.config_write()
        self.assertEqual(vars(self.plb.params), vars(batlab.Settings()))
        os.remove(self.plb.sm.fn)
        os.remove(self.plb.sm.fn_spec())
    
    def test_config_load(self):
        self.plb.config_write()
        self.change_a_config_value()
        
        #Load
        self.plb.config_load()
        self.assertEqual(getattr(self.plb.params,self.item),self.item_new_val)

    def test_config_setup(self):
        some_process = 'some_calculation'
        self.plb.config_setup(data_process=some_process)
        self.assertEqual(self.plb.params.data_process, some_process)

    def test_args_parser__segment_range_0(self):
        """Make sure that the args_parser returns a list"""
        args = self.plb.args_parser().parse_args('-r 2 3'.split())
        sr = args.data_segment_range
        self.assertIsInstance(sr, list)
    
    def test_args_parser__segment_range_1(self):
        """Make sure that the args_parser returns a list when no args given"""
        args = self.plb.args_parser().parse_args()
        sr = args.data_segment_range
        self.assertIsInstance(sr, list)
        
    def test_args_parser(self):
        """Verifies that the arguments returned by the args_parser
        are present in and equal to the oens from the Settings() class"""
        clargs_dict = vars(self.plb.args_parser().parse_args())
 
        li_assertion_error = []
        li_key_error = []
        dict_settings = vars(self.plb.params)
        for k in clargs_dict.keys():
            try :
                self.assertEqual(getattr(self.plb.params, k),clargs_dict [k])
            except AssertionError:
                li_assertion_error.append(k)
            except KeyError:
                li_key_error.append(k)
        msg = ''
        if li_assertion_error:
            msg += "AssertionError on keys {}".format(li_assertion_error)
            msg += os.linesep
        if li_key_error:
            msg += "KeyError on keys {}".format(li_key_error)
            msg += os.linesep
        if msg:
            msg += 'self.params = {}'.format(dict_settings)
            msg+= os.linesep
            msg += 'clargs = {}'.format(clargs_dict )
            raise self.failureException(msg)
        
    
    
    def test_cli(self):
        some_process =  'some_calculation'
        self.plb.config_setup(['--data-process', some_process])
        self.assertEqual(self.plb.params.data_process, some_process)
    
    def test_cli_load_settings(self):
        """Command line interface _ load settings from file option"""
        self.plb.params.figure_plot=1
        self.plb.config_write()
        # Force to 0
        self.plb.params.figure_plot=0
        # and ask to use configuration file
        self.plb.config_setup(clargs=['--config-load-from', self.plb.sm.config.filename])
        self.assertTrue(self.plb.params.figure_plot)

    
    def test_cli_load_settings_ow_by_cla(self):
        """Make sure command line args ovewite the one loaded from file"""
        self.plb.params.figure_mode='s'
        self.plb.config_write()
        
        # Set a different value to be sure 
        self.plb.params.figure_plot= 'a'
        # and ask to use configuration file
        self.plb.config_setup(clargs = [
                        # load settings
                        '--config-load-from', self.plb.sm.config.filename, 
                        # Set mode
                        '--figure-mode', 'o'])
        self.assertEqual(self.plb.params.figure_mode, 'o')
    
    def test_exec(self):
        """Run the code with as many options as possible"""
        self.plb.exec_kwargs(
                    data_files=data.LI_FLATFILE_ALL,
##                    data_format='flat', 
                    # Select some channels
                    channels=[0, 1, 3], 
                    # Process data
                    data_process='numpy.trapz', 
##                    figure_manager='basic', 
                    # Plot figure
                    figure_plot = 0, 
                    figure_mode='s', 
                    figure_show=0,
                    figure_use_color = 1, 
                    figure_use_markers = 1, 
##                    figure_use_dashes=1, 
                    figure_use_line_style=1, 
                    figure_write=1, 
                    # Publish document
                    publish = 1, 
                    publish_formats=['rst', 'pdf', 'html'], 
                    # Write settings
                    settings_write = 1, 
                    verbose=0
                    )
    

class BatLab_config_setup(BatLabBase, unittest.TestCase):
    
    def setUp(self):
        super(BatLab_config_setup, self).setUp()
##        BatLabBase.setUp(self)
        self.plb.params.figure_mode='s'
        self.plb.config_write()
        self.plb.params.figure_mode='non existing mode'
        
    def test_config_setup__load_settings(self):
        """Loads settings from file"""
        self.plb.config_setup(clargs=['--config-load-from', self.plb.sm.config.filename])
        self.assertEqual(self.plb.params.figure_mode, 's')
    
    def test_config_setup__load_settings_overwrite(self):
        """Make sure kwargs have priority over the settings loaded from file"""
        self.plb.config_setup(clargs=['--config-load-from', self.plb.sm.config.filename, 
                                      '--figure-mode',  'o'])
        self.assertEqual(self.plb.params.figure_mode, 'o')


