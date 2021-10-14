#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:56:58 2019
@author: cdesbois

load a monitor wave recording:
    - choose a file
    - load the header to a pandas dataframe
    - load the date into a pandas dataframe

____
"""

import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog


def choosefile_gui(dir_path=None):
    """select a file using a dialog.

    :param str dir_path: optional location of the data (paths['data'])

    :returns: filename (full path)
    :rtype: str
    """
    print("loadmonitor_waverecord.choosefile_gui")
    if dir_path is None:
        dir_path = os.path.expanduser("~")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dir_path, filter="csv (*.csv)"
    )
    if isinstance(fname, tuple):
        filename = fname[0]
    else:
        filename = str(fname)
    return filename

    # caption = "choose a recording"
    # options = QFileDialog.Options()
    # # to be able to see the caption, but impose to work with the mouse
    # # options |= QFileDialog.DontUseNativeDialog
    # fname = QFileDialog.getOpenFileName(
    #     caption=caption, directory=dir_path, filter="*.csv", options=options
    # )
    # # fname = QFileDialog.getOpenfilename(caption=caption,
    # # directory=direct, filter='*.csv')
    # # TODO : be sure to be able to see the caption
    # return fname[0]


def loadmonitor_waveheader(filename=None):
    """load the wave file header.

    :param str filename: full name of the file

    :returns: header
    :rtype: pandas.Dataframe
    """
    print("loadmonitor_waverecord.loadmonitor_waveheader")
    print("filename= {}".format(os.path.basename(filename)))
    if filename is None:
        filename = choosefile_gui()
        print(f"called returned= {filename}")
    headerdf = pd.read_csv(
        filename, sep=",", header=None, index_col=None, nrows=12, encoding="iso-8859-1"
    )
    return headerdf


def loadmonitor_wavedata(filename=None):
    """load the monitor wave csvDataFile.

    :param str filename: full name of the file

    :returns: df = trends data
    :rtype: pandas.Dataframe
    """
    print("loadmonitor_waverecord.loadmonitor_wavedata")
    fs = 300  # sampling rate
    date = pd.read_csv(filename, nrows=1, header=None).iloc[0][1]
    print("loading wave_data of {}".format(os.path.basename(filename)))
    datadf = pd.read_csv(
        filename,
        sep=",",
        skiprows=[14],
        header=13,
        index_col=False,
        encoding="iso-8859-1",
        usecols=[0, 2, 3, 4, 5, 6],
        dtype={"Unnamed: 0": str},
    )  # , nrows=200000) #NB for development
    datadf = pd.DataFrame(datadf)
    if datadf.empty:
        print(
            "{} there are no data in this file : {} !".format(
                ">" * 20, os.path.basename(filename)
            )
        )
        return datadf
    # columns names correction
    colnames = {
        "~ECG1": "wekg",
        "~INVP1": "wap",
        "~INVP2": "wvp",
        "~CO.2": "wco2",
        "~AWP": "wawp",
        "~Flow": "wflow",
        "~AirV": "wVol",
        "Unnamed: 0": "time",
    }
    datadf = datadf.rename(columns=colnames)

    # scaling correction
    if "wco2" in datadf.columns:
        datadf.wco2 = datadf.wco2.shift(-480)  # time lag correction
        datadf["wco2"] *= 7.6  # CO2 % -> mmHg
    datadf["wekg"] /= 100  # tranform EKG in mVolts
    datadf["wawp"] *= 10  # mmH2O -> cmH2O

    datadf.time = datadf.time.apply(
        lambda x: pd.to_datetime(date + "-" + x) if not pd.isna(x) else x
    )
    # correct date time if over midnight
    min_time_iloc = datadf.loc[datadf.time == datadf.time.min()].index.values[0]
    if min_time_iloc > datadf.index.min():
        print("recording was performed during two days")
        secondday_df = datadf.iloc[min_time_iloc:].copy()
        secondday_df.time = secondday_df.time.apply(
            lambda x: x + timedelta(days=1) if not pd.isna(x) else x
        )
        datadf.iloc[min_time_iloc:] = secondday_df
    # interpolate time values (fill the gaps)
    dt_df = datadf.time[datadf.time.notnull()]
    time_delta = (dt_df.iloc[-1] - dt_df.iloc[0]) / (
        dt_df.index[-1] - dt_df.index[0] - 1
    )
    start_time = datadf.time.iloc[0]
    datadf["datetime"] = [start_time + i * time_delta for i in range(len(datadf))]
    datadf["point"] = datadf.index  # point location
    # add a 'sec'
    datadf["sec"] = datadf.index / fs

    # clean data
    # params = ['wekg', 'wap', 'wco2', 'wawp', 'wflow']

    # wData.wap.value_counts().sort_index()
    datadf.loc[datadf.wap < -100, "wap"] = np.nan
    datadf.loc[datadf.wap > 200, "wap"] = np.nan
    if "wco2" in datadf.columns:
        datadf.loc[datadf.wco2 < 0, "wco2"] = 0
    return datadf


#%%
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    file_name = choosefile_gui(os.path.expanduser("~"))
    file = os.path.basename(file_name)
    if file[0] == "M":
        if "Wave" in file:
            wheader_df = loadmonitor_waveheader(file_name)
            wdata_df = loadmonitor_wavedata(file_name)
