#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 14:41:15 2022

@author: cdesbois
"""
from PyQt5.QtWidgets import QInputDialog, QWidget


def select_wave_to_plot(waves: list, num=1) -> str:
    """
    select the wave trace to plot

    Parameters
    ----------
    waves : list
        list of available waves traces
    num : TYPE, optional
        index of the waves in the plot (1 or 2)
    Returns
    -------
    str
        wave name
    """

    global APP
    if num == 1:
        question = "choose first wave"
    if num == 2:
        question = "do you want a second one ?"
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    wave, ok_pressed = QInputDialog.getItem(widg, "select", question, waves, 0, False)
    if ok_pressed and wave:
        selection = wave
    else:
        selection = None
    return selection
