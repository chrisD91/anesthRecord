#!/usr/bin/env python3

"""
Created on Tue Apr 19 09:08:56 2016
@author: cdesbois

collection of functions to plot the trend data

____
"""
import logging
from typing import Any, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

import anesplot.plot.t_axplot as tap
from anesplot.plot import pfunc

# from . import pfunc
# from . import t_axplot as tap

# import pfunc

logging.info("trend_plot_loaded")

pfunc.update_pltparams()
# pfunc.update_pltparams()


# %%
def plot_header(
    header: dict[str, Any], param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot the header of the file.

    Parameters
    ----------
    descr : dict
        header of the recording.
    param : dict, optional (default is None)
        dictionary of parameters.

    Returns
    -------
    fig : plt.Figure
        plot of the header.
    """
    if not header:
        logging.warning("empty header")
        return plt.figure()
    if param is None:
        param = {"save": False, "file": ""}
    hcell = 2
    wcell = 2
    wpad = 0.2
    #    nbrows = 11
    nbcol = 2
    hpad = 0.1
    txt = []
    for key, val in header.items():
        if key == "Weight":
            val *= 10
        txt.append([key, val])
    # ['Age', 'Sex', 'Weight', 'Version', 'Date', 'Patient Name', 'Sampling Rate',
    # 'Height', 'Patient ID', 'Equipment', 'Procedure']
    fig = plt.figure(figsize=(nbcol * hcell + hpad, nbcol * wcell + wpad))
    fig.__name__ = "header"
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table = ax.table(cellText=txt, loc="center", fontsize=18, bbox=[0, 0, 1, 1])
    # table.auto_set_font_size(False)
    table.set_fontsize(10)
    # table.set_zorder(10)
    for spineval in ax.spines.values():
        spineval.set_color("w")
        spineval.set_zorder(0)
    # annotations
    pfunc.add_baseline(fig, param)
    # pfunc.add_baseline(fig, param)
    return fig


# ------------------------------------------------------
def hist_cardio(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Mean arterial pressure histogramme using matplotlib.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded trends data (keys used : 'ip1m' and 'hr),.
    param : dict, optional (default is None).
        parameters (save=bolean, 'path': path to directory).

    Returns
    -------
    plt.Figure
    """
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        # return plt.figure()
        return fig
    if param is None:
        param = {}
    keys = {"ip1m", "hr"}
    if not keys.issubset(set(datadf.columns)):
        txt = f"{set(keys) - set(datadf.columns)} is/are missing in the data"
        logging.warning(txt)
        # return plt.figure()
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    fig.__name__ = "hist_cardio"
    # arterial pressure
    ax = axes[0]
    ser = pfunc.remove_outliers(datadf, "ip1m")
    tap.axplot_hist(ax, ser, key="ip1")
    # heart rate
    ax = axes[1]
    ser = pfunc.remove_outliers(datadf, "hr")
    tap.axplot_hist(ax, ser, key="hr")

    for ax in axes:
        # call
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def hist_co2aa(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot end tidal CO2 and anesthetic agent (aa) histogram.

    (NB CO2 should have been converted from % to mmHg)

    Parameters
    ----------
    data : pd.DataFrame
        the recorded data.
    param : dict, optional (default is None).
        parameters.

    Returns
    -------
    matplotlib.pyplot.Figure.
    """
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        # return plt.figure()
        return fig
    if param is None:
        param = {}
    keys = {"co2exp", "aaExp"}
    if not keys.issubset(set(datadf.columns)):
        txt = f"{set(keys) - set(datadf.columns)} is/are missing in the data"
        logging.warning(txt)
        # return plt.figure()
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig
    # aa
    try:
        agent = datadf.aaLabel.value_counts().index[0]
    except AttributeError:
        agent = "aa"
    if agent == "" or agent == "0":
        agent = "aa"
    # TODO fix this for taph recording
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    fig.__name__ = "hist_co2_aa"
    # co2
    ax = axes[0]
    ser = pfunc.remove_outliers(datadf, "co2exp")
    tap.axplot_hist(ax, ser, key="co2")
    # iso
    ax = axes[1]
    ser = pfunc.remove_outliers(datadf, "aaExp")
    tap.axplot_hist(ax, ser, key=agent)
    median = datadf.aaExp.median()
    ax.text(0, 1, f"{median=:.2f}", ha="left", va="top", transform=ax.transAxes)

    for ax in axes:
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
        # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def plot_cardiovasc(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Cardiovascular plot.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded trends data, columns used :['ip1s', 'ip1m', 'ip1d', 'hr'].
    param : dict, optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                         dtime = boolean for time display in HH:MM format)

    Returns
    -------
    matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}  # type : dict[str, Any]

    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    cardiac_items = {"ip1m", "ip1d", "ip1s", "hr"}
    if not cardiac_items.issubset(set(datadf.columns)):
        diff = cardiac_items - set(datadf.columns)
        logging.warning("unable to perform the cardiovacular plot")
        txt = f"{diff} are not present in the data"
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    # restrict and timeUnit
    pressuredf = pfunc.restrict_trenddf(datadf, param)
    pressuredf = pressuredf[list(cardiac_items)]

    fig = plt.figure()
    fig.__name__ = "cardiovascular"
    ax_l = fig.add_subplot(111)
    tap.axplot_hr(ax_l, pressuredf)

    ax_r = ax_l.twinx()
    tap.axplot_arterialpressure(ax_r, pressuredf)

    ax_l.spines["right"].set_visible(False)
    ax_r.spines["left"].set_visible(False)
    # if timebase == "datetime":
    if pressuredf.index.dtype == "<M8[ns]":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    pfunc.color_axis(ax_l, "left", "tab:grey")  # call
    pfunc.color_axis(ax_r, "right", "tab:red")  # call
    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    xlims = (param.get("xmin", None), param.get("xmax", None))
    if all(xlims):
        ax_r.set_xlim(*xlims)
    return fig


# ------------------------------------------------------
def plot_cardiovasc_p1p2(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Cardiovascular plot with central venous pressure (p2).

    Parameters
    ----------
    data : pd.DataFrame
        the trends recorded data
            columns used :['ip1s', 'ip1m', 'ip1d', 'hr', 'ip2s', 'ip2m', 'ip2d'].
    param : dict, optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
            dtime = boolean for time display in HH:MM format).

    Returns
    -------
    TYPE
        matplotlib.pyplot.Figure.
    """
    if param is None:
        param = {}  # type : dict[str, Any]
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    cardiac_items = {"ip1m", "ip1d", "ip1s", "hr", "ip2s", "ip2d", "ip2m"}
    cardiac_present = cardiac_items & set(datadf.columns)
    if not cardiac_present:
        # if not cardiac_items.issubset(set(datadf.columns)):
        diff = cardiac_items - set(datadf.columns)
        txt = f"{diff} are not present in the data"
        logging.warning("unable to perform the cardiovac_p1p2 plot")
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    # restrict and timeUnit
    pressuredf = pfunc.restrict_trenddf(datadf, param)
    pressuredf = pressuredf[list(cardiac_present)]

    fig, axes = plt.subplots(figsize=(12, 6), ncols=1, nrows=2, sharex=True)
    fig.__name__ = "cardiovascular_p1p2"
    ax_l = axes[0]
    ax_r = ax_l.twinx()
    # heart rate  plotted first (background)
    tap.axplot_hr(ax_r, pressuredf)
    pfunc.color_axis(ax_r, "right", "tab:grey")  # call
    tap.axplot_arterialpressure(ax_l, pressuredf)
    pfunc.color_axis(ax_l, "left", "tab:red")
    # venuous pressure
    ax = axes[1]
    tap.axplot_arterialpressure(ax, pressuredf, key="ip2")
    pfunc.color_axis(ax, "left", "tab:blue")  # call
    if pressuredf.index.dtype == "<M8[ns]":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    for i, ax in enumerate(fig.get_axes()):
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.spines["top"].set_visible(False)
        if i == 0:
            ax.spines["right"].set_visible(False)
        else:
            ax_r.spines["left"].set_visible(False)
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def plot_co2aa(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot CO2/anestheticAgent over time.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded data. Columns used :['ip1s', 'ip1m', 'ip1d', 'hr'].
    param : dict, optional (default is None).
        dict(save: boolean, path['save'], xmin, xmax, unit,
             dtime = boolean for time display in HH:MM format)

    Returns
    -------
    matplotlib.pyplot.Figure
    """
    #    breakpoint()
    if param is None:
        param = {}  # type : dict[str, Any]
    if datadf.empty or len(datadf) < 5:
        logging.warning("empty dataframe")
        txt = "empty dataframe"
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    plot_items = {"co2insp", "co2exp", "aaInsp", "aaExp"}
    if not plot_items.issubset(set(datadf.columns)):
        diff = plot_items - set(datadf.columns)
        logging.warning("unable to perform the cardiovacular plot")
        txt = f"{diff} are not present in the data"
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    # restrict and timeUnit
    plot_df = pfunc.restrict_trenddf(datadf, param)
    plot_df = plot_df[list(plot_items)]

    fig = plt.figure()
    fig.__name__ = "co2_aa"
    # co2
    ax_l = fig.add_subplot(111)
    tap.axplot_co2(ax_l, plot_df)
    pfunc.color_axis(ax_l, "left", "tab:blue")
    # aa
    try:
        aa = datadf.aaLabel.value_counts().index[0]
    except AttributeError:
        aa = "aa"
    # TODO fix this for taph recording
    ax_r = ax_l.twinx()
    tap.axplot_aa(ax_r, plot_df, key=aa)
    pfunc.color_axis(ax_r, "right", "tab:grey")

    ax_l.spines["right"].set_visible(False)
    ax_r.spines["left"].set_visible(False)
    if plot_df.index.dtype == "<M8[ns]":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in fig.get_axes():
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.spines["top"].set_visible(False)

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def plot_co2o2(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Respiratory plot : CO2 and Iso.

    Parameters
    ----------
    data : pd.DataFrame
        recorded trends data columns used :["co2insp", "co2exp", "o2insp", "o2exp"].
    param : dict, optional(default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    TYPE
        maplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    plot_items = {"co2insp", "co2exp", "o2insp", "o2exp"}
    if not plot_items.issubset(set(datadf.columns)):
        diff = plot_items - set(datadf.columns)
        txt = f"{diff} are not present in the data)"
        logging.warning("unable to perform the cardiovacular plot")
        logging.warning(txt)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    # restrict and timeUnit
    plot_df = pfunc.restrict_trenddf(datadf, param)
    plot_df = plot_df[list(plot_items)]

    fig = plt.figure()
    fig.__name__ = "co2o2"
    # co2
    ax_l = fig.add_subplot(111)
    tap.axplot_co2(ax_l, plot_df)
    pfunc.color_axis(ax_l, "left", "tab:blue")
    # o2
    ax_r = ax_l.twinx()
    tap.axplot_o2(ax_r, plot_df)
    pfunc.color_axis(ax_r, "right", "tab:green")

    if plot_df.index.dtype == "<M8[ns]":
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_r.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in [ax_l, ax_r]:
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def plot_ventil(
    datadf: pd.DataFrame, param: Optional[dict["str", Any]] = None
) -> plt.Figure:
    """
    Plot ventilation.

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded trend data
        columns used : (tvInsp, pPeak, pPlat, peep, minVexp, co2RR, co2exp )
    param : dict, optional (default is None)
        param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        logging.warning("txt")
        fig = pfunc.empty_data_fig(txt)  # error message fig
        pfunc.add_baseline(fig, param)
        return fig

    plot_df = pfunc.restrict_trenddf(datadf, param)

    fig = plt.figure(figsize=(12, 5))
    fig.__name__ = "ventil"

    ax1 = fig.add_subplot(211)
    tap.axplot_ventiltidal(ax1, plot_df)
    pfunc.color_axis(ax1, "left", "tab:orange")  # call

    ax1_r = ax1.twinx()
    tap.axplot_ventilpressure(ax1_r, plot_df)
    pfunc.color_axis(ax1_r, "right", "tab:red")  # call

    ax2 = fig.add_subplot(212, sharex=ax1)
    tap.axplot_minvol_rr(ax2, plot_df)
    pfunc.color_axis(ax2, "left", "tab:grey")  # call

    ax2_r = ax2.twinx()
    tap.axplot_co2(ax2_r, plot_df)
    pfunc.color_axis(ax2_r, "right", "tab:blue")  # call

    ax1_r.set_ylim(0, 50)

    for ax in [ax1, ax1_r, ax2, ax2_r]:
        # if dtime:
        if plot_df.index.dtype == "<M8[ns]":
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)
        else:
            ax.set_xlabel("etime (min)")
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        # ax.set_xlim(*xlims)
        # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def plot_recrut(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Display a recrut manoeuver.

    Parameters
    ----------
    data : pd.DataFrame
        recorded trend data. Columns used : (pPeak, pPlat, peep, tvInsp)
    param : dict
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format)

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        mes = f"plot_recrut: empty data for {param.get('file', '')}"
        logging.warning(mes)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    # restrict and timeUnit
    toplot_df = pfunc.restrict_trenddf(datadf, param)

    fig = plt.figure()
    fig.__name__ = "recrut"
    # ventil_pressure
    ax1 = fig.add_subplot(111)
    tap.axplot_ventilpressure(ax1, toplot_df)
    pfunc.color_axis(ax1, "left", "tab:red")
    ax1.spines["right"].set_visible(False)
    # ventil_volume
    ax1_r = ax1.twinx()
    tap.axplot_ventiltidal(ax1_r, toplot_df)
    pfunc.color_axis(ax1_r, "right", "tab:orange")
    ax1.spines["left"].set_visible(False)

    for ax in fig.get_axes():
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        if toplot_df.index.dtype == "<M8[ns]":
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            ax.set_xlabel("etime (min)")
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


def plot_ventilcardio(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Build ventilation and cardiovascular plot.

    Parameters
    ----------
    datadf : pd.DataFrame
        trend data. Columns used : ['ip1s', 'ip1m', 'ip1d', 'hr']
    param : dict Optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        mes = f"plot_ventilcardio: {txt} for {param.get('file', '')}"
        logging.warning(mes)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    if "tvInsp" not in datadf.columns:
        logging.warning("no spirometry data in the recording")

    # cardiac_items = {"ip1m", "ip1d", "ip1s", "hr"}
    # if not cardiac_items.issubset(set(datadf.columns)):
    #     diff = cardiac_items - set(datadf.columns)
    #     txt = f"{diff} are not present in the data"
    #     mes = f" {txt} ({param.get('file', '')})"
    #     logging.warning("unable to perform the cardiovacular plot")
    #     logging.warning(mes)
    #     fig = pfunc.empty_data_fig(txt)
    #     pfunc.add_baseline(fig, param)
    #     return fig

    # restrict and timeUnit
    plot_df = pfunc.restrict_trenddf(datadf, param)
    # pressuredf = plot_df[list(cardiac_items)]

    fig = plt.figure(figsize=(12, 5))
    fig.__name__ = "ventil_cardio"

    ax1 = fig.add_subplot(211)
    tap.axplot_ventiltidal(ax1, plot_df)
    pfunc.color_axis(ax1, "left", "tab:orange")  # call
    ax1.spines["right"].set_visible(False)

    ax1_r = ax1.twinx()
    tap.axplot_ventilpressure(ax1_r, plot_df)
    pfunc.color_axis(ax1_r, "right", "tab:red")  # call
    ax1_r.spines["left"].set_visible(False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    # hr in the background
    ax2_r = ax2.twinx()
    # tap.axplot_hr(ax2_r, pressuredf)
    tap.axplot_hr(ax2_r, plot_df)
    pfunc.color_axis(ax2_r, "right", "tab:grey")
    ax2_r.spines["left"].set_visible(False)

    # tap.axplot_arterialpressure(ax2, pressuredf)
    tap.axplot_arterialpressure(ax2, plot_df)
    pfunc.color_axis(ax2, "left", "tab:red")
    ax2.spines["right"].set_visible(False)

    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        pfunc.color_axis(ax, "bottom", "tab:grey")
        if plot_df.index.dtype == "<M8[ns]":
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)
        else:
            ax.set_xlabel("etime (min)")

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


def plot_sathr(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot a sat and sat_hr over time.

    Parameters
    ----------
    taphdata : pd.DataFrame
        the taph recording
    dtime : boolean, optional (default is True)
        plot over dtime (or elapsed time)

    Returns
    -------
    fig : plt.Figure
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        txt = "empty dataframe"
        mes = f"{txt} for {param.get('file', '')}"
        logging.warning("ubale to perform plot_sathr")
        logging.warning(mes)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    oxy_items = {"sat", "spo2Hr"}
    if not oxy_items.issubset(set(datadf.columns)):
        diff = oxy_items - set(datadf.columns)
        txt = f"{diff} are not present in the data"
        mes = f" {txt} ({param.get('file', '')})"
        logging.warning("unable to perform the satHr plot")
        logging.warning(mes)
        fig = pfunc.empty_data_fig(txt)
        pfunc.add_baseline(fig, param)
        return fig

    plot_df = pfunc.restrict_trenddf(datadf, param)
    plot_df = plot_df[list(oxy_items)]

    fig = plt.figure()
    fig.__name__ = "sat_hr"
    # sat
    axl = fig.add_subplot(111)
    tap.axplot_sat(axl, plot_df)
    pfunc.color_axis(axl, "left", "tab:red")  # call
    axl.spines["right"].set_visible(False)
    # sathr
    axr = axl.twinx()
    tap.axplot_sathr(axr, plot_df)
    pfunc.color_axis(axr, "right", "tab:grey")  # call
    axr.spines["left"].set_visible(False)

    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        if plot_df.index.dtype == "<M8[ns]":
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)
        else:
            ax.set_xlabel("etime (min)")

    # annotations
    pfunc.add_baseline(fig, param)

    fig.tight_layout()
    return fig
