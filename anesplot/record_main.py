#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main script/module to load and display an anesthesia record

can be runned as a script::
    python record_main.py

or imported as a package::
    import anestplot.record_main as rec

----
"""
# see https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from pathlib import Path

print("Running" if __name__ == "__main__" else "Importing", Path(__file__).resolve())
# print('-'*10)
# print('this is {} file and __name__ is {}'.format('record_main', __name__))
# print('this is {} file and __package__ is {}'.format('record_main', __package__))
# print('-'*10)

# print('__file__={0:<35} \n __name__={1:<20} \n __package__={2:<20}'.format(
#     __file__,__name__,str(__package__)))
# print('-'*10)


import gc
import os
import sys
from importlib import reload

import numpy as np
import pandas as pd
import pyperclip

import matplotlib

matplotlib.use("Qt5Agg")  # NB use automatic for updating
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget

# to have the display beginning from 0
from matplotlib import rcParams

rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

from anesplot.config.load_recordRc import build_paths

paths = build_paths()
# paths = load_recordRc.paths

# works from outside, but not within spyder (relative import)
# see https://dev.to/codemouse92/dead-simple-python-project-structure-and-imports-38c6
# error in spyder : relative import with no known parent package
# from .loadrec import explore

# requires to have '.../anesthPlot' in the path
import anesplot.loadrec.explore
import anesplot.loadrec.loadmonitor_trendrecord as lmt
import anesplot.loadrec.loadmonitor_waverecord as lmw
import anesplot.loadrec.loadtaph_trendrecord as ltt
import anesplot.loadrec.loadtelevet as ltv
import anesplot.plot.trend_plot as tplot
import anesplot.plot.wave_plot as wplot
import anesplot.treatrec.clean_data as clean
import anesplot.treatrec.wave_func as wf
import anesplot.treatrec as treat

# import loadrec.explore

# from . import loadrec.explore


def choosefile_gui(dir_path=None):
    """Select a file via a dialog and return the (full) filename.

    parameters
    ----
    dir_path : str
        location to place the gui ('generally paths['data']) else home

    return
    ----
    fname[0] : str
        filename
    """
    if dir_path is None:
        dir_path = os.path.expanduser("~")
    caption = "choose a recording"
    options = QFileDialog.Options()
    # to be able to see the caption, but impose to work with the mouse
    #    options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(
        caption=caption, directory=dir_path, filter="*.csv", options=options
    )
    #    fname = QFileDialog.getOpenfilename(caption=caption,
    #                                        directory=direct, filter='*.csv')
    # TODO : be sure to be able to see the caption
    return fname[0]


def trendname_to_wavename(name):
    """ just compute the supposed name """
    return name.split(".")[0] + "Wave.csv"


def select_type(question=None, items=None, num=0):
    """select the recording type:

    parameters
    ----

    return
    ----
    kind : str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet]
       """
    if items is None:
        items = ("monitorTrend", "monitorWave", "taphTrend", "telVet")
    if question is None:
        question = "choose kind of file"
    qw = QWidget()
    kind, ok_pressed = QInputDialog.getItem(qw, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = kind
    else:
        selection = None
    return selection


def select_wave(waves, num=1):
    """select the recording type:

    parameters
    ----

    return
    ----
    kind : str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet]
       """
    if num == 1:
        question = "choose first wave"
    if num == 2:
        question = "do you want a second one ?"
    qw = QWidget()
    wave, ok_pressed = QInputDialog.getItem(qw, "select", question, waves, 0, False)
    if ok_pressed and wave:
        selection = wave
    else:
        selection = None
    return selection


def build_param_dico(file=None, asource=None, pathdico=paths):
    """initialise a dict save parameters  ----> TODO see min vs sec

    parameters
    ----
    file : str
        the recording filename
    source : str
        the origin of the recording
    return
    ----
    dico : dict
        a dictionary describing the situation
            [item, xmin, xmax, ymin, ymax, path, unit, save, memo, file, source]
    """
    dico = dict(
        item=1,
        xmin=None,
        xmax=None,
        ymin=0,
        ymax=None,
        path=pathdico.get("sFig", "~"),
        unit="min",
        save=False,
        memo=False,
        file=file,
        source=asource,
        dtime=True,
    )
    return dico


def plot_trenddata(df, header, param_dico):
    """clinical main plots of a trend recordings

    parameters
    df : pdDataframe
        recorded data (MonitorTrend.data)
    header : dict
        recording parameters (MonitorTrend.header)
    param_dico : dict
        plotting parameters (MonitorTrend.param)

    return
    ----
    afig_dico : dict of name:fig
    """
    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        if "co2exp" in df.columns.values:
            df.loc[df["co2exp"] < 20, "co2exp"] = np.NaN
        if ("ip1m" in df.columns.values) and not df.ip1m.isnull().all():
            df.loc[df["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            print("no pressure tdata recorded")
    afig_list = []
    print("building figures")
    # plotting
    plot_func_list = (
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
    )
    for func in plot_func_list:
        # afig_list.append(func(df.set_index("eTimeMin"), param_dico))
        afig_list.append(func(df, param_dico))
    afig_list.append(tplot.plot_header(header, param_dico))
    # for fig in afig_list:
    #     if fig:                 # test if figure is present
    #         fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    #         fig.text(0.01, 0.01, file, ha='left', va='bottom', alpha=0.4)
    print("plt.show")
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    names.append("header")
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


class Waves:
    """the base object to store the records."""

    def __init__(self, filename=None):
        """
        :param filename: DESCRIPTION, defaults to None
        :type filename: str, optional
        :return: basic class for the records
        :rtype: wave object

        """
        if filename is None:
            filename = choosefile_gui(paths["data"])
        self.filename = filename
        self.file = os.path.basename(filename)
        self.fs = None
        self.source = None
        self.data = None
        self.header = None
        self.param = dict(
            xmin=None,
            xmax=None,
            ymin=0,
            ymax=None,
            path=paths["sFig"],
            unit="min",
            save=False,
            memo=False,
            file=os.path.basename(filename),
            source=None,
            fs=None,
            dtime=True,
        )


# +++++++
class SlowWave(Waves):
    """class for slowWaves = trends

    attributes:
    -----------
        file : str
            short name
        filename : str
            long name

    methods
    -------
        clean_trend : external
            clean the data
        show_graphs : external
            plot clinical main plots
    """

    def __init__(self, filename=None):
        super().__init__(filename)

    def clean_trend(self):
        """
        clean the data, remove irrelevant,
        input = self.data,
        output = pandas dataFrame
        nb doesnt change the obj.data in place
        """
        df = clean.clean_trenddata(self.data)
        return df

    def show_graphs(self):
        """ basic clinical plots """
        fig_dico = plot_trenddata(self.data, self.header, self.param)
        return fig_dico


class MonitorTrend(SlowWave):
    """ monitor trends recordings:

        input = filename : path to file
        load = boolean to load data (default is True)

    attibutes:
    ----------
        file : str
            short name
        filename : str
            long name
        header : dict
            record parameters
        source : str
            recording apparatus (default = 'monitor')
        fs : float
            sampling rate
        param : dict
            display parameters

    methods (inherited)
    -------------------
        clean_trend : external
            clean the data
        show_graphs : external
            plot clinical main plots
    """

    def __init__(self, filename=None, load=True):
        super().__init__(filename)
        self.header = lmt.loadmonitor_trendheader(self.filename)
        self.load = load
        # load if header is present & not data
        if self.header:
            if self.load:
                self.data = lmt.loadmonitor_trenddata(self.filename, self.header)
            self.source = "monitor"
            self.fs = self.header.get("Sampling Rate", None)
            self.param["source"] = "monitorTrend"
            # self.param'file' : os.path.basename(filename)}


class TaphTrend(SlowWave):
    """ taphonius trends recordings

    input  ... FILLME

    attributes ... FILLME


    """

    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltt.loadtaph_trenddata(self.filename)
        self.source = "taphTrend"
        self.header = self.load_header()

    def load_header(self):
        """ load the header -> pandas.dataframe """
        headername = choosefile_gui(dir_path=os.path.dirname(self.filename))
        if headername:
            header = ltt.loadtaph_patientfile(headername)
        else:
            header = None
        return header

    def extract_taph_events(self):
        """ extract Taph events

        parameters
        ----------
        data : pandas dataframe
            record df form taphonius recording)

        return
        ------
        eventdf pandas dataframe
            events dataframe
        """
        eventdf = self.data[["events", "datetime"]].dropna()
        # remove time, keep event
        eventdf.events = eventdf.events.apply(lambda st: st.split("-")[1])
        return eventdf


# ++++++++
class FastWave(Waves):
    """class for Fastwaves = continuous recordings."""

    def __init__(self, filename=None):
        super().__init__(filename)

    def plot_wave(self, tracesList=None):
        """
        simple choose and plot for a wave
        input = none -> GUI, or list of waves to plot (max=2)

        """
        if self.data.empty:
            fig = None
            print("there is no data to plot")
        else:
            cols = [w for w in self.data.columns if w[0] in ["i", "r", "w"]]
            if tracesList is None:
                tracesList = []
                # trace = select_type(question='choose wave', items=cols)
                for num in [1, 2]:
                    trace = select_wave(waves=cols, num=num)
                    if trace is not None:
                        tracesList.append(trace)
            if tracesList:
                # fig, _ = wf.plot_wave(self.data, keys=[trace], mini=None, maxi=None)
                fig, lines = wplot.plot_wave(
                    self.data, keys=tracesList, param=self.param
                )
                fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
                fig.text(0.01, 0.01, self.file, ha="left", va="bottom", alpha=0.4)
                self.trace = tracesList
                plt.show()
            else:
                self.trace = None
                fig = None
                lines = None
            self.fig = fig
            return fig, lines

    def define_a_roi(self):
        """define a ROI."""
        df = self.data
        if self.fig:
            ax = self.fig.get_axes()[0]
            # TODO chekc points of date of xaxis
            if self.param["dtime"]:
                # TODO get the iloccation from the dtime
                # df.iloc[df.index.get_loc(dt, method='nearest')]
                # bug if values are duplicated (eg in the end of a wave recording)

                startT, endT = ax.get_xlim()
                start_dtime = pd.to_datetime(matplotlib.dates.num2date(startT))
                end_dtime = pd.to_datetime(matplotlib.dates.num2date(endT))
                # remove timezone
                start_dtime = start_dtime.tz_localize(None)
                end_dtime = end_dtime.tz_localize(None)
                start_dt, start_pt, start_sec = (
                    df.loc[df.datetime == start_dtime, ["datetime", "point", "sec"]]
                    .head(1)
                    .squeeze()
                )

                end_dt, end_pt, end_sec = (
                    df.loc[df.datetime == end_dtime, ["datetime", "point", "sec"]]
                    .tail(1)
                    .squeeze()
                )

            else:
                # point Value
                lims = ax.get_xlim()  # pt values

                start_dt, start_pt, start_sec = (
                    df.loc[df.point == int(lims[0]), ["datetime", "point", "sec"]]
                    .head(1)
                    .squeeze()
                )
                end_dt, end_pt, end_sec = (
                    df.loc[df.point == int(lims[1]), ["datetime", "point", "sec"]]
                    .tail(1)
                    .squeeze()
                )

            roidict = {
                "sec": (start_sec, end_sec),
                "pt": (start_pt, end_pt),
                "dt": (start_dt, end_dt),
            }
            self.roi = roidict


class TelevetWave(FastWave):
    """class to organise teleVet recordings transformed to csv files."""

    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltv.loadtelevet(filename)
        self.source = "teleVet"
        self.fs = self.data.index.max() / self.data.timeS.iloc[-1]


class MonitorWave(FastWave):
    """class to organise monitorWave recordings.
        input : filename = path to file
        load = boolean to load data (default is True)

    attibutes ... FILLME


    methods ... FILLME
    """

    def __init__(self, filename=None, load=True):
        super().__init__(filename)
        header = lmw.loadmonitor_waveheader(filename)
        self.header = dict(zip(header[0], header[1]))
        self.load = load
        if self.load:
            data = lmw.loadmonitor_wavedata(filename)
            self.data = data
        self.source = "monitorWave"
        self.fs = 300
        self.param["fs"] = 300


def main():
    # look for terminal filename passed as the first argument
    provided_filename = None
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            provided_filename = sys.argv[1]
        else:
            print("{} is not a valid filename".format(sys.argv[1]))

    os.chdir(paths["recordMain"])
    print("backEnd= ", plt.get_backend())  # required ?
    print("start QtApp")
    try:
        app
    except NameError:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    # list of loaded records
    try:
        records
    except NameError:
        records = {}
    # choose file and indicate the source
    print("select the file containing the data")
    if provided_filename is None:
        file_name = choosefile_gui(paths["data"])
    else:
        file_name = provided_filename
    pyperclip.copy(file_name)
    kinds = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    # select base index in the scoll down
    num = 0
    if "Wave" in file_name:
        num = 1
    if not os.path.basename(file_name).startswith("M"):
        num = 2
    source = select_type(question="choose kind of file", items=kinds, num=num)
    # general parameters
    params = build_param_dico(file=os.path.basename(file_name), asource=source)
    if not os.path.isfile(file_name):
        print("this is not a file")
        return
    if source == "telVet":
        telvet = TelevetWave(file_name)
        params["fs"] = 500
        params["kind"] = "telVet"
        telvet.param = params
        telvet.plot_wave()
    elif source == "monitorTrend":
        monitorTrend = MonitorTrend(file_name)
        if monitorTrend.data is None:
            print("empty recording")
            return
        if monitorTrend.header is None:
            print("empty header")
            return
        params["t_fs"] = monitorTrend.header.get("Sampling Rate") / 60
        monitorTrend.param = params
        if monitorTrend.data is not None:
            fig_list = monitorTrend.show_graphs()
    elif source == "monitorWave":
        monitorWave = MonitorWave(file_name)
        params["fs"] = float(monitorWave.header["Data Rate (ms)"]) * 60 / 1000
        params["kind"] = "as3"
        monitorWave.param = params
        monitorWave.plot_wave()
    elif source == "taphTrend":
        taphTrend = TaphTrend(file_name)
        taphTrend.param = params
        # tdata= clean.clean_trendData(tdata)
        fig_list = taphTrend.show_graphs()
    else:
        print("this is not recognized recording")
    # records = list_loaded()
    plt.show()
    try:
        app
    except NameError:
        app.exec_()
    return file_name


#%%
if __name__ == "__main__":
    filename = main()
