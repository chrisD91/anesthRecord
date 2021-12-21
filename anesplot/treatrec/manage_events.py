#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

to extract the events from the taphonius files

"""
import os

import pandas as pd

import anesplot.record_main as rec

file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"
file = os.path.basename(file_name)

# see the taphClass
ttrend = rec.TaphTrend(file_name)
self = ttrend
eventdf = self.data[["events", "datetime"]].dropna()
eventdf = eventdf.set_index("datetime")
eventdf.events = eventdf.events.apply(
    lambda st: [_.strip("[").strip("]") for _ in st.split("\r\n")]
)

#%%
def convert_day(st):
    """get a day YYYYmonthD an convert it to YYY-month-D"""
    previous = st[0]
    new = st[0]
    for x in st[1:]:
        if x.isalpha() == previous.isalpha():
            new += x
        else:
            new += "-" + x
        previous = x
    return new


def extract_taphmessages(df):
    """extract the messages that contain the kw"""
    content = set()
    for cell in df.events:
        for event in cell:
            content.add(event.split("-")[-1])
    content = {_.split(":")[0].strip() for _ in content}
    content = {_.split("from")[0].strip() for _ in content}

    acts = {_ for _ in content if "changed" in _}
    acts = {
        _ for _ in acts if not _.startswith("Power") and not _.startswith("Primary")
    }
    errors = content - acts

    return errors, acts


day = file.split("-")[0].strip("SD")
day = convert_day(day)

error_messages, action_messages = extract_taphmessages(eventdf)

#%%
# TODO find preset values
message = ""  # ?? presetq


def extract_event(df):
    """extract timestamp of the messages
    input:
        df: pandasDataFrame containing the taphonius events
    output:
        marks: dictionary {message : [timestamp]}
    """
    marks = {}
    messages = ["Init Complete", "Ventilate"]
    for mes in messages:
        # for message in action_messages:
        matching = []
        for i, cell in enumerate(df.events):
            for event in cell:
                if mes in event:
                    matching.append((i, event))
                    # print(event)
        marks[mes] = []
        for match in matching:
            i = match[0]
            time_stp = eventdf.index[i]
            marks[mes].append(time_stp)
    return marks


def extract_actions(df, messages):
    """extract actions dtime and changes from taph recording:
    input:
        df: pandasDataFrame of taph events
        actions : action messages
    output
        marks: dictionary {action : [[timestamp, (valueBefore, valueAfter)], ...]}
    """
    marks = {}
    for mes in messages:
        matching = []
        for i, cell in enumerate(df.events):
            for event in cell:
                if mes in event:
                    matching.append((i, event))
                    # print(event)
        # action : [[dtime, before, after], ...]
        marks[mes] = []
        for match in matching:
            i = match[0]
            values = list(match[1].split("from")[-1].strip().split(" to "))
            values = [_.replace("s", "") for _ in values]
            values = [float(_) for _ in values]
            time_stp = eventdf.index[i]
            marks[mes].append([time_stp, values])
    return marks


events = extract_event(eventdf)
actions = extract_actions(eventdf, action_messages)
#%%


def build_dataframe(acts):
    """build a dataframe containing all the actions, one per column"""

    names = {
        "Inspiratory pause value changed": "pause",
        "CPAP value changed": "peep",
        "Tidal Volume changed": "vol",
        "RR changed": "rr",
    }
    dflist = []
    for act, event in acts.items():
        df = pd.DataFrame(event, columns=["dt", names[act]]).set_index("dt")
        dflist.append(df)
    df = pd.concat(dflist).sort_index()

    return df


action_df = build_dataframe(actions)
