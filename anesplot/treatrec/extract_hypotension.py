# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import anesplot.record_main as rec
from anesplot.record_main import MonitorTrend

#import utils
font_size = 'medium' # large, medium
params = {'font.sans-serif': ['Arial'],
          'font.size': 12,
          'legend.fontsize': font_size,
          'figure.figsize': (8.5, 3),
          'axes.labelsize': font_size,
          'axes.titlesize': font_size,
          'xtick.labelsize': font_size,
          'ytick.labelsize': font_size,
          'axes.xmargin': 0}
plt.rcParams.update(params)
plt.rcParams['axes.xmargin'] = 0            # no gap between axes and traces



#df = trends.data
#%%

plt.close('all')

def extract_hypotension(trends, pamin=70):
    """
    return a dataframe with the beginning and ending phses of hypotension

    Parameters
    ----------
    trends : MonitorTrend object
    pamin : float= threshold de define hypotension on mean arterial pressure
    (default is 70)
    Returns
    -------
    durdf : pandas DataFrame containing
        transitionts (up and down, in  seconds from beginning)
        and duration in the hypotension state (in seconds)
    """
    df = trends.data.copy()
    if 'ip1m' not in df.columns:
        print('no ip1m recording in the data')
        return trends.param['file']
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))['ip1m'])
    df['low'] = df.ip1m < pamin
    df['trans'] = df.low - df.low.shift(-1)
    # extract changes
    durdf = pd.DataFrame()
    # monotonic
    if len(df.trans.dropna().value_counts()) > 1:
        durdf['down'] = df.loc[df.trans == -1].index.to_list()
        up = df.loc[df.trans == 1].index.to_list()
        durdf = durdf.join(pd.Series(name='up', data=up))
        a, b = durdf.iloc[0]
        if a > b:
            durdf.up = durdf.up.shift(-1)
        durdf['hypo_duration'] = durdf.up - durdf.down
        durdf = durdf.dropna()
    return durdf


def plot_hypotension(trends, durdf, durmin=15, pamin=70):
    """
    plot the hupotentions phases

    Parameters
    ----------
    trends : TYPE
        DESCRIPTION.
    durdf : TYPE
        DESCRIPTION.
    durmin : TYPE, optional
        DESCRIPTION. The default is 15.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.

    """
    param = trends.param
    df = trends.data.copy()
    if len(df) < 1:
        print('empty data for {}'.format(param['file']))
        return param['file']
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))['ip1m'])

    fig = plt.figure()
    fig.suptitle('peroperative hypotension')
    ax = fig.add_subplot(111)
    ax.plot(df.ip1m, '-', color='tab:red', alpha=0.8)
    ax.axhline(y=70, color='tab:grey', alpha=0.5)
    if len(durdf) > 0:
        for a,b,t  in durdf.loc[durdf.hypo_duration > 60].values:
            ax.vlines(a, ymin=50, ymax=70, color='tab:red', alpha = 0.5)
            ax.vlines(b, ymin=50, ymax=70, color='tab:green', alpha = 0.5)
            if t > 15 * 60:
                ax.axvspan(xmin=a, xmax=b, color='tab:red', alpha=0.3)
        nb = len(durdf[durdf.hypo_duration > (durmin * 60)])
        txt = '{} period(s) of significative hypotension \n (longer than {} min below {} mmHg)'.format(
            nb, durmin, pamin)
        ax.text(0.5, 0.1, txt, ha='center', va='bottom', transform=ax.transAxes,
                color='tab:grey')
        txt = 'hypotension lasting longer than 15 minutes are represented as red rectangles '
        ax.text(0.5, 0.95, txt, ha='center', va='bottom', transform=ax.transAxes,
                color='tab:grey')
        durations = list(durdf.loc[
            durdf.hypo_duration > 15*60, ['hypo_duration']].
            values.flatten() / 60)
        if len(durations) > 0:
            durations = [round(_) for _ in durations]
            txt = 'hypotensions={} min'.format(durations)
            ax.text(0.5, 0.03, txt, ha='center', va='bottom', 
                    transform=ax.transAxes, color='k')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    return fig

def plot_all_dir_hypo(dirname=None):
    if dirname is None:
        dirname = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded'
    files = []
    for file in os.listdir(dirname):
        if os.path.isfile(os.path.join(dirname, file)):
            files.append(file)    
    files = [_ for _ in files if 'Wave' not in _]
    files = [_ for _ in files if not _.startswith('.')]
    for file in files:
        filename = os.path.join(dirname, file)
        trends = MonitorTrend(filename)
        if not trends.data is None:
            if 'ip1m' in trends.data.columns:
                dur_df = extract_hypotension(trends, pamin=70)
                plot_hypotension(trends, dur_df)
    # in case of pb
    return filename


#%%
# filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded/M2021_3_8-9_9_48.csv'
# trends = rec.MonitorTrend(filename)
plt.close('all')
dir_name = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded/2018'

filename = plot_all_dir_hypo(dir_name)    

trends = MonitorTrend(filename)
if not trends.data is None:
    dur_df = extract_hypotension(trends, pamin=70)
    fig = plot_hypotension(trends, dur_df)
else: 
    print('no data')