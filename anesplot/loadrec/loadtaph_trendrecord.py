#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 15:30:07 2019
@author: cdesbois

load a taphonius data recording:
    - choose a file gui -> filename (! choose the SD...csv file !)
    - load the patient datafile -> dictionary
    - load the recorded date -> pandas.DataFrame

nb = 4 files are present in a Taphonius recording :
    - .pdf -> anesthesia 'manual style' rebuild record
    - .xml -> taphonius technical record
    - Patient.csv -> patient id and specifications
    - SD...csv -> anesthesia record

"""

import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget

if "paths" not in dir():
    paths = {}
paths["taph"] = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"


# list taph recordings
def build_taph_decodedate_dico(pathdict: dict = None) -> dict:
    """
    list all the taph recordings and the paths to the record

    Parameters
    ----------
    pathdict : dict, optional
        dictionary containing {'taph': pathToTheData}, (default is None).

    Returns
    -------
    dict
        get all the recorded files expressed as {date : filename}.

    """

    if pathdict is None:
        pathdict = paths
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
    taphdata = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    apath = pathdict.get("taph_data", taphdata)

    dct = defaultdict(list)
    # records = []
    for root, _, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            # records.append(record_name)

            recorddate = record.strip("SD").strip(".csv").lower()
            for abbr, num in months.items():
                recorddate = recorddate.replace(abbr, num)
            thedate = time.strptime(recorddate, "%Y_%m_%d-%H_%M_%S")
            recorddate = "SD" + time.strftime("%Y_%m_%d-%H:%M:%S", thedate)
            dct[recorddate].append(record_name)
    return dct


def extract_record_day(monitor_file_name: str) -> str:
    """
    extract the date as 'YYYY_MM_DD' from a monitor_filename

    Parameters
    ----------
    monitor_file_name : str
        monitor file name (shortname).

    Returns
    -------
    str
        same date expressed as YYYY_MM_DD.

    """

    record_date = os.path.basename(monitor_file_name.lower())
    for txt in ["sd", "m", ".csv", "wave"]:
        record_date = record_date.strip(txt)
    thedate = time.strptime(record_date, "%Y_%m_%d-%H_%M_%S")
    day = time.strftime("%Y_%m_%d", thedate)
    return day


def choose_taph_record(monitorname: str = None) -> str:
    """
    explore the recording folders and proposes to selct one

    Parameters
    ----------
    monitorname : str, optional
        a monitor file (short) name to place the pointer in the pull down menu.

    Returns
    -------
    str
        selected file (full) name.

    """

    print(f"{' ' * 20} + choose taph_record")
    taphdico = build_taph_decodedate_dico()
    recorddates = sorted(taphdico.keys(), reverse=True)

    # global APP
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    question = "select the recording date"
    if monitorname is not None:
        mname = os.path.basename(monitorname)
        question = f"{question} \n ({mname=})"

    day_index = 0  # first key (<-> last date)
    if monitorname is not None:
        day = extract_record_day(monitorname)
        # index of the first record to be displayed based on year
        for i, thedate in enumerate(recorddates):
            if str(day) in thedate:
                day_index = i
                break
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    recorddate, ok_pressed = QInputDialog.getItem(
        widg, "select", question, recorddates, day_index, False
    )
    if ok_pressed and recorddate:
        filename = taphdico[recorddate][
            -1
        ]  # if bug : two dirs, the last should contain the data
        print(f"{'-' * 10} founded {os.path.basename(filename)}")
    else:
        filename = None
        print(f"{'-' * 10} cancelled")
    return filename


def loadtaph_trenddata(filename: str) -> pd.DataFrame:
    """
    load the taphoniusData trends data.

    Parameters
    ----------
    filename : str
        selected file (full) name.

    Returns
    -------
    pandas.DataFrame
        the recorded data.

    """

    if filename is None:
        print(f"{'!' * 10} no name provided")
        return pd.DataFrame()
    print(f"{'-' * 20} < loadtaph_datafile")
    if not os.path.isfile(filename):
        print(f"{'!' * 10} datafile not found")
        print(f"{filename}")
        print(f"{'!' * 10} datafile not found")
        print()
        return pd.DataFrame()
    print(f"{'-' * 10} loading taph_datafile {os.path.basename(filename)}")

    # check
    # filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/'+
    # 'before2020/REDDY_A13-99999/Patients2013DEC16/Record08_19_11/SD2013DEC16-8_19_11.csv'

    try:
        # df = pd.read_csv(filename, sep=",", header=1, skiprows=[2])
        # row 0 -> groups
        # row 1 -> header
        # row 2 -> units
        datadf = pd.read_csv(
            filename, sep=",", header=1, skiprows=[2], index_col=False,
        )
    except pd.errors.ParserError:
        print(f"corrupted file ({os.path.basename(filename)})")
        # generally related to pb with the auxillary controler
        # df = pd.read_csv(
        #     filename,
        #     sep=",",
        #     header=1,
        #     skiprows=[2],
        #     on_bad_lines="skip",
        #     engine="python",
        #     index_col=False,
        # )
        return pd.DataFrame()

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
        "Exp Time.1": "expTime1",
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
    datadf.rename(columns=corr_title, inplace=True)
    datadf = pd.DataFrame(datadf)
    # datadf.replace("nan", np.nan)
    datadf = datadf.dropna(axis=0, how="all")
    datadf = datadf.dropna(axis=1, how="all")

    if len(datadf) < 4:
        print(f"empty file ({os.path.basename(filename)})")
        for col in ["datetime", "time", "eTime", "eTimeMin"]:
            datadf[col] = np.nan
        return datadf
    # # >>
    # import pdb

    # pdb.set_trace()
    # # >>
    datadf["datetime"] = pd.to_datetime(datadf.Date + ";" + datadf.Time, dayfirst=True)
    datadf["time"] = datadf.Date + "-" + datadf.Time
    datadf["time"] = pd.to_datetime(datadf["time"], dayfirst=True)

    datadf[["Date", "Time"]] = datadf[["Date", "Time"]].astype(str)
    # nb not for events because that will change np.nan to str(nan)
    sampling = (datadf.time[1] - datadf.time[0]).seconds
    datadf["eTime"] = datadf.index * sampling
    datadf["eTimeMin"] = datadf.eTime / 60
    # to remove the zero values :
    # OK for histograms, but induce a bug in plotting
    #    data.ip1m = data.ip1m.replace([0], [None])
    #    data = data.replace([0], [None])
    # CO2: from % to mmHg
    try:
        datadf[["co2exp", "co2insp"]] *= 760 / 100
    except KeyError:
        print("no capnographic recording")
    print(f"{'-' * 20} loaded taph_datafile ({os.path.basename(filename)}) >")
    return datadf


def loadtaph_patientfile(filename: str) -> dict:
    """
    load the taphonius patient.csv file ('header' in monitor files, description)

    Parameters
    ----------
    filename : str
        the taph recording file (full) name ('SDYYYMMDD...').
        (the headername will be reconstructed inside the function)

    Returns
    -------
    dict
        the patient description data.

    """

    headername = os.path.join(os.path.dirname(filename), "Patient.csv")

    print(f"{'.' * 20} < loading taph_patientfile")
    if not os.path.isfile(headername):
        print(f"{'!' * 10} patient_file not found")
        print(f"{headername}")
        print(f"{'!' * 10} patient_file not found")
        print()
        return {}
    print(f"{'.' * 10} loading {os.path.basename(headername)}")

    patientdf = pd.read_csv(
        headername, header=None, usecols=[0, 1], encoding="iso8859_15"
    )
    # NB encoding needed for accentuated letters
    patientdf[0] = patientdf[0].str.replace(":", "")
    patientdf = patientdf.set_index(0).T
    # convert to num
    patientdf["Body weight"] = patientdf["Body weight"].astype(float)
    # convert to a dictionary
    descr = patientdf.loc[1].to_dict()

    print(f"{'-' * 20} loaded taph_patientfile ({os.path.basename(headername)}) >")
    return descr


def shift_datetime(datadf: pd.DataFrame, minutes_to_add: int = None) -> pd.DataFrame:
    """
    add a datetime shift to the dataframe to compensate computer time shift (usually one hour)

    Parameters
    ----------
    datadf : pd.DataFrame
        a recording (that have to contain 'datetime' and 'time' column.
    minutes_to_add : int, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    datadf : pd.DataFrame
        the recording with shifted datetime and time columns.

    """
    if minutes_to_add:
        shift = timedelta(minutes=minutes_to_add)
        if {"datetime", "time"} < set(datadf.columns):
            datadf["datetime"] += shift
            datadf["time"] += shift
        else:
            print("datetime and time are not in the dataframe columns")
    return datadf


def shift_elapsed_time(
    datadf: pd.DataFrame, minutes_to_add: int = None
) -> pd.DataFrame:
    """
    add a elapsedtime shift to the dataframe to compensate recording start

    Parameters
    ----------
    datadf : pd.DataFrame
        a recording (that have to contain 'datetime' and 'time' column.
    minutes_to_add : int, optional (default is None)

    Returns
    -------
    datadf : pd.DataFrame
        the recording with shifted eTime and eTimeMin columns.

    """
    if minutes_to_add:
        shift = minutes_to_add
        if {"eTime", "eTimeMin"} < set(datadf.columns):
            datadf["eTime"] += shift * 60
            datadf["eTimeMin"] += shift
        else:
            print("eTime and eTimeMin are not in the dataframe columns")
    return datadf


def sync_elapsed_time(datetime_0: datetime, taphdatadf: pd.DataFrame) -> pd.DataFrame:
    """
    use the first point of monitor recording to sync the taph elapsed time (s and min)
    !!! beware, datetime should be the same one the two devices ... or corrected !!!

    Parameters
    ----------
    datetime_0 : datetime.datetime
        the 0 of the time (usually monitordatadf.datetime.iloc[0]
    taphdatadf : pd.DataFrame
        the taph recording.

    Returns
    -------
    taphdatadf : pd.DataFrame
        the corrected taph recording.

    """
    mini_index = (abs(taphdatadf.datetime - datetime_0)).idxmin()
    taphdatadf.eTime -= taphdatadf.iloc[mini_index].eTime
    taphdatadf.eTimeMin -= taphdatadf.iloc[mini_index].eTimeMin
    return taphdatadf


# %%
if __name__ == "__main__":

    # from PyQt5.QtWidgets import QApplication
    from anesplot.config.load_recordrc import build_paths

    paths = build_paths()
    APP = QApplication(sys.argv)
    APP.setQuitOnLastWindowClosed(True)

    #   monitor_name = "M2021_9_9-11_44_35.csv"
    #    file_name = choose_taph_record(monitor_name)
    NAME = (
        "before2020/Anonymous/Patients2013DEC17/Record08_29_27/SD2013DEC17-8_29_27.csv"
    )
    NAME = "Anonymous/Patients2022JAN21/Record22_52_07/SD2022JAN21-22_52_7.csv"
    # check datetime (non linear and there is 2015 & 2021dates)
    file_name = os.path.join(paths["taph_data"], NAME)

    tdata_df = loadtaph_trenddata(file_name)
    header_dico = loadtaph_patientfile(file_name)
