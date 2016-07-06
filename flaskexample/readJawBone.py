# readJawBone.py
#
# read in the JawBoneData in csv format
# process it
#
# LKS, June 2016 part of Insight Program
#
#
import datetime
import numpy as np
import os
import webScrapeFunctions as WS
import plottingFunctions as pf
import glob
import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import sys

def loadData(username, password,location, data=[]):
    #
    # the usual suspects for loading in data
    # data = the file to be added to the data base 
    #
    tableName=username
    con = None
    con = psycopg2.connect(dbname='postgres', user='loisks', host='localhost', password=password)
    #cur = con.cursor()
    # make it create individual data base
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    con2 = psycopg2.connect("dbname='jawbone' user='loisks'")  
    cur=con2.cursor()

    #
    # try to access user data - if none then create a new table of their data
    # need to check this first 
    # 
    try:
        # build on the data set already there
        query1="SELECT * FROM "+tableName
        cur.execute(query1) # access data currently in data base 
        prevData=cur.fetchall()
        #startDate=prevData[-1][0]+datetime.timedelta(days=1)

    except: # if there is no data base 
        con2.rollback()
        con2 = psycopg2.connect("dbname='jawbone' user='loisks'")  
        cur=con2.cursor()
        # just in case a data base is already there
        #try:
        #    qq="DROP TABLE " +username
        #    cur.execute(qq)
        #except:
        #    print("didn't need to drop the table") 
        query2=" CREATE TABLE "+tableName+" (Date TIMESTAMP, Steps REAL, Distance REAL, Calories REAL, ActiveTime REAL, Sleep REAL,  meanTemperature REAL, maxTemperature REAL, minTemperature REAL,precipitation REAL, wind REAL); "
	print('MAKES IT TO CHECKPOINT #2 LO')
        cur.execute(query2)
        
    #
    # first test to see if there is a file
    print data
    #stop
    if data != []:
        try:
            startDate=prevData[-1][0]+datetime.timedelta(days=1)
            print("START DATE IS: " + str(startDate))
            iStart=min(range(len(data['Dates'][1:])), key=lambda i: abs(data['Dates'][1:][i]-startDate))+1

        except:
	   print("First of year")
           iStart=1
#            print instartDate
#            startDate=datetime.datetime.strptime(i, '%Y%m%d')
        # then there is a file to be added to the data base
        params=['Dates', 'Steps', 'Distance', 'Calories', 'ActiveTime', 'SleepTime']
    #

        print iStart

        # correct for nans
        data['SleepTime']=np.array(data['SleepTime'])
        data['SleepTime'][np.isnan(data['SleepTime'])]=-1000
#
# set up Jawbone table
        for iDate in range(iStart, len(data['Dates'])):
            curDate=data['Dates'][iDate]
            dateLink=datetime.datetime.strftime(curDate,'%d'+'.'+'%m'+'.'+'%Y')
            try:
                weatherData=WS.getWeatherData(curDate, location)  # returns a list
                
                      
          #      print('Acquired Weather Data')    
                
                query = 'INSERT INTO '+username+' (DATE,STEPS, DISTANCE, CALORIES,\
                ACTIVETIME, SLEEP, MEANTEMPERATURE, MAXTEMPERATURE, MINTEMPERATURE,\
                PRECIPITATION, WIND) VALUES (%s, %s, %s, %s,\
                %s, %s, %s, %s, %s, %s, %s);'
                
                
                dataC=( curDate,float(data['Steps'][iDate]),\
                       float(data['Distance'][iDate]),\
                       float(data['Calories'][iDate]),\
                       float(data['ActiveTime'][iDate]),\
                       float(data['SleepTime'][iDate]), weatherData[0], \
                       weatherData[1], weatherData[2], weatherData[3], weatherData[4])
                print dataC
                cur.execute(query,dataC)
                con2.commit()
            except:
                print("bad data for " + str(curDate) )
                

    Parameters=['Steps', 'Distance', 'Calories', \
                    'ActiveTime','Sleep','MeanTemperature', 'MaxTemperature', \
                    'MinTemperature','Precip', 'Wind']
    Labels=['Steps','Distance [m]',  'Calories','Active Time [hours]',  \
        'Sleep [Hours]', 'Average Temperature [F]', \
        'Max Temperature [F]', 'Min Temperature', 'Precipitation [inches]', \
        'Wind [mph]']
    activeList=['Steps', 'Distance', 'Calories','ActiveTime', \
               'Sleep']
    weatherList=['MeanTemperature', 'MaxTemperature', 
            'MinTemperature','Precip', 'Wind']
    activeLabels=['Steps', 'Distance [km]', 'Calories','Active Time [hours]',  \
            'Sleep [Hours]']
    weatherLabels=['Average Temperature [F]', \
               'Max Temperature [F]', 'Min Temperature', 'Precipitation [inches]', \
               'Wind [mph]']

    results=pf.plotter(activeList, weatherList, activeLabels, weatherLabels, \
                       'jawbone', username, location, color='green')
    cals=results.CalPredict
    bestCorr=results.bestCorr
    bestDay=results.bestDay
    
    return(cals,bestCorr,bestDay) 











    
#os.chdir('RachaelTomasino')
#years=glob.glob('*.csv')
#dataYears={}
#time={}
#for i in years:
#    dataYears[i[0:4]]=np.swapaxes(np.genfromtxt(i, delimiter=','), 1, 0)
#    # convert to date strings in form YYYYmmdd
#    temp=[ datetime.datetime.strptime(str(int(dataYears[i[0:4]][0][j])), '%Y%m%d') \
#          for j in range(1,len(dataYears[i[0:4]][0]))]
#    dataYears[i[0:4]][0]=list( dataYears[i[0:4]][0])
#    time[i[0:4]]=[np.nan]+ temp
#
# now get the data that matters 
# 
# 41 is steps
# 37 is distance in meters
# 43 is calories
# 35 is active time in seconds
# 48 is sleep time
#
#
#params=['Dates', 'Steps', 'Distance', 'Calories', 'ActiveTime', 'SleepTime']
#indicies=[0,41, 37, 43, 35, 48]
## now have to adjust for the right dates
#dataModified={}
#for iP in range(len(params)):
#    dataModified[params[iP]]=[]
#
#for iyear in years:
#    goodvals= np.isnan(dataYears[iyear[0:4]][41]) # get rid of the nans
#    for index in range(1,len(indicies)):
#        dataModified[params[index]]+=list(dataYears[iyear[0:4]][indicies[index]][~goodvals])
#    dataModified['Dates']+=list(np.array(time[iyear[0:4]])[~goodvals])
#    
## set up data base
#
#con = None
#con = psycopg2.connect(dbname='postgres', user='loisks', host='localhost', password=password)
##cur = con.cursor()
## make it create individual data base
#con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#con2 = psycopg2.connect("dbname='jawbone' user='loisks'")  
#cur=con2.cursor()

#try:
#        # build on the data set already there
#        cur.execute("SELECT * FROM "+tableName) # access data currently in data base 
#        prevData=cur.fetchall()
#        startDate=prevData[-1][0]+datetime.timedelta(days=1)
#
#except: # if there is no data base 
#       
#        con2 = psycopg2.connect("dbname='jawbone' user='loisks'")  
#        cur=con2.cursor()
#        cur.execute(" CREATE TABLE RACHAEL (Date TIMESTAMP, Steps REAL, Distance REAL, Calories REAL, ActiveTime REAL, Sleep REAL,  meanTemperature REAL, maxTemperature REAL, minTemperature REAL,precipitation REAL, wind REAL); ")
#        startDate=dataModified['Dates'][0]


#iStart=min(range(len(dataModified['Dates'])), key=lambda i: abs(dataModified['Dates'][i]-startDate))
#print iStart
#
# correct for nans
#dataModified['SleepTime']=np.array(dataModified['SleepTime'])
#dataModified['SleepTime'][np.isnan(dataModified['SleepTime'])]=-1000
##
## set up Jawbone table
#for iDate in range(iStart, len(dataModified['Dates'])):
#    curDate=dataModified['Dates'][iDate]
#    dateLink=datetime.datetime.strftime(curDate,'%d'+'.'+'%m'+'.'+'%Y')    
#    weatherData=WS.getWeatherData(curDate, location)  # returns a list
#    print('Acquired Weather Data')    
#    
#    # add directly to data base
#    #dateq=datetime.datetime.strftime(curDt, '%Y%m%d')
#    query = 'INSERT INTO RACHAEL (DATE,STEPS, DISTANCE, CALORIES, ACTIVETIME, SLEEP,\
#    MEANTEMPERATURE, MAXTEMPERATURE, MINTEMPERATURE,\
#    PRECIPITATION, WIND) VALUES (%s, %s, %s, %s,\
#    %s, %s, %s, %s, %s, %s, %s);'
#    data=( curDate,float(dataModified['Steps'][iDate]),\
#           float(dataModified['Distance'][iDate]),\
#           float(dataModified['Calories'][iDate]),\
#           float(dataModified['ActiveTime'][iDate]),\
#           float(dataModified['SleepTime'][iDate]), weatherData[0], \
#           weatherData[1], weatherData[2], weatherData[3], weatherData[4])
#    print data
#    cur.execute(query,data)
#    con2.commit()
#
# 
#
# fetch the data
#cur.execute("SELECT * FROM RACHAEL") # access data currently in data base 
#AllUserData=cur.fetchall()
#Parameters=['Steps', 'Distance', 'Calories', \
#        'ActiveTime','Sleep','MeanTemperature', 'MaxTemperature', \
#        'MinTemperature','Precip', 'Wind']
#Labels=['Steps','Distance [m]',  'Calories','Active Time [hours]',  \
#        'Sleep [Hours]', 'Average Temperature [F]', \
#        'Max Temperature [F]', 'Min Temperature', 'Precipitation [inches]', \
#        'Wind [mph]']
#dates=pd.DatetimeIndex(np.swapaxes(AllUserData, 1,0)[0])
#dataOnly=np.swapaxes(np.swapaxes(AllUserData,1,0)[1:],1,0)
#df=pd.DataFrame(dataOnly, columns=Parameters)
#
#activeList=['Steps', 'Distance', 'Calories', 'ActiveTime', 'Sleep']
#weatherList=['MeanTemperature', 'MaxTemperature', 
#        'MinTemperature','Precip', 'Wind']
#activeLabels=['Steps', 'Distance [m]', 'Calories', \
#              'Active Time [Hours] ', 'Sleep [Hours]']
#weatherLabels=['Average Temperature [F]', \
#        'Max Temperature [F]', 'Min Temperature [F]', 'Precipitation [inches]', \
#        'Wind [mph]']
## get rid of the zeros in the polar loop data 
#for iParam in range(len(activeList)):
#    df[activeList[iParam]]=df[activeList[iParam]].replace(0,np.nan)
#
#
## clean the entire data frame!
#df=df.replace(1e-31, np.nan)
#df['Precip'][df['Precip']>5]=np.nan # change this later?
#
#df['Dates']=df.index
#df['week_days']=dates.dayofweek
#
#
# BOX and WHISKER PLOTS
#subdirWhisker='Statistics/BoxWhisker'
#for iParam in range(len(Parameters)):
#    x=df.pivot(index='Dates', columns='week_days', values=Parameters[iParam])
#    ax=x.plot(kind='box', fontsize=15)
#    ax.set_xlabel('Days of Week', fontsize=15)
#    ax.set_ylabel(Labels[iParam], fontsize=15)
#    ax.set_xticklabels(['M', 'Tu', 'W','Th', 'F', 'S',  'S'])
#    plt.draw()
#    if not os.path.exists(subdirWhisker):
#        os.umask(0) # unmask if necessary
#        os.makedirs(subdirWhisker) 
#    os.chdir(subdirWhisker)#
#    fig = ax.get_figure()
#    fig.savefig('boxwhisker_'+Parameters[iParam]+'_daysofweek.png')
#    os.chdir('..')
#    os.chdir('..')
#    #
#
#for iP in range(len(activeList)):
#    for j in range(len(weatherList)):
#        # linear regression
#        pf.statsScat(np.array(df[activeList[iP]]),
#                     np.array([float(df[weatherList[j]][i]) for i in \
#                               range(len(df[weatherList[j]]))]), \
#                     activeLabels[iP], weatherLabels[j], 1e100, 1, '', \
#                     'Statistics/Scatter', activeList[iP]+'_'+\
#                     weatherList[j]+'_scatter.png')
#        corr=df[activeList[iP]].corr(df[weatherList[j]])
#        print('R = '+str(corr)+' for '+activeList[iP]+' and '+weatherList[j])
#        os.chdir('..')
#        
#
#
#
#WeekdayList=['M', 'Tu', 'W','Th', 'F', 'S',  'S']
#for iParam in range(len(activeList)):
#  for j in range(len(weatherList)):
#    x=df.pivot(index='Dates', columns='week_days', values=activeList[iParam])
#    y=df.pivot(index='Dates', columns='week_days', values=weatherList[j])
#    #
#    # scatter based on day of week
#    
#    for W in range(len(WeekdayList)):
#        pf.statsScat(x[W],y[W], activeLabels[iParam], weatherLabels[j],\
#                     1e100, 1, '', \
#                     'Statistics/ScatterWeekday', WeekdayList[W]+'_'+ \
#                     activeList[iParam]+'_'+\
#                     weatherList[j]+'_scatter.png')
#        corr=x[W].corr(y[W])
#        print('For '+ WeekdayList[W]+' R = '+str(corr)+' for '+activeList[iParam]+' and '+weatherList[j])
#        os.chdir('..')
        
