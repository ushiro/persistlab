#!/usr/bin/env python
"""
    persistlab.batlab
    ~~~~~~~~~~~~~

    This implements the core of persistlab features.

    :copyright: (c) 2013 Stephane Henry.
    :license: BSD, see LICENSE for more details.
    
    
    Some Improvements?
    ~~~~~~~~~~~~~
    * figure size option to cli
    * bigger line size in plots
    * smaller legend numbers 
    * and, and, and...
"""

from __future__ import print_function

import StringIO
import glob
import sys
import os
import shutil
import argparse
from collections import OrderedDict

from matplotlib import pyplot
import configobj
import pandas

import persist
import figitem
import measfile
import publishrst
from VERSION import __version__
from fileutils import find_non_existing_dir as fned


class DefaultFigure(figitem.FigureManager):
    
    def __init__(self, *args, **kwargs):
        super(DefaultFigure, self).__init__(*args, **kwargs)
        
        # Figure items
        self.figure_items = OrderedDict()
        self.figure_items ['ax.xlabel'] = 'X label with no unit and a dot.'
        self.figure_items ['ax.ylabel'] = 'Y(SI)'
        self.figure_items ['ax.grid'] = 0
        self.figure_items['ax.x.powerlimits'] = [-3, 3]
        self.add_item('ax.y.powerlimits', [-3, 3])
        
        mlx = self.add_item('ax.x.maxnlocator',  5)
        self.add_interact(item=mlx, key='1', value=1)
        self.add_interact(item=mlx, key='!', value=-1)
        mly = self.add_item('ax.y.maxnlocator',  5)
        self.add_interact(item=mly, key='2', value=1)
        self.add_interact(item=mly, key='"', value=-1)


class Settings:

    def __init__(self):
        """The default values must give a type compatible with persist.py
        e.g. no empty list, so type casting works"""

        # Configuration file
        self.config_write = 0
##        self.config_load = 0
        self.config_load_from=''        
        # Data files
        self.data_files=[]
        self.data_format='flat'
        self.data_channels=[-1]  
        self.data_segment_range = [-1]
        # Data processing
        self.data_process=''
        self.data_process_fn='stats.csv'
        # Plotting
        self.figure_write=0
        self.figure_plot = 0
        self.figure_mode='a'
        self.figure_type='default'
        self.figure_show=0
        self.figure_formats = ['eps', 'jpg', 'svg']
        self.figure_legend = 1 # args_parser says show by default
        self.figure_use_color = 0
        self.figure_use_markers = 0
        self.figure_use_dashes = 0
        self.figure_use_line_style = 0
        # General output
        self.output_dir='output'
        self.output_overwrite=0
        # Report
        self.publish = 0
        self.publish_float_format='%.2e'
        self.publish_formats=['html']
        self.publish_base_name = 'report'
        # Verbose
        self.verbose=0
    
    # Convenience methods
    def print_items(self):
        for k in sorted(self.__dict__.keys()):
            print ('{} = {}'.format(k, self.__dict__[k]))

    def update(self, params):
        vars(self).update(params)
    
    def __call__(self):
        return vars(self)


class Plotter(object):
    
    def __init__(self, **kwargs):
        # Figure managers
        self.figtypes = {'default':DefaultFigure}
        self.modes = ['a', 'o', 's']
    
    def write_figures(self, lifm, verbose=0, figure_formats=['.jpg'], 
                      output_dir='output_dir', **kwargs):
##        [fm.write_fig(fm, **kwargs) for fm in lifm]
        [fm.write_fig() for fm in lifm]
        if 0 :
            if verbose:
                str_figs_bn = ' '.join([fm.bn_fig for fm in lifm])
                message = 'saved image(s) "{}" '.format(str_figs_bn) 
                message  += 'to output directory "{}" '.format(output_dir)
                message += 'using extension(s) "{}"'.format(figure_formats)
                print (message)
    
    def make_fm(self, figure_type='default', **kwargs):
        return self.figtypes[figure_type](**kwargs)
    
    def legend_label(self, i, legend_format = 'ch. {}'):
        return legend_format.format(i)
    
    def visualise_o(self, limf, **kwargs):
        """one file per figure"""
        lifm = []
        for mf in limf:
            fm = self.make_fm(bn_fig='fig_' + mf.bn, **kwargs)
            lifm.append(fm)
            for i, s in enumerate(mf):
                ll = self.legend_label(s.name)
                fm.plot_series(series=s, i=i, legend_label=ll, **kwargs)
            fm.adorn(**kwargs)
        return lifm
    
    def _legend_label_a(self, mf, series):
        return '{}, ch.{}'.format(mf.bn, series.name)
    
    def visualise_a(self, limf, **kwargs):
        """all files in one figure"""
        cp = self.common_prefix(limf)
        fm = self.make_fm(bn_fig='fig_' + cp, **kwargs)
        i = 0
        for mf in limf:
            for series in mf:
                ll = self._legend_label_a(mf=mf, series=series)
                fm.plot_series(fm=fm, series=series, i=i, legend_label=ll, 
                               **kwargs)
                i += 1
        fm.adorn(**kwargs)
        return [fm]
    
    def common_prefix(self, limf):
        cp = os.path.commonprefix([mf.bn for mf in limf]).strip('_')
        if len(cp) < 2:
            cp = 'fig'
        return cp
    
    def visualise_s(self, limf, **kwargs):
        """all files in one figure, concatenating the channels"""
        # Shift
        lastindexes = [mf.dfs().index[-1] for mf in limf]
        cumsums = [sum(lastindexes[:i]) for i in range(len(lastindexes))]
        lidf = [mf.df.shift(delay, freq=1) for mf, delay in zip(limf, cumsums)]
        # Concatenate
        df = pandas.concat(lidf)
        # Visualise
        cp = self.common_prefix(limf)
        fm = self.make_fm(bn_fig='fig_' + cp, **kwargs)
        for i, s in df.iteritems():
            ll = self.legend_label(i)
            fm.plot_series(series=s, i=i, legend_label=ll, **kwargs)
        # Customise plot
        fm.adorn(**kwargs)
        # Return the figure manager
        return [fm]
    
    def visualise(self, limf, figure_mode='a', **kwargs):
        return getattr(self, 'visualise_' + figure_mode)(limf, **kwargs)


class InteractivePlotter(Plotter):
    
    def __init__(self, plab):
        super(InteractivePlotter, self).__init__()
        self.plab = plab
    
    def off_key(self, event):
        if event.key == 'i':
            # Update settings from figure
            self.plab.config_write()
        if event.key == 'd':
            #Update figure from settings
            self.plab.config_load()
        if event.key == 'w':
            self.plab.config_write()
    
    def make_fm(self, **kwargs):
        fm = super(InteractivePlotter, self).make_fm(**kwargs)
        
        # link the figure_items to the PersistLab instance
        self.plab.figure_items = fm.figure_items
        
        # keep a reference to figure_manager for connections
        self.lifm.append(fm) 
        
        # Add some interaction
        fm.figure.canvas.mpl_connect('key_release_event', self.off_key)
        fm.on_key_actions['w'] = fm.write_fig
        fm.on_key_actions['i'] = fm.getp
        fm.off_key_actions['d'] = fm.setp
        fm.help.appendix += '"i" and "d" actions write/read the settings file'
        
        # Return the figure manager
        return fm
    
##    def visualise(self, *args, **kwargs):
    def visualise(self, **kwargs):
        self.lifm = []
##        return super(InteractivePlotter, self).visualise(*args, **kwargs)
        return super(InteractivePlotter, self).visualise(**kwargs)


class PersistLab(object):
    
    """ Data visusalisation and processing with persistence of teh settings
    
    Note: The settings file takes the name of the output directory 
    appended with a '.ini' extension. """
    
    def __init__(self, 
                    # Settings
                    Settings = Settings, 
                    section_params = 'Configuration', 
                    section_figitems = 'figure items', 
                    SettingsManager = persist.SettingsManager, 
                    # Data plotting
                    Plotter=InteractivePlotter, 
##                    figure_items = FIGURE_ITEMS, 
                    # Data processing
                    DataProcessor=measfile.DataProcessor,
                    # Data parsing
                    DataFileParser=measfile.DataFileParser, 
                    # Document publishing
                    Publisher=publishrst.Publisher, 
                    # Other
                    **kwargs):
        # Settings
        self.section_params = section_params
        self.section_figitems = section_figitems
        self.plugins_versions = {}
        self.params = Settings()
        self.sm = SettingsManager(**self.params())
        self.figure_items = {}
        # Publisher
        self.publisher = Publisher()
        # File parser
        self.dataparser = DataFileParser()
        # Data processor
        self.dataproc = DataProcessor()
        # Plotter
        self.plotter = Plotter(plab=self)
##        self.figure_items = figure_items
    
    def config_write(self):
        # Working directory
        self.sm.config['working directory'] = os.getcwd()        
        
        # Section 'figure items'
        self.sm.config[self.section_figitems] = {}
##        fig_items = self.plotter.lifm[0].figure_items
        self.sm.config[self.section_figitems].update(self.figure_items)
        
        # Section 'Parameters'
        sn = self.section_params
        self.sm.fill_section(params=self.params, section_name=sn)
        # Section 'versions'
        section_version = 'versions'
        self.sm.config[section_version] = {}
        pyversion = '.'.join(str(e) for e in sys.version_info[:3])
        self.sm.config[section_version]['python']  = pyversion
        plt_version = pyplot.matplotlib.__version__
        self.sm.config[section_version]['matplotlib']  = plt_version
        self.sm.config[section_version]['pandas']  = pandas.__version__
        self.sm.config[section_version]['configobj']  = configobj.__version__
        self.sm.config[section_version]['persistlab']  = __version__
        # Write to file
        self.sm.write()
    
    def config_load(self, fn=None):
        self.sm.load(fn)
        self.params.update(self.sm.config[self.section_params])
        self.figure_items.update(self.sm.config[self.section_figitems])
    
    def config_setup(self, clargs=None, 
                        config_load_from=0, 
                        output_overwrite=0, 
                        **kwargs):
        if clargs :
            # Check for the 'load settings from file' option
            args = self.args_parser().parse_args(clargs)
            config_load_from = args.config_load_from
        config_load_from and self.config_load(config_load_from)
        
        if clargs:
            # Parse all clargs. If 'config_load_from' was specified,
            # the default values come from this file
            self.args_parser().parse_args(clargs, namespace=self.params)
        else:
            # Update self.params with the kwargs params to give them priority 
            # over the parameters potentially loaded  from a settings file
            self.params.update(kwargs)
        
        # Choose output directory
        if not output_overwrite:
            self.params.output_dir = fned(self.params.output_dir)
        # Update settings manager properties
        self.sm.verbose = self.params.verbose
        self.sm.fn = self.params.output_dir + '.ini'
        
    
    def data_plot(self):
##        lifm = self.plotter.visualise(plab=self, limf=self.limf, 
        lifm = self.plotter.visualise(limf=self.limf, 
##                        figure_items = self.figure_items, 
                        **vars(self.params))
        if self.params.figure_write:
            self.plotter.write_figures(lifm, **vars(self.params))
            libn = [fm.bn_fig for fm in lifm]
            if self.params.publish:
                self.publisher.add_figures(libn, **vars(self.params))
        self.params.figure_show and pyplot.show()
    
    def data_process(self):
        stats_df = self.dataproc.compute(limf=self.limf, **self.params.__dict__)
        u = self.params.publish
        u and self.publisher.add_dataframe(stats_df, **self.params.__dict__)

    def args_parser(self):
        
        """Creates and return a command line arguments parser."""
        
        # Initialise the argument parser
        _str_descr = "Batch data processing with persistence of the settings"
        parser = argparse.ArgumentParser(description = _str_descr, 
                        version=__version__, 
                        conflict_handler='resolve', 
                        # Is this noe the default one?
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        #  POSITIONAL ARGUMENTS : datafiles  #
        parser.add_argument('data_files',
                        nargs='*', 
                        default = self.params.data_files, 
                        type = os.path.relpath, 
                        metavar='FILE',
                        help="data file(s) to be processed.")
        
        #  OPTIONAL ARGUMENTS #
        # General #
        parser.add_argument('-v','--verbose',  
                        default=self.params.verbose, 
                        action='count', 
                        help='verbose.')
        parser.add_argument('-cl', '--config-load-from', 
                        default=self.params.config_load_from, 
                        metavar='FILE', 
                        help="file to load settings from.")
        # Data files #
        parser.add_argument('-df', '--data-format',  
                        choices=self.dataparser.fileformats.keys(),
                        default=self.params.data_format, 
                        help='data file format.')
        parser.add_argument('-n', '--data-channels', 
                        nargs= '+',
                        default=self.params.data_channels, 
                        type=int, 
                        metavar = 'N', 
                        help='channel(s) to plot, "-1" plots all.')
        parser.add_argument('-p', '--data-process',  
##                        choices=self.dataproc.calculators.keys(), 
                        # The choices are not limited here
                        # to be able to accept numpy universal functions,
                        # e.g. numpy.add, ...
                        action = 'store', 
##                        nargs=1, 
                        default=self.params.data_process, 
                        help='data processing type.')
        
        parser.add_argument('-r', '--data-segment-range', 
                        nargs=2,
##                        nargs='*',
                        type=int, 
                        metavar = 'N', 
                        default=self.params.data_segment_range, 
                        help=('segment start and stop, "-1" means all of them.'
                              ' Only valid for multiple segment data file.'))
        
        # Visualisation #
        parser.add_argument('-f', '--figure-plot', 
                            action='store_true', 
                            default=self.params.figure_plot, 
                            help='draw figures')
        parser.add_argument('-s', '--figure-show', 
                        action='store_true', 
                        help='show the matplotlib interface.')
        parser.add_argument('-m', '--figure-mode', 
                        choices=self.plotter.modes,
                        default=self.params.figure_mode, 
                        help=('figure modes. "a": all files in one figure; '
                              '"o": one files in one figure '
                              'and "s": same channels (all files).')
                        )
        
        parser.add_argument('-t', '--figure-type',
                        choices=self.plotter.figtypes.keys(), 
                        default = self.params.figure_type, 
                        help='figure type.', 
                        )
        
        parser.add_argument('-g', '--figure-legend',
                        action='store_false', 
                        help='show legend on figures.')
    
        parser.add_argument('-i', '--figure-formats', 
                        default=self.params.figure_formats,
                        nargs='+', 
                        metavar='F', 
                        help = 'image file formats.')
        
        parser.add_argument('-w', '--figure-write',
                        action='store_true', 
                        help='write figure(s) to image files.')
    
        # Figure lines styles #
        parser.add_argument('-h', '--figure-use-dashes', 
                        action='store_true', 
                        help='use dashes for the lines.')
        parser.add_argument('-l','--figure-use-line-style', 
                        action='store_true', 
                        help="""use matplotlib default line styles 
                        ("-","--", "-.",  and ":")""")
        parser.add_argument('-c','--figure-use-color', 
                            action='store_true', 
                            help='use color for lines.')
        parser.add_argument('-k','--figure-use-markers', 
                        action='store_true', 
                        help='use markers for lines.')
                            #  Change this to "-l" and '--line-style' for line style?
                        # e.g. "-l  cm" would mean use color and markers.
                        # => issue with dashes and mpl default line style, 
                        # that are not possible together...
                        # => issue with 'choices' from args_parse 
                        # that are set to accept only one value... would need something
                        # that accepts a combination of sevral choices
                        #
                        # The action ''append_const''  or 'append' might be useful here to
                        # add lines styles to a container specified by 'dest'
        # Outputs #
        parser.add_argument('-od', '--output-dir', 
                        nargs=1,
                        metavar='DIR', 
                        default = self.params.output_dir, 
                        help='output directory')
        parser.add_argument('-oo', '--output-overwrite', 
                        action='store_true', 
                        help='overwrite the output directory.')
        
        # Document publishing #
        parser.add_argument('-u', '--publish', 
                            action='store_true', 
                            help='publish output document')
        
        parser.add_argument('-uf', '--publish-formats',
                        nargs='+', 
                        choices=self.publisher.formats, 
                        default=self.params.publish_formats, 
                        help='output document formats.', 
                        )
        #
        return parser
    
    def exec_kwargs(self, **kwargs):
        # Arange the parameters    
        self.config_setup(**kwargs)
        # Parse data
        self.limf = self.dataparser.parse_files(**self.params())
        # Process data
        self.params.data_process and self.data_process()
        # Plot
        self.params.figure_plot and self.data_plot()
        # Publish document
        self.params.publish and self.publisher.publish(**self.params())
        # Write config
        self.params.config_write and self.config_write()

    
def persistlab(PLab = PersistLab, **kwargs):
    plab = PLab()
    plab.exec_kwargs(**kwargs)
    return plab
    
# Debug
def clean_output(li_patterns=['output*', 'settings*', 'stats.csv']):
    """Convenience function to clean-up output files and directory"""
    for str_dir in li_patterns:
        for g in glob.glob(str_dir):
            os.path.isdir(g) and shutil.rmtree(g) 
            os.path.isfile(g) and os.remove(g)

def debug():
    
    0 and PersistLab().args_parser().print_help()
    
    import data
    
    clean_output()
    
    persistlab(
                    data_files=data.LI_FLATFILE_ALL,
##                    data_format='flat', 
##                    channels=[0, 1, 3], 
##                data_process='numpy.trapz', 
####                    figure_manager='basic', 
                    figure_plot = 1, 
##                figure_mode='s', 
                    figure_show=1,
                    figure_use_color = 1, 
                    figure_use_markers = 1, 
####                    figure_use_dashes=1, 
####                    figure_use_line_style=1, 
##                figure_write=0, 
##                publish = 0, 
##                publish_formats=[
####                                    'pdf',
##                               'html' 
##                               ], 
####                    publish_base_name = 'publish', 
##                config_write = 0, 
##                verbose=0, 
                )
    clean_output()
    print ('End debug {}'.format(os.path.relpath(__file__)))

if __name__ == "__main__":
    debug()
#

