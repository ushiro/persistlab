#!/usr/bin/env python

"""
    persistlab.persistlab
    ~~~~~~~~~~~~~

    Some reStructuredText related routines

    :copyright: (c) 2013 Stephane Henry.
    :license: BSD, see LICENSE for more details.

"""
from __future__ import print_function

import os
import sys

try:
    # Rubber or docutils related stuff?
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass
from docutils.core import publish_file

sys.path.append("/usr/share/rubber")
from rubber.cmdline import Main as RubberMain

def rstfig(bnfig):
    """Make a reST string with a figure basename"""
    return """.. figure:: {0}
  
   {0}""".format(bnfig)

def str_rstfigs(libnfig):
    return os.linesep.join([rstfig(bn) for bn in libnfig]+[''])
    
def rst_listfig(libnfig, fnrst='output.rst'):
    """Make rst file with list of figures."""
    # rst text
    str_rst = str_rstfigs(libnfig)
    # write to text file
    with open(fnrst, 'w') as f:
        f.write(str_rst)
    print ("output document written at {}".format(fnrst))
    
def several_rst_fig(lifigfn):
        return '{0}{0}'.format(os.linesep).join([rstfig(i) for i in lifigfn])

# rst file convertion
def rst2html(fn_rst):
    """Create latex file with docutils"""
    fn_html = os.path.splitext(fn_rst)[0] + '.html'
    with open(fn_rst) as foi:
        with open(fn_html, 'w') as foo:
            t = publish_file(source = foi, destination=foo, writer_name='html')
    return fn_html

def rst2latex(fn_rst):
    """Create latex file with docutils"""
    fn_tex = os.path.splitext(fn_rst)[0] + '.tex'
    with open(fn_rst) as foi:
        with open(fn_tex, 'w') as foo:
            t = publish_file(source = foi, destination=foo, writer_name='latex')
    return fn_tex

def latex2dvi2ps2pdf(fn_tex):
    """Convert to pdf with rubber"""
    # the working directory is changed here,
    # to simplify the handling of picture pathes 
    cw = os.getcwd()
    d, n = os.path.split(fn_tex)
    if d:
        os.chdir(d)
    try:
        # From rubber man page:
        """
       -d, --pdf
              Produce PDF  output.   When  this  option
              comes  after  --ps  (for  instance in the
              form -pd) it is a synonym for  -o ps2pdf,
              otherwise  it acts as -m pdftex, in order
              to use pdfLaTeX instead of LaTeX.

       -p, --ps
              Process the DVI produced by  the  process
              through  dvips(1) to produce a PostScript
              document.  This option is a  synonym  for
              -o dvips, it cannot come after --pdf.
        
       -q, --quiet
              Decrease  the  verbosity  level.  This is
              the reverse of -v.

        """
        RubberMain()(['--quiet','-pd', n])
    except:
        print ( "failed latex 2 dvi 2 ps 2 latex, trying pdflatex")
        try:
            RubberMain()([
                            # quiet
                            '-q', 
                            # pdf
                            '-d', 
                            #source
                            n, 
                            ])
        except:
            print ("Failed to produce pdf output")
    os.chdir(cw)

# 2 ways of producing pdf: through latex chain or with rst2pdf module
def rst2pdf(fn_rst):
    """Use latex chain to produce pdf document from rst"""
    fn_tex = rst2latex(fn_rst)
    latex2dvi2ps2pdf(fn_tex)

def rst2pdf_nops():
    """Use rst2pdf python package to directly produce pdf document from rst"""
    from rst2pdf import createpdf
    createpdf.main(['rst.rst'])

class Publisher:
    
    def __init__(self):
        self.formats = ['rst', 'pdf', 'html']
        self._str_csv_table = """.. csv-table:: {0}
   :header-rows: 1
   :stub-columns: 1
   :file: {0}"""
        self.str_rst = ''
    
    def publish_rst(self, fn_rst):
        with open (fn_rst, 'w') as f:
            f.write(self.str_rst)
    
    def publish(self, publish_formats=['rst'], output_dir='', 
                publish_base_name='', verbose=0, **kwargs):
        not os.path.isdir(output_dir) and os.mkdir(output_dir)
        fn_rst = os.path.join(output_dir, publish_base_name + '.rst')
        publish_rst = any([x in ['html','rst','pdf'] for x in publish_formats])
        publish_rst and self.publish_rst(fn_rst)
        'pdf' in publish_formats and rst2pdf(fn_rst)
        'html' in publish_formats and rst2html(fn_rst)
        if verbose:
            f = ', '.join(publish_formats)
            print ('Written output document to format(s) "{}"'.format(f))

    def add_figures(self, lifigbn=[], output_dir='',verbose=0, **kwargs):
        str_figs = str_rstfigs(libnfig=lifigbn)
        self.str_rst += str_figs
        verbose and print ('added figures to rst string')
    
    def add_dataframe(self, df_stats, output_dir='', 
                    data_process_fn='dataframe.csv', 
                    output_float_format='%.2e', 
                    verbose=0, **kwargs):
        """write pandas dataframe to csv file and add entry to the rst text
        
        the unicode character 'U+2001' can allow to align the values in table
        """
        not os.path.isdir(output_dir) and os.mkdir(output_dir)
        of = os.path.join(output_dir, data_process_fn)
        df_stats.to_csv(of, float_format=output_float_format)
        verbose and print ('written calculations to "{}"'.format(of))
        
        str_csv_table = self._str_csv_table.format(data_process_fn)
        self.str_rst += str_csv_table + os.linesep + os.linesep
        verbose and print ('added csv-table entry to rst string')

# DEBUG
if __name__ == '__main__':
    print (rst2pdf(fn_rst))
    print ('end')
#

