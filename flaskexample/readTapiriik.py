# readTapiriik.py
#
# read in the Garmin .tcx data from Tapiriik and run some statistics with
# the weather
#
# LKS, June 2016, part of the Insight Data Science Program
#
# import
import numpy as np
import tcxparser
import os
import glob
from geopy.geocoders import Nominatim
#os.chdir('flaskexample')
import webScrapeFunctions as WS
import plottingFunctions as pf
#os.chdir('..')
import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import sys
#
#

def loadData(username, password, loc2, dataModified=[]):

   tableName=username

   con = None
   con = psycopg2.connect(dbname='postgres', user='loisks', host='localhost', password='poppy33')

   # make it create individual data base
   ActiveLabels=['Date', 'ActiveTime', 'Location', 'Distance', 'Calories']
   con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
   con2 = psycopg2.connect("dbname='endomondo' user='loisks'")  
   cur=con2.cursor()

   # get all the files
   #os.chdir("/Users/loisks/Documents/InsightProject/Hosting/flaskexample/Jimmy")
   #fileList=glob.glob('*.tcx')

   try:
     print('*****'+tableName+'*****')
     query='SELECT * FROM '+tableName
     cur.execute(query) # access data currently in data base 
     prevData=cur.fetchall()
     startDate=datetime.datetime.strftime(prevData[-1][0]+datetime.timedelta(days=1), '%Y-%m-%d')

   except:
      
      con2.rollback()
      con2 = psycopg2.connect("dbname='endomondo' user='loisks'")  
      cur=con2.cursor()
      try:
            qq="DROP TABLE " +username
            cur.execute(qq)
      except:
            print("didn't need to drop the table")
      con2.rollback()
      con2 = psycopg2.connect("dbname='endomondo' user='loisks'")
      cur=con2.cursor()
      print("*********Creating a New Table********")
      query2=" CREATE TABLE "+ tableName +" (Date TIMESTAMP, ActiveTime REAL, \
        Distance REAL, Calories REAL, \
        meanTemperature REAL, maxTemperature REAL, minTemperature REAL,precipitation REAL, wind REAL); "
      cur.execute(query2)
   if dataModified!=[]:

      try:
       for iFile in range(len(dataModified['Date'])):
	curDate =datetime.datetime.strptime( dataModified['Date'][iFile], \
'%Y-%m-%d')
	location=dataModified['Location'][iFile]
	workoutTime=dataModified['ActiveTime'][iFile]
	calories=dataModified['Calories'][iFile]
	distance=dataModified['Distance'][iFile]
        dateLink=datetime.datetime.strftime(curDate,'%d'+'.'+'%m'+'.'+'%Y')    
        weatherData=WS.getWeatherData(curDate, location)  # returns a list
        print('Acquired Weather Data')
        
        #
        #
        query = 'INSERT INTO '+tableName+' (DATE, ACTIVETIME, DISTANCE, \
        CALORIES, \
        MEANTEMPERATURE, MAXTEMPERATURE, MINTEMPERATURE,\
        PRECIPITATION, WIND) VALUES (%s, %s, %s, %s,\
        %s, %s, %s, %s, %s);'
        data=( curDate, workoutTime,distance, calories, \
               weatherData[0], \
               weatherData[1], weatherData[2], weatherData[3], weatherData[4])
        print data
        cur.execute(query,data)
        con2.commit()
      except:
         print iFile
# 
###
   activeList=['ActiveTime',  'Distance', 'Calories']
   weatherList=['MeanTemperature', 'MaxTemperature', 
        'MinTemperature','Precip', 'Wind']
   activeLabels=['Active Time [s]','Distance [m]',  'Calories']
   weatherLabels=['Average Temperature [F]', \
        'Max Temperature [F]', 'Min Temperature [F]',\
                  'Precipitation [inches]', \
        'Wind [mph]']
   # loc2 is for preditions
   data=pf.plotter(activeList, weatherList, activeLabels, weatherLabels, \
                      'endomondo', tableName, loc2,color='#FFA500', nn=15 \
                      )
   cals=data.CalPredict
   bestCorr=data.bestCorr
   bestDay=data.bestDay
   os.chdir("..")
   return(cals,bestCorr,bestDay)
   
