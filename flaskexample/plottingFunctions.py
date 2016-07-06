# plottingFunctions.py
#
# make it easy to run stats and make the plots without
# bogging down the dataStats.py script
#
# LKS, June 2016 part of Insight
#
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats 
import os
import psycopg2
import sys
import pandas as pd
import numpy as np
from scipy.stats import kendalltau
import seaborn as sns
from sklearn import datasets, linear_model
from sklearn.neighbors import KNeighborsClassifier
import webScrapeFunctions as WS
import datetime
 

# think about turning this into a class for more mobility and to share the data
# frame throughout
# quick useful definition
def reject_outliers(data, m=2):
        data[abs(data - np.mean(data)) > m * np.nanstd(data)]=np.nan
        return data

class plotter():
    # class to take the data from the SQL data base and do things with it


    def dataFetch(self):
        #
        # connect to the data base and pull from table
        con2 = psycopg2.connect("dbname="+self.dbname+" user='loisks'")  
        cur=con2.cursor()
        query="SELECT * FROM "+str(self.tableName)
        cur.execute(query)
        #
        # get all the data 
        AllUserData=cur.fetchall()
        #
        # get the dates 
        self.dates=pd.DatetimeIndex(np.swapaxes(AllUserData, 1,0)[0])
        dataOnly=np.swapaxes(np.swapaxes(AllUserData,1,0)[1:],1,0)
        self.df=pd.DataFrame(dataOnly, columns=self.Parameters)
        return(None)

    def dataRun(self):
        # make the plots
        self.dataFetch()
        #
        # this next stretch cleans the whole data set 
        # 
        # replace the 0's with nanas 
        for iParam in range(len(self.activeList)):
            self.df[self.activeList[iParam]]=\
                        self.df[self.activeList[iParam]].replace(0,np.nan)
        self.df=self.df.replace(1e-31,np.nan)
        self.df['Wind']=self.df['Wind'].replace(0,np.nan)
        print self.df['Precip']
        self.df['Dates']=self.df.index
        self.df['week_days']=self.dates.dayofweek
        
        #
        # code that needs to be in place because of Jimmy's hatred of
        # Mondays
        godDamnMondays=['M', 'Tu', 'W','Th', 'F', 'S',  'S']
        FullLabels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', \
                    'Saturday', 'Sunday']
        godDamnIndexes=range(7)
        tickLabels=[]
        tickLabelsFull=[]
        indices=[]
        #
        # variable naming convention because Jimmy hates running on
        # mondays for the enomondo data 
        for iDamn in godDamnIndexes:
            if iDamn in self.dates.dayofweek:
                tickLabels.append(godDamnMondays[iDamn])
                tickLabelsFull.append(FullLabels[iDamn])
                indices.append(iDamn)
        
        #
        # now call the plotting functions
        # Box and Whisker
        
        self.boxAndWhisker(tickLabels)
        #
        #
        strongCorrR=[]
        strongCorrLabels=[]
        for iP in range(len(self.activeList)):
            for j in range(len(self.weatherList)):
            
                self.statsScat(np.array(self.df[self.activeList[iP]]), \
                np.array([float(self.df[self.weatherList[j]][i]) for i in \
                               range(len(self.df[self.weatherList[j]]))]), \
                self.activeLabels[iP], self.weatherLabels[j], 1e100, 1, '', \
                    '/root/Hosting/flaskexample/static/'+self.tableName, self.activeList[iP]+'_'+\
                     self.weatherList[j]+'_scatter')
                corr=self.df[self.activeList[iP]].corr(self.df[self.weatherList[j]])
                print('R = '+str(corr)+' for '+self.activeList[iP]+\
                      ' and '+self.weatherList[j])
                strongCorrR.append(corr)
                strongCorrLabels.append(self.weatherLabels[j])
                
        #        
        #
        #
        # and by week day
        WeekdayList=['M', 'Tu', 'W','Th', 'F', 'S',  'S']
        bestday=[]

        for W in indices:
            bestday.append(np.nanmedian(self.df.pivot(index='Dates', columns='week_days', values='Calories')[W]))
                        
        for iParam in range(len(self.activeList)):
            for j in range(len(self.weatherList)):
                x=self.df.pivot(index='Dates', columns='week_days',\
                           values=self.activeList[iParam])
                y=self.df.pivot(index='Dates', columns='week_days',\
                           values=self.weatherList[j])
                #
                # scatter based on day of week
                for W in indices:
                    
                    self.statsScat(x[W],y[W], self.activeLabels[iParam], \
                                 self.weatherLabels[j],\
                                 1e100, 1, '', \
                                 '/root/Hosting/flaskexample/static/'+\
                                   self.tableName, godDamnMondays[W]+'_'+ \
                                 self.activeList[iParam]+'_'+\
                                 self.weatherList[j]+'_scatter')
                    corr=x[W].corr(y[W])
                    print('For '+ godDamnMondays[W]+' R = '+str(corr)+' for '+\
                          self.activeList[iParam]+' and '+self.weatherList[j])

       
        indexMax=np.where(np.array(strongCorrR) == np.nanmax(strongCorrR))[0]
        dayMax=np.where(np.array(bestday)==np.nanmax(bestday))[0]

        self.bestCorr=strongCorrLabels[indexMax[0]]
        self.bestDay=tickLabelsFull[dayMax[0]]
      
        return(None) # nothing to return! Again!                     
        
    def statsScat(self,df1,df2, xlabel,ylabel,xmin, xmax, xscale,subdir,\
              filename, marker='x', s=40, c='Red'):
        #
        # df1 = x param
        # df2 = y param
        # xlabel = x label
        # ylabel = y label
        # xmin = xmin, 1e100 if you don't want to set this
        # xmax = xmax  
        # xscale = 'log' or anything but
        # subdir = directory to save in
        # filename = filename
        #
        # compute linear regression
        # seaborn plots?
       
        try:
             
             df1=reject_outliers(df1); df2=reject_outliers(df2)
             
             mask = ~np.isnan(df1) & ~np.isnan(df2)
             slope,intercept,rval, pval, std=stats.linregress(df1[mask], df2[mask])
             #print slope, intercept
             line=np.array(sorted(df1[mask]))*slope+intercept

             sns.set(style="ticks", font='Arial')
             sns.set_context("talk")
        
             jp=sns.jointplot(df2[mask], df1[mask], kind="reg", stat_func=kendalltau, color=self.color)
             jp.set_axis_labels(ylabel, xlabel)
             #jp.set(xlabel=xlabel,ylabel=ylabel)
             #if not os.path.exists('statistics/SeaBorn'):
             #    os.umask(0) # unmask if necessary
             #    os.makedirs('statistics/SeaBorn') 
             os.chdir('/root/Hosting/flaskexample/static/'+self.tableName)
             jp.savefig("seaborn_"+filename+".png")
             
             fig=plt.figure()
             ax=fig.add_subplot(111)
             ax.scatter(df1, df2, marker=marker, s=s, c=c)
             ax.set_xlabel(xlabel)
             ax.set_ylabel(ylabel)
             ax.plot(sorted(np.array(df1[mask])),line, lw=2, c='Blue')
             if xscale=='log':
                 ax.set_xscale('log')
             if xmin != 1e100:
                 ax.set_xlim(xmin,xmax)
             plt.draw()
             #os.chdir(subdir)
             os.chdir('/root/flaskexample/static/'+self.TableName)
             fig.savefig(filename+'.png')
             
        except:
   
            print('Not enough data!')
        return(None) 

    def boxAndWhisker(self,tickLabels, subdirName='Statistics/BoxWhisker'):
       # Parameters = List of value Names
       # df = the data frame
       # Labels = What is the parameter being plotted on box and whisker
       # subdirName = where to save the data
       #
       #
       for iParam in range(len(self.Parameters)):
           x=self.df.pivot(index='Dates', columns='week_days', \
                           values=self.Parameters[iParam])
           ax=x.plot(kind='box', fontsize=15)
           ax.set_xlabel('Days of Week', fontsize=15)
           ax.set_ylabel(self.Labels[iParam], fontsize=15)
           ax.set_xticklabels(tickLabels)
           plt.draw()
           #if not os.path.exists(subdirName):
           #    os.umask(0) # unmask if necessary
           #    os.makedirs(subdirName) 
           #os.chdir(subdirName)#
           os.chdir('/root/Hosting/flaskexample/static/'+self.tableName)
           fig = ax.get_figure()
           fig.savefig('boxwhisker_'+self.Parameters[iParam]+'_daysofweek.png')


    def barPlotbins(self, data, bins, xlabel,ylabel,xticklabels,subdirName,\
                    saveFile):
        #
        # data = data to be plotted, should be 1 d array
        # bins = bin ranges
        fig=plt.figure()
        fig.subplots_adjust(bottom=0.15, left=0.16, right=0.9)
        font = {'family' : 'normal',
                      'weight' : 'bold',
                      'size'   : 22}
        plt.rc('font', **font)
        ax=fig.add_subplot(111)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
       
        data[np.isnan(data) == True] = 0

        ax.bar(bins,data, align='center', color='Blue', width=5)
        ax.set_xticks(xticklabels)
        ax.set_xticklabels([str(i) for i in xticklabels])
        #if not os.path.exists(subdirName):
        #       os.umask(0) # unmask if necessary
        #       os.makedirs(subdirName) 
        #os.chdir(subdirName)#
        os.chdir('/root/Hosting/flaskexample/static/'+self.tableName)
        fig.savefig(saveFile+'.png')
        #os.chdir('..'); os.chdir('..')
        return(None)

        
    def weatherBins(self):
        #
        # group the mean temperature data and report back
        # which temperatures highest calories occured at
        #
        temp=np.array(self.df['MeanTemperature'])
        weth=np.array(self.df['Wind'])
        noTempBins=15
        tempMin=20
        tempMax=90
        Trange=np.linspace(tempMin, tempMax, noTempBins) # 29 bins
        Wrange=np.linspace(0,70,36) # 36 bins  
        tempdict= [ [] for i in range(noTempBins)]
        winddict= [ [] for i in range(36)]
        TcalorieDict = [ 0 for j in range(noTempBins)]
        WcalorieDict = [ 0 for j in range(36)]

        TcalorieDict[0]=np.nanmedian(self.df['Calories'][temp<tempMin])
        TcalorieDict[-1]=np.nanmedian(self.df['Calories'][temp>tempMax])
        WcalorieDict[0]=np.nanmedian(self.df['Calories'][weth<0])
        WcalorieDict[-1]=np.nanmedian(self.df['Calories'][weth>70])

        for iT in range(1,noTempBins-1):
            TcalorieDict[iT]=np.nanmedian(self.df['Calories']\
                              [(temp>=Trange[iT]) & (temp<Trange[iT+1])])

        for iW in range(1,35):
            WcalorieDict[iW]=np.nanmedian(self.df['Calories']\
                              [(temp>=Wrange[iW]) & (temp<Wrange[iW+1])])

        #
        # make two bar plots
        print TcalorieDict
        self.barPlotbins( np.array(TcalorieDict),Trange, 'Temperature [F]','Calories', \
                          Trange[::3],'Statistics/Barplots',\
                          'temperature_calories_barplot')
       
        self.barPlotbins( np.array(WcalorieDict),Wrange, 'Wind [mph]','Calories', \
                          Wrange[::6],'Statistics/Barplots',\
                          'wind_calories_barplot')

      
        
        return(None)

    def predictor(self):
        #
        # get the correlation coefficients and create a weight
        # sum from there
        #
        # df = data frame
        # date = datetime to be checked 
        #
        df=self.df
        curTime=datetime.datetime.now()
        location=self.location
        
        # note python 0 = Monday
        weatherDAT=WS.getWeatherData(curTime, location)
        print('*************')
        print('WEATHER DATA IS: ' + str(weatherDAT))
        print('*************')
        WeekdayList=['M', 'Tu', 'W','Th', 'F', 'S',  'S']
        curWeekday=curTime.weekday()
        #
        # fetch the weather data
        
        inputT=weatherDAT[0]
        inputP=weatherDAT[3]
        inputW=weatherDAT[4]
       
        from sklearn.neighbors import KNeighborsClassifier

        vars=['MeanTemperature','Wind','Precip']
        inputs=[inputT, inputP, inputW]
        

        # first get the kendalls tau
        KendallTaus=[]
        sPredict=[]
        
                        
        for iVar in range(len(vars)):
            x=df.pivot(index='Dates', columns='week_days',\
                            values=vars[iVar])
            y=df.pivot(index='Dates', columns='week_days',\
                            values='Calories')

            
            y[y==0]=np.nan
            try:
                    mask = ~np.isnan(x[curWeekday]) & ~np.isnan(y[curWeekday])
                    
                    # now get the nearest neighbor 
                    neigh = KNeighborsClassifier(n_neighbors=self.nn, weights='distance')
            
                    xtemp=np.array(x[curWeekday][mask]); ytemp=np.array(y[curWeekday][mask])
                    print("ytemp is: " +str(ytemp))
                    print("xtemp is: " + str(xtemp))
                    # print(neigh)
                    KendallTaus.append(kendalltau(xtemp,ytemp)[0])
                    ytemp=np.asarray(ytemp,dtype="|S6")
                    xtemp=np.asarray([ [xtemp[i]] for i in range(len(xtemp))], dtype="|S6")
            except:
                    xtemp=0
                    ytemp=0
            
            try:
                            neigh.fit(xtemp,ytemp)
                            sPredict.append(neigh.predict([[inputs[iVar]]]))
                            print sPredict
            except:

                print('Not enough points!')
        #
        # get the sum total
        TauSum=np.nansum(np.abs(KendallTaus))
        #
        # normalize and sum
        CalPredict=0
        print(sPredict)
        for iVar in range(len(vars)):
            try:
               
                temp11=float(sPredict[iVar][0])*np.abs(float(1.0*KendallTaus[iVar]))/(float(1.0*TauSum))
               
                if np.isnan(temp11) != True:

                        CalPredict+= temp11
            except:
                print("Gah those data points!")
        try:
            print "Predicted Calories with these conditions: " + str(CalPredict)
            self.CalPredict=CalPredict
        except:
            print "Not Enough Data"
            self.CalPredict=CalPredict
        return(None)

 
           
    def __init__(self, activeList, weatherList, activeLabels,\
                 weatherLabels, dbname, tableName, location, validation=0, \
                 color="#9013e7", nn=15):
        #
        # *** all the inputs need to be lists!! *** 
        # activeList = Labels to pull from SQL
        # weatherList = weather labels to pull from SQL
        # activeLabels = axes labels for Activity
        # weatherLabels = axes labels for weather
        # dbname = data base name
        # tableName = table name (JIMMY!)
        # location = location string
        # validation = 0 if not validation, otherwise gives a datetime to test

        Parameters=activeList+weatherList
        Labels=activeLabels+weatherLabels
        activeList=['Calories']
        weatherList=['MeanTemperature', 'Precip', 'Wind']
        activeLabels=['Calories']
        weatherLabels=['Average Temperature [F]', 'Precipitation [inches]', 'Wind [mph]']
        #
        # put it in data base
        self.Parameters=Parameters
        self.Labels=Labels
        self.activeList=activeList
        self.weatherList=weatherList
        self.activeLabels=activeLabels
        self.weatherLabels=weatherLabels
        self.dbname=dbname
        self.tableName=tableName
        self.location = location
        self.validation = validation
        self.color=color
        self.nn=nn
        
        subdir='/root/Hosting/flaskexample/static/'+self.tableName
        if not os.path.exists(subdir):
            os.umask(0) # unmask if necessary
            os.makedirs(subdir) 
              
        
        #
        # run the script

        self.dataRun()
        self.weatherBins()
        self.predictor()
        #os.chdir('/Users/loisks/Documents/tmp/database')
        #import pickle
        ## for validation purposes, remove if not validating
        #with open(self.tableName+'.p', 'wb') as file:                
        #        pickle.dump(self.df, file)
        #with open(self.tableName+'_dates.p', 'wb') as file: 
        #        pickle.dump(self.dates, file)
                
        os.chdir('/root/Hosting/flaskexample')
        #print (np.nanmedian(self.df['calories']))
        return(None)
