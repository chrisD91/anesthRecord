#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:52:00 2020

function used to treat an EKG signal and extract the heart rate
typycally=
0- view if files are loaded
    print(check())
1- params
    params = monitorWave.param
    #data = monitorWave.data
    # build a dataframe to work with (waves)
    ekg_df = pd.DataFrame(monitorWave.data.wekg)

2- low pass filtering
    ekg_df['wekg_lowpass'] = wf.fix_baseline_wander(ekg_df.wekg,
                                                monitorWave.param['fs'])
3- beats locations (beat based dataFrame)
    beat_df = detect_beats(ekg_df.wekg_lowpass, params)
4- plot
    figure = plot_beats(ekg_df.wekg_lowpass, beat_df)

    #fs=300
    beat_df = compute_rr(beat_df, monitorWave.param)
    hr_df = interpolate_rr(beat_df)
    figure = plot_rr(hr_df, params, HR=True)


@author: cdesbois
"""

#import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.signal as sg
from scipy.interpolate import interp1d
import treatrec.wave_func as wf

#%
def detect_beats(ser, fs=300, species='horse'):
    """ detect the peak locations """
    df = pd.DataFrame()
#    fs = param.get('fs', 300)
    if species == 'horse':
        height = 0.5      # min, max
        distance = 0.7*fs    # sec
        prominence = 1
        #    width=(2,15)
        #    plateau_size= 1
    else:
        print('no parametrisation performed ... to be done')
        return df
    pk, beats_params = sg.find_peaks(ser*-1, height=height, distance=distance,
                                     prominence=prominence)
    df['pLoc'] = pk
    for key in beats_params.keys():
        df[key] = beats_params[key]
    if 'peak_heights' in df.columns:
        df = df.rename(columns={'peak_heights': 'yLoc'})
        df.yLoc *= -1
    return df

def plot_beats(ecg, beats):
    """ plot ecg waveform + beat location """
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('verify the accuracy of the beat detection')
    ax0 = fig.add_subplot(211)
    ax0.plot(ecg.values, label='ekg')
    ax0.set_ylabel('ekg (mV)')
    ax0.set_xlabel('pt value')
    ax0.plot(beats.pLoc, beats.yLoc, 'o', color='orange', label='R')
    
    ax1 = fig.add_subplot(212, sharex=ax0)
    ax1.plot(beats.pLoc[:-1], np.diff(beats.pLoc), 'r-', label='rr')
    ax1.set_ylabel('rr (pt value)')
    ax1.set_xlabel('pt value')
    fig.legend()
    for ax in fig.get_axes():
        for loca in ['top', 'right']:
            ax.spines[loca].set_visible(False)
    fig.tight_layout()
    return fig

def locate_beat(df, fig):
    """ locate the beat location identified in the figure """
    # find irrelevant beat location
    # see https://stackoverflow.com/questions/21415661/
    #logical-operators-for-boolean-indexing-in-pandas
    lims = fig.get_axes()[0].get_xlim()
    position = df.pLoc[(lims[0] < df.pLoc) & (df.pLoc < lims[1])].index
    print('to add a peak use df.drop(<position>, inplace=True)')
    print("don't forget to rebuild the index") 
    print("df.sort_value(by=['pLoc']).reset_index(drop=True)")
    return position

def append_a_peak(beatdf, ekgdf, fig, lim=None):
    """ append the beat location in the fig to the beat_df 
        input : beat_df, 
                figure scaled to see one peak,
                lim = tuple(xmin, xmax), default=None
        output : df sorted and reindexed
    """
    # find the limits of the figure
    if not lim:
        lim = fig.get_axes()[0].get_xlim()
    #restrict area around the undetected pic
    df = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]]
    #locate the beat (external call)
    local_df = detect_beats(df)
    locpic = local_df.pLoc.values[0]
    # reassign the pt value
    pt_pic = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]].index[locpic]
    local_df.pLoc.values[0] = pt_pic
    local_df.left_bases.values[0] += (pt_pic - locpic)
    local_df.right_bases.values[0] += (pt_pic - locpic)
    # reinsert in the beat_df
    beatdf = pd.concat([beatdf, local_df])
    beatdf = beatdf.sort_values(by=['pLoc']).reset_index(drop=True)
    return beatdf

#%
def compute_rr(abeat_df, param):
    """
    compute rr intervals
    intput : pd.DataFrame with 'pLoc', and fs=sampling frequency
    output : pd.DataFrame appendend with:
        'rr' =  rr duration
        'rrDiff' = rrVariation
        'rrSqDiff' = rrVariation^2
    """
    fs = param.get('fs', 300)
    # compute rr intervals
#    beat_df['rr'] = np.diff(beat_df.pLoc)
    abeat_df['rr'] = abeat_df.pLoc.shift(-1) - abeat_df.pLoc # pt duration
    abeat_df.rr = abeat_df.rr / fs*1000     # time duration
    #remove outliers
    abeat_df = abeat_df.replace(abeat_df.loc[abeat_df.rr > 2000], np.nan)
    abeat_df = abeat_df.interpolate()
    abeat_df = abeat_df.dropna(how='all')
    abeat_df = abeat_df.dropna(axis=1, how='all')
    # compute variation
    abeat_df['rrDiff'] = abs(abeat_df.rr.shift(-1) - abeat_df.rr)
    abeat_df['rrSqDiff'] = (abeat_df.rr.shift(-1) - abeat_df.rr)**2
    return abeat_df

def interpolate_rr(abeat_df):
    """
    interpolate the beat_df (pt -> time values)
    input : beat Df
    output : pdDatatrame with evenly spaced data
        'espts' = evenly spaced points
        'rrInterpol' = interpolated rr
    """
    ahr_df = pd.DataFrame()

    first_beat_pt = int(beat_df.iloc[0].pLoc)
    last_beat_pt = int(beat_df.iloc[-1].pLoc)
    ahr_df['espts'] = np.arange(first_beat_pt, last_beat_pt)

    # interpolate rr
    rrx = abeat_df.pLoc[:-1].values        # rr locations
    rry = abeat_df.rr[:-1].values         # rr values
    # f = interp1d(rrx, rry, kind='cubic', bounds_error=False, fill_value="extrapolate")
    f = interp1d(rrx, rry, kind='linear')
    ahr_df['rrInterpol'] = f(ahr_df['espts'])
    # interpolate rrDiff
    rry = abeat_df.rrDiff[:-1].values
    # f = interp1d(rrx, rry, bounds_error=False, fill_value="extrapolate")
    f = interp1d(rrx, rry, kind='linear')
    ahr_df['rrInterpolDiff'] = f(ahr_df['espts'])
    # interpolate rrSqrDiff
    rry = abeat_df.rrSqDiff[:-1].values
    # f = interp1d(rrx, rry, bounds_error=False, fill_value="extrapolate")
    f = interp1d(rrx, rry, kind='linear')
    ahr_df['rrInterpolSqDiff'] = f(ahr_df['espts'])
    return ahr_df

def plot_rr(ahr_df, param, HR=False):
    """
    plot RR vs pt values + rrSqDiff
    input :
        hr_df = pdDataFrame
        params : dict containing 'fs' as key
    """
    fs = param['fs']

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(211)
    ax.set_title('RR duration')
    xvals = ahr_df.espts.values/fs/60
    ax.plot(xvals, ahr_df.rrInterpol.values)
    ax.set_ylabel('RR (msec)')
    ax.set_xlabel('min (fs  ' + str(fs) + ')')
    ax.grid()
    lims = ahr_df.rrInterpol.quantile([0.01, 0.99])
    ax.set_ylim(lims)
    ax2 = fig.add_subplot(212, sharex=ax)
    if HR:
        ax2.set_title('heart rate')
        yvals = 1/ahr_df.rrInterpol.values*60*1000
        ax2.plot(xvals, yvals, '-g')
        lims = (np.quantile(1/ahr_df.rrInterpol.values*60*1000, q=0.01),
                np.quantile(1/ahr_df.rrInterpol.values*60*1000, q=0.99))
        ax2.set_ylim(lims)
    else:
        ax2.set_title('RR sqVariation')
        ax2.plot(xvals, ahr_df.rrInterpolSqDiff.values, '-g')
        lims = (0, ahr_df.rrInterpolSqDiff.quantile(0.98))
        ax2.set_ylim(lims)
    for loca in ['top', 'right']:
        ax.spines[loca].set_visible(False)
        ax2.spines[loca].set_visible(False)
#    file = os.path.basename(filename)
    fig.text(0.99, 0.01, param['file'], ha='right', va='bottom', alpha=0.4)
    fig.text(0.01, 0.01, 'cdesbois', ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    return fig

#%% heart rate
def plot_agreement(trend_data, ekgdf):
    """ plot ip1HR & hr to check agreement """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(trend_data.hr)
    axt = ax.twiny()
    axt.plot(1/ekgdf.rrInterpol*60*1000, 'r-')
    return fig

def replace_hr_in_monitorTrend(trend_data, ekgdf):
    """ append an 'hr' column in the dataframe """
    df = pd.DataFrame()
    df['hr'] = 1/ekgdf.rrInterpol*60*1000
    df['datetime'] = monitorWave.data.datetime
    df = df.set_index('datetime').resample('5s').mean()
    #tdata = monitorTrend.data
    #df.reset_index(inplace=True)
    #tdata['hr'] = df.hr
    trend_data['hr'] = df.reset_index()['hr']
    return trend_data

def append_rr_to_monitorWave(wave_data, ekgdf):
    """ append an 'hr' column in the dataframe """
    wave_data['rr'] = ekgdf['rrInterpol']
    return wave_data


################################

if __name__ == '__main__':
    # view if files are loaded
    print(check())
    #%detect beats after record_main for monitorWave
    params = monitorWave.param
    #data = monitorWave.data
    # build a dataframe to work with (waves)
    ekg_df = pd.DataFrame(monitorWave.data.wekg)

    #low pass filtering
    ekg_df['wekg_lowpass'] = wf.fix_baseline_wander(ekg_df.wekg,
                                                    monitorWave.param['fs'])
    # beats locations (beat based dataFrame)
    beat_df = detect_beats(ekg_df.wekg_lowpass, params)
    #plot
    figure = plot_beats(ekg_df.wekg_lowpass, beat_df)

    #fs=300
    beat_df = compute_rr(beat_df, monitorWave.param)
    hr_df = interpolate_rr(beat_df)
    figure = plot_rr(hr_df, params, HR=True)

#%% merge the wave and treated df
    # loc of the first beat
    first_beat_loc = int(beat_df.pLoc.iloc[0] - ekg_df.index.min())
    #append to ekg_df (ie contain ekg, ekg_lowpass,
    ekg_df = pd.concat([ekg_df, hr_df.shift(first_beat_loc)], axis=1, join='outer')

    #del first_beat_loc
    #del hr_df
    #del beat_df
    # NB HR is 1/ekg_df.rrInterpol*60*1000

    figure = plot_agreement(monitorTrend.data, ekg_df)
#%%
    monitorTrend.data = replace_hr_in_monitorTrend(monitorTrend.data, ekg_df)
    monitorWave.data = append_rr_to_monitorWave(monitorWave.data, ekg_df)
