#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 15:30:07 2019
@author: cdesbois

load a taphonius data recording:
    - choose a file
    - load the patient datafile to a dictionary
    - load the physiological date into a pandas dataframe

nb = 4 files per recording :
    - .pdf -> anesthesia record 'manual style'
    - .xml -> taphonius technical record -> to be extracted
    - Patient.csv -> patient id and specifications
    - SD...csv -> anesthesia record
____
"""

import os
import sys
from collections import defaultdict
from datetime import time

import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog


if not "paths" in dir():
    paths = dict()
paths["taph"] = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"


#%% list taph recordings


def list_taph_recordings(pathdict=paths):
    """list all the taph recordings and the paths to the record:
    input:
        paths: dictionary containing {'taph': pathToTheData}
    output:
        dictionary: {date : pathToDirectory}
    """

    months = {
        "jan": "_01_",
        "feb": "_02_",
        "mar": "_03_",
        "apr": "_04_",
        "may": "_05_",
        "jun": "_06_",
        "jul": "_07_",
        "aug": "_08_",
        "sep": "_09_",
        "oct": "_10_",
        "nov": "_11_",
        "dec": "_12_",
    }
    taphpath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    apath = pathdict.get("taph", taphpath)

    dct = defaultdict(list)
    records = []
    for root, dirs, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            records.append(record_name)

            record = record.strip("SD").strip(".csv").lower()
            for k, v in months.items():
                record = record.replace(k, v)
            d = time.strptime(record, "%Y_%m_%d-%H_%M_%S")
            record = "SD" + time.strftime("%Y_%m_%d-%H:%M:%S", d)
            dct[record].append(os.path.dirname(record_name))
    return dct


taphRecords = list_taph_recordings()

#%%
def choosefile_gui(dir_path=None):
    """select a file using a dialog.

    :param str dir_path: optional location of the data (paths['data'])

    :returns: filename (full path)
    :rtype: str
    """
    if dir_path is None:
        dir_path = os.path.expanduser("~")
    caption = "choose a recording"
    options = QFileDialog.Options()
    # to be able to see the caption, but impose to work with the mouse
    # options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(
        caption=caption, directory=dir_path, filter="*.csv", options=options
    )
    # fname = QFileDialog.getOpenfilename(caption=caption,
    # directory=direct, filter='*.csv')
    # TODO : be sure to be able to see the caption
    return fname[0]


def loadtaph_trenddata(filename):
    """load the taphoniusData trends data.

    :param str filename: fullname

    :returns: df = trends data
    :rtype: pandas.Dataframe
    """

    print("{} > loadtaph_trend_data".format("-" * 20))
    if not os.path.isfile(filename):
        print("{} {}".format("!" * 10, "file not found"))
        print("{}".format(filename))
        print("{} {}".format("!" * 10, "file not found"))
        print()
        return pd.DataFrame()
    print("{} loading taphtrend {}".format("-" * 10, os.path.basename(filename)))

    # check
    # filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/REDDY_A13-99999/Patients2013DEC16/Record08_19_11/SD2013DEC16-8_19_11.csv'

    df = pd.read_csv(filename, sep=",", header=1, skiprows=[2])
    corr_title = {
        "Date": "Date",
        "Time": "Time",
        "Events": "events",
        "CPAP/PEEP": "peep",
        "TV": "tv",
        "TVcc": "tvCc",
        "RR": "co2RR",
        "IT": "it",
        "IP": "ip",
        "MV": "minVol",
        "I Flow": "iFlow",
        "I:E Ratio": "IE",
        "Exp Time": "expTime",
        "TV.1": "tv1",
        "Insp Time": "inspTime",
        "Exp Time.1": "expTime",
        "RR.1": "rr1",
        "MV.1": "mv1",
        "I Flow.1": "iFlow1",
        "I:E Ratio.1": "IE1",
        "CPAP/PEEP.1": "peep1",
        "PIP": "pip",
        "Insp CO2": "co2insp",
        "Exp CO2": "co2exp",
        "Resp Rate": "rr",
        "Insp Agent": "aaInsp",
        "Exp Agent": "aaExp",
        "Insp O2": "o2insp",
        "Exp O2": "o2exp",
        "Atmospheric Pressure": "atmP",
        "SpO2 HR": "spo2Hr",
        "Saturation": "sat",
        "Mean": "ip1m",
        "Systolic": "ip1s",
        "Diastolic": "ip1d",
        "HR": "hr",
        "T1": "t1",
        "T2": "t2",
        "ECG HR": "ekgHR",
        "Batt1": "batt1",
        "Current1": "curr1",
        "Batt2": "batt2",
        "Current2": "curr2",
        "Piston Position": "pistPos",
        "Insp N2O": "n2oInsp",
        "Exp N2O": "n2oExp",
    }
    df.rename(columns=corr_title, inplace=True)
    df = pd.DataFrame(df)
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    df["datetime"] = pd.to_datetime(df.Date + ";" + df.Time)
    df["time"] = df.Date + "-" + df.Time
    df["time"] = pd.to_datetime(df["time"], dayfirst=True)
    sampling = (df.time[1] - df.time[0]).seconds
    df["eTime"] = df.index * sampling
    df["eTimeMin"] = df.eTime / 60
    # to remove the zero values :
    # OK for histograms, but induce a bug in plotting
    #    data.ip1m = data.ip1m.replace([0], [None])
    #    data = data.replace([0], [None])
    # CO2: from % to mmHg
    try:
        df[["co2exp", "co2insp"]] *= 760 / 100
    except KeyError:
        print("no capnographic recording")
    file = os.path.basename(filename)

    print("{} < loaded taph_trenddata ({})".format("-" * 20, file))
    return df


def loadtaph_patientfile(headername):
    """load the taphonius patient.csv file

    :param str headername: fullname

    :returns: descr = patient_data
    :rtype: dict
    """
    print("{} > loadind taph_patientfile ({})".format("-" * 20, headername))

    df = pd.read_csv(headername, header=None, usecols=[0, 1], encoding="iso8859_15")
    # NB encoding needed for accentuated letters
    df[0] = df[0].str.replace(":", "")
    df = df.set_index(0).T
    # convert to num
    df["Body weight"] = df["Body weight"].astype(float)
    # convert to a dictionary
    descr = df.loc[1].to_dict()

    print("{} < loaded taph_patientfile ({})".format("-" * 20, headername))
    return descr


#%%
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    dirname = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/"
    # >>>> only one example to developp
    dirname = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18"
    # <<<<
    if not os.path.isdir(dirname):
        dirname = "~"
    file_name = choosefile_gui(dir_path=os.path.expanduser(dirname))
    file = os.path.basename(file_name)
    dirname = os.path.dirname(file_name)

    if file.startswith("SD"):
        tdata_df = loadtaph_trenddata(file_name)
    else:
        print("please choose the file that begins with 'SD'")
        file_name = choosefile_gui(dir_path=dirname)
        file = os.path.basename(file_name)
        if file[:2] == "SD":
            tdata_df = loadtaph_trenddata(file_name)
