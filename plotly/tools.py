# -*- coding: utf-8 -*-

"""
tools
=====

Functions that USERS will possibly want access to.

"""
import os.path
from . import graph_objs
from . import matplotlylib
from . import utils
from . import exceptions

PLOTLY_DIR = os.path.join(os.path.expanduser("~"), ".plotly")
CREDENTIALS_FILE = os.path.join(PLOTLY_DIR, ".credentials")
PLOT_OPTIONS_FILE = os.path.join(PLOTLY_DIR, ".plot_options")
THEMES_FILE = os.path.join(PLOTLY_DIR, ".themes")

_DEFAULT_PLOT_OPTIONS = dict(
    filename="plot from API",
    fileopt="new",
    world_readable=True,
    auto_open=True)


def ensure_local_plotly_files_exist():
    if not os.path.isdir(PLOTLY_DIR):
        os.mkdir(PLOTLY_DIR)
    for filename in [CREDENTIALS_FILE, PLOT_OPTIONS_FILE, THEMES_FILE]:
        if not os.path.exists(filename):
            f = open(filename, "w")
            f.close()


### config tools ###

def save_plot_options_file(filename="", fileopt="",
                      world_readable=None, auto_open=None):
    """Set the keyword-value pairs in `~/.plotly_plot_options`.
        TODO: the kwarg defaults are confusing - maybe should be left as a kwargs
        TODO: should this be hiddenz?
    """
    ensure_local_plotly_files_exist()
    plot_options = get_plot_options_file()
    if (not plot_options and
        (filename or fileopt or world_readable is not None or
         auto_open is not None)):
        plot_options = {}
    if filename:
        plot_options['filename'] = filename
    if fileopt:
        plot_options['fileopt'] = fileopt
    if world_readable is not None:
        plot_options['world_readable'] = world_readable
    if auto_open is not None:
        plot_options['auto_open'] = auto_open
    utils.save_json(PLOT_OPTIONS_FILE, plot_options)


def get_plot_options_file(*args):
    """Return specified args from `~/.plotly_plot_options`. as dict.

    Returns all if no arguments are specified.

    Example:
        get_plot_options_file('username', 'api_key')

    """
    ensure_local_plotly_files_exist()
    options = utils.load_json(PLOT_OPTIONS_FILE, *args)
    if len(options):
        return {str(key): val for key, val in options.items()}
    else:
        return {}


def show_plot_options_file(*args):
    """Print specified kwargs from `~/.plotly_plot_options`.

    Prints all if no keyword arguments are specified.

    """
    ensure_local_plotly_files_exist()
    plot_options = get_plot_options_file(*args)
    if len(args):
        print "The specified keys from your plot options file:\n"
    else:
        print "Your plot options file:\n"
    for key, val in plot_options.items():
        print "\t{}: {}".format(key, val).expandtabs()


### credentials tools ###

def set_credentials_file(username="", api_key="", stream_ids=()):
    """Set the keyword-value pairs in `~/.plotly_credentials`.

    """
    ensure_local_plotly_files_exist()
    credentials = get_credentials_file()
    if not credentials and (username or api_key or stream_ids):
        credentials = {}
    if username:
        credentials['username'] = username
    if api_key:
        credentials['api_key'] = api_key
    if stream_ids:
        credentials['stream_ids'] = stream_ids
    utils.save_json(CREDENTIALS_FILE, credentials)


def get_credentials_file(*args):
    """Return specified args from `~/.plotly_credentials`. as dict.

    Returns all if no arguments are specified.

    Example:
        get_credentials_file('username')

    """
    ensure_local_plotly_files_exist()
    return utils.load_json(CREDENTIALS_FILE, *args)


def show_credentials_file(*args):
    """Print specified kwargs from `~/.plotly_credentials`.

    Prints all if no keyword arguments are specified.

    """
    ensure_local_plotly_files_exist()
    credentials = get_credentials_file(*args)
    if len(args):
        print "The specified keys from your credentials file:\n"
    else:
        print "Your credentials file:\n"
    for key, val in credentials.items():
        print "\t{}: {}".format(key, val).expandtabs()


### embed tools ###

def get_embed(username, plot_id, width="100%", height=525):
    padding = 25
    if isinstance(width, (int, long)):
        s = ("<iframe id=\"igraph\" scrolling=\"no\" seamless=\"seamless\" "
             "src=\"https://plot.ly/"
             "~{username}/{plot_id}/{plot_width}/{plot_height}\" "
             "height=\"{iframe_height}\" width=\"{iframe_width}\">"
             "</iframe>").format(
            username=username, plot_id=plot_id,
            plot_width=width-padding, plot_height=height-padding,
            iframe_height=height, iframe_width=width)
    else:
        s = ("<iframe id=\"igraph\" scrolling=\"no\" seamless=\"seamless\" "
             "src=\"https://plot.ly/"
             "~{username}/{plot_id}\" "
             "height=\"{iframe_height}\" width=\"{iframe_width}\">"
             "</iframe>").format(
            username=username, plot_id=plot_id,
            iframe_height=height, iframe_width=width)

    return s


def embed(username, plot_id, width="100%", height=525):
    s = get_embed(username, plot_id, width, height)
    try:
        # see if we are in the SageMath Cloud
        from sage_salvus import html
        return html(s, hide=False)
    except:
        pass
    try:
        from IPython.display import HTML
        return HTML(s)
    except:
        return s


### mpl-related tools ###

def mpl_to_plotly(fig, resize=False, strip_style=False, verbose=False):
    """Convert a matplotlib figure to plotly dictionary and send.

    All available information about matplotlib visualizations are stored
    within a matplotlib.figure.Figure object. You can create a plot in python
    using matplotlib, store the figure object, and then pass this object to
    the fig_to_plotly function. In the background, mplexporter is used to
    crawl through the mpl figure object for appropriate information. This
    information is then systematically sent to the PlotlyRenderer which
    creates the JSON structure used to make plotly visualizations. Finally,
    these dictionaries are sent to plotly and your browser should open up a
    new tab for viewing! Optionally, if you're working in IPython, you can
    set notebook=True and the PlotlyRenderer will call plotly.iplot instead
    of plotly.plot to have the graph appear directly in the IPython notebook.

    Note, this function gives the user access to a simple, one-line way to
    render an mpl figure in plotly. If you need to trouble shoot, you can do
    this step manually by NOT running this fuction and entereing the following:

    ============================================================================
    from mplexporter import Exporter
    from mplexporter.renderers import PlotlyRenderer

    # create an mpl figure and store it under a varialble 'fig'

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    ============================================================================

    You can then inspect the JSON structures by accessing these:

    renderer.layout -- a plotly layout dictionary
    renderer.data -- a list of plotly data dictionaries

    Positional arguments:
    fig -- a matplotlib figure object
    username -- a valid plotly username **
    api_key -- a valid api_key for the above username **
    notebook -- an option for use with an IPython notebook

    ** Don't have a username/api_key? Try looking here:
    https://plot.ly/plot

    ** Forgot your api_key? Try signing in and looking here:
    https://plot.ly/api/python/getting-started

    """
    renderer = matplotlylib.PlotlyRenderer()
    matplotlylib.Exporter(renderer).run(fig)
    if resize:
        renderer.resize()
    if strip_style:
        renderer.strip_style()
    if verbose:
        print renderer.msg
    return renderer.plotly_fig


### graph_objs related tools ###

# TODO: Scale spacing based on number of plots and figure size
def get_subplots(rows=1, columns=1, horizontal_spacing=0.1,
                 vertical_spacing=0.15, print_grid=False):
    """Return a dictionary instance with the subplots set in 'layout'.

    key (types, default=default):
        description.

    rows (int, default=1):
        Number of rows, evenly spaced vertically on the figure.

    columns (int, default=1):
        Number of columns, evenly spaced horizontally on the figure.

    horizontal_spacing (float in [0,1], default=0.1):
        Space between subplot columns. Applied to all columns.

    vertical_spacing (float in [0,1], default=0.05):
        Space between subplot rows. Applied to all rows.

    print_grid (True | False, default=False):
        If True, prints a tab-delimited string representation of your plot grid.

    """
    fig = dict(layout=graph_objs.Layout())  # will return this at the end
    plot_width = (1 - horizontal_spacing * (columns - 1)) / columns
    plot_height = (1 - vertical_spacing * (rows - 1)) / rows
    plot_num = 0
    for rrr in range(rows):
        for ccc in range(columns):
            xaxis_name = 'xaxis{}'.format(plot_num + 1)
            x_anchor = 'y{}'.format(plot_num + 1)
            x_start = (plot_width + horizontal_spacing) * ccc
            x_end = x_start + plot_width

            yaxis_name = 'yaxis{}'.format(plot_num + 1)
            y_anchor = 'x{}'.format(plot_num + 1)
            y_start = (plot_height + vertical_spacing) * rrr
            y_end = y_start + plot_height

            xaxis = graph_objs.XAxis(domain=[x_start, x_end], anchor=x_anchor)
            fig['layout'][xaxis_name] = xaxis
            yaxis = graph_objs.YAxis(domain=[y_start, y_end], anchor=y_anchor)
            fig['layout'][yaxis_name] = yaxis
            plot_num += 1
    if print_grid:
        print "This is the format of your plot grid!"
        grid_string = ""
        plot = 1
        for rrr in range(rows):
            grid_line = ""
            for ccc in range(columns):
                grid_line += "[{}]\t".format(plot)
                plot += 1
            grid_string = grid_line + '\n' + grid_string
        print grid_string
    return graph_objs.Figure(fig)  # forces us to validate what we just did...


def get_valid_graph_obj(obj, obj_type=None):
    try:
        new_obj = graph_objs.STRING_TO_CLASS[obj.__class__.__name__.lower]()
    except KeyError:
        try:
            new_obj = graph_objs.STRING_TO_CLASS[obj_type]()
        except KeyError:
            raise exceptions.PlotlyError("'obj' nor 'obj_type' are "
                                         "recognizable graph_objs.")  # TODO
    if isinstance(new_obj, list):
        new_obj += obj
    else:
        for key, val in obj.items():
            new_obj[key] = val
    new_obj.force_clean()
    return new_obj