#!/usr/bin/env python3
"""
Created on Fri May 20 13:05:03 2022

@author: cdesbois

plot functions
"""
import logging
import os
from typing import Any, Optional

# import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import dates as mdates

# matplotlib.use("QT5agg")
# matplotlib.use("MacOsX")


def update_pltparams() -> None:
    """Update the matplotlib rcParams."""
    fontsize = "medium"  # large, medium
    params = {
        "font.sans-serif": ["Arial"],
        "font.size": 12,
        "legend.fontsize": fontsize,
        "figure.figsize": (12, 3.1),
        "axes.labelsize": fontsize,
        "axes.titlesize": fontsize,
        "xtick.labelsize": fontsize,
        "ytick.labelsize": fontsize,
        "axes.xmargin": 0,
    }
    plt.rcParams.update(params)
    plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces
    logging.info("pfunc.update_pltparams: updated the matplotlib rcParams (plot_func)")
    # logging.warning(f"{params}")


def empty_data_fig(mes: str = "") -> plt.Figure:
    """
    Generate an empty figure message for empty/missing data.

    Parameters
    ----------
    mes : str, optional (default is None)
        the message to display.

    Returns
    -------
    fig : plt.Figure
        an empty figure.

    """
    fig = plt.figure()
    fig.text(
        0.5,
        0.5,
        mes,
        horizontalalignment="center",
        fontsize="x-large",
        verticalalignment="center",
    )
    return fig


def restrict_trenddf(df: pd.DataFrame, parm: dict["str", Any]) -> pd.DataFrame:
    """
    Change index and restrict the trend dataframe in time.

    Parameters
    ----------
    df : pd.DataFrame
        the data.
    parm : dict["str", Any]
        a dictionary with {dtime:bool, xmin, and xmax}.

    Returns
    -------
    toplot_df : pd.DataFrame
        the dataframe with datetime or elapsed time index,
        limited between xmin and xmax (if provided).

    """
    # xlims = (parm.get("xmin", None), parm.get("xmax", None))
    # unit = parm.get("unit", "")
    dtime = parm.get("dtime", False)
    # global timeUnit
    if dtime:
        timebase = "dtime"
        parm["unit"] = "dtime"
    else:
        timebase = "etimemin"
        parm["unit"] = "min"
    if df.index.duplicated().any():
        logging.critical("duplicated values in the index, didn't change the index")
        toplot_df = df
    else:
        toplot_df = df.set_index(timebase).copy()
        xmin = parm.get("xmin")
        if xmin is None:
            xmin = toplot_df.index.min()
        xmax = parm.get("xmax")
        if xmax is None:
            xmax = toplot_df.index.max()
        toplot_df = toplot_df.loc[xmin:xmax]
    return toplot_df


def add_baseline(fig: plt.figure, param: Optional[dict[str, Any]] = None) -> None:
    """Annotate the base of the plot."""
    if param is None:
        param = {}
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, param.get("file", ""), ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()


# ------------------------------------------------------
def remove_outliers(
    datadf: pd.DataFrame, key: str, limits: Optional[dict[str, tuple[Any, Any]]] = None
) -> pd.Series:
    """
    Remove outliers.

    Parameters
    ----------
    datadf : pd.DataFrame
        the data.
    key : str
        a column label to extract the trace.
    limits : dict, optional
        {limLow: val, limHigh:val} (default is None).

    Returns
    -------
    ser : pandas.Series
        data without the outliers.
    """
    if limits is None:
        limits = {
            "co2exp": (20, 80),
            "aaExp": (0.2, 3.5),
            "ip1m": (15, 160),
            "hr": (10, 100),
        }

    if key not in datadf.columns:
        logging.warning("%s is not present in the data", key)
        return pd.Series()

    if key not in limits:
        logging.warning("%s limits are not defined, min & max will be used", key)
        logging.warning("add new limits to pfunc.remove_outliers")
    ser = datadf[key].copy()
    lims = limits.get(key, (ser.min(), ser.max()))
    ser[~ser.between(lims[0], lims[1])] = np.nan
    ser = ser.dropna()
    return ser


def color_axis(ax0: plt.Axes, spine: str = "bottom", color: str = "r") -> None:
    """
    Change the color of the label & tick & spine.

    Parameters
    ----------
    ax : plt.Axes
        the axis to work on.
    spine : str, optional (default is "bottom")
        optional location in ['bottom', 'left', 'top', 'right'] .
    color : str, optional (default is "r")
        the color to use.

    Returns
    -------
    None.
    """
    ax0.spines[spine].set_color(color)
    if spine == "bottom":
        ax0.xaxis.label.set_color(color)
        ax0.tick_params(axis="x", colors=color)
    elif spine in ["left", "right"]:
        ax0.yaxis.label.set_color(color)
        ax0.tick_params(axis="y", colors=color)


def append_loc_to_fig(
    ax0: plt.Axes, dt_list: list[Any], label: str = "g"
) -> dict[int, float]:
    """
    Append vertical lines to indicate a time location 'for eg: arterial blood gas'.

    Parameters
    ----------
    ax0 : plt.Axes
        the axis to add on.
    dt_list : list
        list of datetime values.
    label : str, optional (default is 'g')
        a key to add to the label.

    Returns
    -------
    dict
        a dictionary containing the locations.
    """
    num_times = mdates.date2num(dt_list)
    res = {}
    for i, num_time in enumerate(num_times):
        txt = label + str(i + 1)
        ax0.axvline(num_time, color="tab:blue")
        ax0.text(num_time, ax0.get_ylim()[1], txt, color="tab:blue")
        res[i] = num_time
    return res


def save_graph(
    path: str, ext: str = "png", close: bool = True, verbose: bool = True
) -> None:
    """
    Save a figure from pyplot.

    Parameters
    ----------
    path : str
        The path (and filename, without the extension) to save the
        figure to.
    ext : str, optional (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.
    close : bool, optional (default=True)
        Whether to close the figure after saving.  If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.
    verbose : bool, optional (default=True)
        Whether to logging.warning information about when and where the image
        has been saved.

    Returns
    -------
    None.
    """
    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    # filename = "%s.%s" % (os.path.split(path)[1], ext)
    filename = ".".join([os.path.split(path)[1], ext])
    if directory == "":
        directory = "."
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    # The final path to save to
    savepath = os.path.join(directory, filename)
    if verbose:
        logging.warning("Saving figure to %s", savepath)
    # Actually save the figure
    plt.savefig(savepath)
    # Close it
    if close:
        plt.close()
    if verbose:
        print("Done")
