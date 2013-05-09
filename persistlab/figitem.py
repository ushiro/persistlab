"""
    persistlab.figitem
    ~~~~~~~~~~

    This module provides a matplotlib figure manager
    to deal with the figure elements as dictionnary elements

    :copyright: (c) 2013 by Stephane Henry..
    :license: BSD, see LICENSE for more details.


    Comments:
    ~~~~~~~
    
    Ideally it should be possible to add a figitem element to the figure
    without supplying an initial value, and the value could be fetched 
    from the image with the get() method. 
    It doesn't seem to be happening in every cases, such as tight layout,
    or other elements that can't provide the value from the figure.
"""

import os
import shutil
from collections import OrderedDict

import pandas
from matplotlib import pyplot as plt
from matplotlib.lines import MarkerStyle

class FigureItem:
    
    def __init__(self, fm, str_item):
        self.str_item = str_item
        li_str_item = str_item.split('.')
        self.item = getattr(fm, li_str_item[0])
        self.param = li_str_item[-1]
        if len(li_str_item) == 3:
            self.side = li_str_item[1]
            if self.side == 'x' or self.side == 'y':
                self.item = getattr(self.item, self.side + 'axis')
    
    def set(self, value, **kwargs):
        getattr(self.item, 'set_' + self.param)(value, **kwargs)
    
    def get(self, **kwargs):
        return getattr(self.item, 'get_' + self.param)(**kwargs)
    
    def get_new_value(self, value = 1):
        """Move item {} of value {}"""
##        modulo = self.p_max - self.p_min + 1
##        nv = self.get() - self.p_min + self.p_incr * value 
##        self.set_p(nv % modulo + self.p_min)
        nv = self.get() + value 
        if self.p_min>nv:
           nv = self.p_max
        elif self.p_max<nv:
            nv = self.p_min
        return nv
    
    def move(self, *args, **kwargs):
        self.set(self.get_new_value(*args, **kwargs))
        plt.draw()
    
    def get_new_value_xy(self, value = 1):
        x, y = self.get()
        if self.side == 'x':
            y = y + value
            if self.p_min>y:
               y = self.p_max
            elif self.p_max<y:
                y = self.p_min
        elif self.side == 'y':
            x = x + value
            if self.p_min>x:
               x = self.p_max
            elif self.p_max<x:
                x = self.p_min
        return (x, y)

class AxFormatter(FigureItem):
    
    def __init__(self, *args, **kwargs):
        FigureItem.__init__(self, *args, **kwargs)
        # Set item to formatter
        self.item = self.item.get_major_formatter()


class AxScientific(AxFormatter):
    
    def get(self):
        return self.item._scientific


class AxPowerLimits(AxFormatter):
    
    def get(self):
        return self.item._powerlimits
    

class AxLocator(FigureItem):
    
    def __init__(self, *args, **kwargs):
        FigureItem.__init__(self, *args, **kwargs)
        self.item = self.item.major.locator


class FigureSizeInches(FigureItem):
    
    def set(self, value):
##        FigureItem.set(self, value, **dict(forward=True))
        FigureItem.set(self, value, forward=True)


class LabelPos(FigureItem):
    
    p_min = -0.5
    p_max = 0.5
    
    """Tight layout doesn't seem to take in account when
    the position of the label is modified with this class"""
    
    def set(self, value):
        self.item.set_label_coords(*value)
    
    def get(self):
        return list(self.item.label.get_position())
    
    def get_new_value(self, *args, **kwargs):
        return self.get_new_value_xy(*args, **kwargs)
    

class AxOffset(AxFormatter):
    
    """This doesn't work, offset is overwritten by MPL"""
    
    def set(self,  value):
        getattr(self.item, '_set_' + self.param)(value)


class MaxNLocator(AxLocator):
    
    p_min = 1
    p_max = 12
    
    def set(self, value):
        self.item.set_params(nbins=value)
    
    def get(self):
        return self.item._nbins


class FigureTightLayout(FigureItem):
    
    def set(self, value):
        self._value = value
        self.item.tight_layout(pad=value)
    
    def get(self):
        return self._value


class SubplotAdjust(FigureItem):
    
    def set(self, value):
        di = {self.side:value}
        self.item.subplots_adjust(**di)
    
    def get(self):
        return getattr(self.item.subplotpars,self.side)

class Grid(FigureItem):
    
    def set(self, value):
        self._value = value
        self.item.grid(value)
    
    def get(self):
        return self.item.xaxis._gridOnMajor


class LegendLoc(FigureItem):
    
    p_min = 0
    p_max = 10
    
    def set(self, value):
        self.item._loc = value
    
    def get(self):
        return self.item._loc


class LegendPos(FigureItem):
    
    def __init__(self, *args, **kwargs):
        FigureItem.__init__(self, *args, **kwargs)
        self.param = 'bbox_to_anchor'
    
    def get(self):
        bbox = FigureItem.get(self).bounds
        ar = self.item.parent.transAxes.inverted().transform(bbox[:2])
        return ar


class Action:
    
    def __init__(self, item=None, str_action='move', value=None):
        self.item = item
        self.str_action = str_action
        self.value = value
    
    def __call__(self):
        getattr(self.item, self.str_action)(self.value)
    
    def help_message(self):
        str_help = '{1} {0} of {2}'
        return str_help.format(self.item.str_item,self.str_action,self.value)


class ActionHelp(Action):
    
    def __init__(self, fm):
        Action.__init__(self)
        self.fm = fm
        self.appendix = ''
    
    def help_message(self):
        return "show this message"
    
    def __call__(self, *args):
        """Show interaction help message"""
        print "Keyboard interactions:"
        for k, a in self.fm.on_key_actions.items():
            if hasattr(a, 'help_message'):
                print ' " {} " : {}'.format(k,a.help_message())
            else:
                print ' " {} " : {}'.format(k, self.fm.on_key_actions[k].__doc__)
        for k, a in self.fm.off_key_actions.items():
            print ' " {} " : {}'.format(k, self.fm.off_key_actions[k].__doc__)
        print self.appendix

FIGITEMS = {'size_inches':FigureSizeInches, 
                'scientific':AxScientific, 
                'powerlimits':AxPowerLimits, 
                'useOffset':AxFormatter, 
                'offset':AxOffset, 
                'maxnlocator':MaxNLocator, 
                'tight_layout':FigureTightLayout, 
                'subplot_adjust':SubplotAdjust, 
                'label_pos':LabelPos, 
                'grid':Grid, 
                'legendloc':LegendLoc, 
                'legendpos':LegendPos}

def itemclass(str_item):
    return FIGITEMS.get(str_item.split('.')[-1], FigureItem)

def modulo(i, li):
    return li[i%len(li)]

class FigureManager(object):
    
    def __init__(self, figure=None, 
                    dashes=[(1, 0), 
                                    (9, 3), 
                                    (4, 4), 
                                    [1, 5], 
                                    (4, 5, 1, 5), 
                                    [4,3,1,3, 1, 3], 
                                    [2, 2], 
                                    [3, 12],
                                    [5, 1] , 
                                    [5, 1, 1, 1], ], 
                    line_styles=['-','--',  '-.',  ':'] , 
                    markers=MarkerStyle.filled_markers, 
                    colors=plt.rcParams['axes.color_cycle'][::-1],
                    
                    figure_items = {}, 
                    
                    image_types=['svg'], 
                    output_dir=',', 
                    bn_fig = 'fig', 
                    
                    verbose=0, 
                    
                    **kwargs):
        
        self.verbose=verbose
        
        # Write figure properties
        self.image_types = image_types
        self.output_dir = output_dir
        self.bn_fig = bn_fig
        
        # Lines properties
        self._colors = colors
        self._markers = markers
        self._line_styles = line_styles
        self._dashes = dashes
        
        # Create or attach matplotlib figure
        if not figure:
            self.figure = plt.figure()
            self.add_axis()
        else:
            self.figure = figure
        
        # Figure items
        self.figure_items = figure_items
        
        # Keyboard interaction
        self.on_key_actions = OrderedDict()
        self.figure.canvas.mpl_connect('key_press_event', self.on_key)
        self.off_key_actions = OrderedDict()
        self.figure.canvas.mpl_connect('key_release_event', self.off_key)
        self.help = ActionHelp(fm=self)
        self.on_key_actions['h'] = self.help
    
    # Figure layout
    def add_axis(self):
        """Add an axis and some settings."""
        self.ax = self.figure.add_subplot(1, 1, 1)
    
    # Interaction
    def add_interact(self, key, *args, **kwargs):
        self.on_key_actions[key] = Action(*args, **kwargs)
    
    def on_key(self, event):
        action = self.on_key_actions.get(event.key)
        action and action()
    
    def off_key(self, event):
        action = self.off_key_actions.get(event.key)
        action and action()

    # Data plot
    def plot_series(self, series, i=0, int_ax=0, 
                    legend_label='undefined', 
                    figure_show_legend=1, 
                    figure_use_color=0, 
                    figure_use_markers=0, 
                    figure_use_dashes=0, 
                    figure_use_line_style=1, 
                    **kwargs): 
        """Plots pandas data series.
        
        *args:
            @series : pandas data series
            @i : index for line type, default to {i}
            @legend_label : legend_label, default to {legend_label}
            @figure_show_legend : show legend, default to {figure_show_legend}
            @figure_use_line_style : use matplotlib line style, default to {figure_use_line_style}
            @figure_use_color : use color, default to {figure_use_color}
            @figure_use_markers : legend_label, default to {figure_use_markers}
            @figure_use_dashes :use custom list of dashes, 
        this overwrites use_line_style argument, default to {figure_use_dashes}
        
        **kwargs are passed to the matplotlib plot function 
        by pandas ploting function
        """.format(i=i,
                        legend_label=legend_label, 
                        figure_show_legend=figure_show_legend, 
                        figure_use_line_style=figure_use_line_style, 
                        figure_use_color=figure_use_color, 
                        figure_use_markers=figure_use_markers, 
                        figure_use_dashes=figure_use_dashes)
                        # Can not introspection fill this up programmatically?
        # Choose the subplot
        ax = self.figure.axes[int_ax]
        # Choose the line properties
        col = figure_use_color and modulo(i, self._colors) or 'k'
        m = figure_use_markers and modulo(i, self._markers) or None
        ls = figure_use_line_style and modulo(i, self._line_styles) or '-'
        plt_kwargs = {}
        if figure_use_dashes:
            plt_kwargs['dashes'] = modulo(i, self._dashes)
        # plot line
        lines = series.plot(ax=ax, color=col, linestyle=ls, marker=m, 
                            label=legend_label,  **plt_kwargs)
        # Show/hide the legend
        ax.legend().set_visible(figure_show_legend)
        
        # Quick fix as measfile.XSegFile generates a FixedFormatter
        from matplotlib.ticker import ScalarFormatter
        ax.xaxis.set_major_formatter(ScalarFormatter())
    
    # Figure items
    def print_item_val(self, item):
        print "{} : {}".format(item.str_item, item.get())
    
    def get_item(self, str_item):
        return itemclass(str_item)(self, str_item)
    
    def add_item(self, str_item, value):
        self.figure_items[str_item] = value
        item = self.get_item(str_item)
        item.set(value)
        return item
    
    def setp(self):
        """Set the figure items values from settings """
        [self.add_item(*i) for i in self.figure_items.items()]
        plt.draw()
    
    def getp(self):
        """Update the settings values from the figure"""
        for str_item in self.figure_items.keys():
            item = self.get_item(str_item)
            self.figure_items[str_item] = item.get()

    # Customise
    def adorn(self, **kwargs):
        # figure items are set after plotting data, 
        # as it is required for the legend,
        # and the grid value, 
        # which seems to be set by pandas serires plot  method
        self.setp()
    
    # Write images to file
    def write_fig(self):
        """Write image file(s)"""
        d = self.output_dir
        not os.path.isdir(d) and os.mkdir(d)
        # Update figure settings as some figure items can have changed,
        # e.g. figure_size_inches because of backend
        0 and fm.update()
        
        # Make sure jpg will be produced for extension-less image see below
        raster_format = 'jpg'
        self.image_types = list(set(self.image_types + [raster_format]))
        # Write pictures
        image_bn = os.path.join(self.output_dir, self.bn_fig)
        li_figfn = [image_bn+'.'+ext for ext in self.image_types]
        [self.figure.savefig(fn) for fn in li_figfn]
        
        # copy image to file with no extension,
        # so the html file created from rst recognise the image
        # compiling a tex file will recognise the right image format/extension
        #but direct rst to html conversion doesn't
        #
        # Edit 04/2013 : changed format to raster image as browser
        # doesn't seem to display svg without extension 
        # (as it was believed to do).
        # To display a proper svg. one might have to generate a different
        # rst source with the svg extension, or have a special html header,
        #or, or, or, or who knows?
        shutil.copy(image_bn + '.'+ raster_format, image_bn)
        
        if self.verbose:
            print "written figures to images '{}' with extensions {}".format(
                            image_bn, self.image_types)


def debug():
    import numpy as np
    fm = FigureManager()
    print (FigureManager.plot_series.__doc__)
    x = np.array([23,234]) + 1e5
    line = fm.ax.plot(x, [4e-6, 9e-6], label='line 1')
    fm.legend = fm.ax.legend()
    
    # Legend position/location
    ll = fm.add_item('legend.legendloc', 3)
    fm.add_interact(item=ll, key='4', value=1)
    fm.add_interact(item=ll, key='$', value=-1)
    fm.print_item_val(ll)
    
    # Legend position
    lp = fm.add_item('legend.legendpos', (0.5, 0.5))
    fm.print_item_val(lp)
    
    
    # Grid
    g = fm.add_item('ax.grid', 1)
    fm.print_item_val(g)
    
    
    # Axis Label text
    fm.add_item('ax.y.label_text',  'Y label')
    lt = fm.add_item('ax.xlabel',  'X label')
    fm.print_item_val(lt)
    # not ok,self.ax.xaxis.set_label does something different
    0 and fm.add_item('ax.y.label',  'Y label') 
    
    # Axis label position
    lp = fm.add_item('ax.y.label_pos',  (-0.02, 0.5))
    fm.print_item_val(lp)
    fm.add_interact(item=lp, key='2', value=0.05)
    fm.add_interact(item=lp, key='"', value=-0.05)
    
    
    # Axis limits
    al = fm.add_item('ax.ylim', [4e-6, 10e-6])
    fm.print_item_val(al)
    # not working, self.ax.xaxis.set_lim is not implemented
    0 and fm.add_item('ax.x.lim', [4, 10], )
    
    # Scientific
    s = fm.add_item('ax.y.scientific', 1)
    fm.print_item_val(s)
    
    # Power limits
    pl = fm.add_item('ax.y.powerlimits', (3, 3))
    fm.print_item_val(pl)
    
    # MaxNLocator
    ml = fm.add_item('ax.y.maxnlocator',  5)
    fm.print_item_val(ml)
    fm.add_interact(item=ml, key='1', value=1)
    fm.add_interact(item=ml, key='!', value=-1)
    
    # Set Offset not working
    uo = fm.add_item('ax.x.useOffset', 1)
    fm.print_item_val(uo)
    o = fm.add_item('ax.x.offset', 1e4)
    fm.print_item_val(o)
    
    # Figure size
    fsi = fm.add_item('figure.size_inches', (3, 4))
    fm.print_item_val(fsi)
    
    # Subplot Adjust (is overwritten by tight layout
    sa = fm.add_item('figure.left.subplot_adjust', 0.5)
    fm.print_item_val(sa)
    
    # Tight layout
    tl = fm.add_item('figure.tight_layout', 0)
    fm.print_item_val(tl)
    
    
    # savefig/show interface
    fm.figure.savefig('test.png')
    1 and plt.show()

if __name__ == '__main__':
    debug()
    print "end debug {}".format(__file__)
