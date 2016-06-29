# trackerFuncs.py
#
# Functions for the Endomondo, Jawbone, and Loop data
#
# LKS June 2016, part of Insight Data Science Project
#
import numpy as np
import tcxparser
import os
import glob
from geopy.geocoders import Nominatim
#import webScrapeFunctions as WS
import plottingFunctions as pf
import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import matplotlib.pyplot as plt
#
#
def endomondo(username):
    #
    # will fetch all the endomondo data
    # and make the plots, putting them into static
    # for data base
    activeList=['ActiveTime',  'Distance', 'Calories']
    weatherList=['MeanTemperature', 'MaxTemperature', 
        'MinTemperature','Precip', 'Wind']
    activeLabels=['Active Time [s]','Distance [m]',  'Calories']
    weatherLabels=['Average Temperature [F]', \
        'Max Temperature [F]', 'Min Temperature [F]', \
                   'Precipitation [inches]', 'Wind [mph]']
    pf.plotter(activeList, weatherList, activeLabels, weatherLabels, \
               'tapiriik', username, \
               dirpath='/Users/loisks/Documents/Insight/Hosting/flaskexample/static/')
    return(None)
