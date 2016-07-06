from flask import render_template
from flaskexample import app
from flask import request
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import numpy as np

import os
import datetime

#from flask import Flask
#app = Flask(__name__, static_url_path = "/root/Hosting/flaskexample/static", static_folder = "/root/Hosting/flaskexample/static")
UPLOAD_FOLDER_RAW = '/root/tmp/raw/'
UPLOAD_FOLDER_EDIT = '/root/tmp/edit/'
ALLOWED_EXTENSIONS = set(['csv','CSV', 'tcx', 'TCX'])

app.config['UPLOAD_RAW_DEST'] = UPLOAD_FOLDER_RAW
app.config['UPLOAD_EDIT_DEST'] = UPLOAD_FOLDER_EDIT
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_RAW

# check file is ok
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
# try looking at app.show 
@app.route('/')
#@app.route('/index')
def index():
   import os
   os.chdir('/root/Hosting/flaskexample') 
   return render_template("cesareans.html",
       title = 'Home', img1="/static/active_Lois.png", img2="static/active_Me_Logo.png",
       )
#
# the forum
#@app.route('/')
#def my_form():
#    return render_template("my-form.html")


@app.route('/output',methods=['POST', 'GET'])
def output():
 #
 # man, this sucks
 #
    
 
 tracker=request.form.get('Tracker')
 username=request.form.get('Username')
 password=request.form.get('Password')
 location=request.form.get('Location')
# dateStart=request.form.get('StartDate')
# print("Date start is: " + str(dateStart))
# dateEnd=request.form.get('EndDate')
 dataModified=[] # for Jawbone file check           
 try:
    #
    # THIS GETS THE FILE. FLASK.
    #
   files = request.files.getlist('file[]')
   print files
   filenames=[]
   for ifile in files:   
     if ifile and allowed_file(ifile.filename):
       filenames.append(ifile.filename)
       ifile.save(os.path.join(app.config['UPLOAD_RAW_DEST'],ifile.filename))
       print ifile.filename

   #get location of saved file
   #print( 'filename: ' + filename)
   filepath = os.path.join(app.config['UPLOAD_RAW_DEST'],filenames[0])
   print filepath
   print app.config['UPLOAD_RAW_DEST']

   if tracker=='Jawbone':
      import glob
      # then this is a csv file
      os.chdir('/root/tmp/raw')
      # get the file
      for ifile in range(len(filenames)):
       print("FILE NAME IS: " +str(filenames[ifile]))
       ff=glob.glob(filenames[ifile])[0]
       dataAll=np.swapaxes(np.genfromtxt(ff, delimiter=','), 1, 0)
      
       temp=[ datetime.datetime.strptime(str(int(dataAll[0][j])), \
              '%Y%m%d') for j in range(1,len(dataAll[0]))]
       dataYears=list( dataAll[0])
       time=[np.nan]+ temp
       # now get the data that matters 
       # 
       # 41 is steps
       # 37 is distance in meters
       # 43 is calories
       # 35 is active time in seconds
       # 48 is sleep time
       #
       params=['Dates', 'Steps', 'Distance', 'Calories', 'ActiveTime', 'SleepTime']
       indicies=[0,41, 37, 43, 35, 48]
       dataModified={}
       # now have to adjust for the right dates
       for iP in range(len(params)):
           dataModified[params[iP]]=[]
       goodvals= np.isnan(dataYears[41]) # get rid of the nans
      
       dataModified['Steps']+=list(dataAll[41])
       dataModified['Distance']+=list(dataAll[37])
       dataModified['Calories']+=list(dataAll[43])
       dataModified['ActiveTime']+=list(dataAll[35])
       dataModified['SleepTime']+=list(dataAll[48])
       dataModified['Dates']+=list(np.array(time))
       #
   if tracker=='Endomondo':
       import glob
       from geopy.geocoders import Nominatim	
       import tcxparser
       # then this is a tcx file
       os.chdir('/root/tmp/raw')
       # get the file
       params=['Date', 'ActiveTime', 'Distance', 'Calories', 'Location']
       dataModified={}
       for iparam in params:
	   dataModified[iparam]=[]
       for ifile in range(len(filenames)):
      		 print("FILE NAME IS: " +str(filenames[ifile]))
       		 ff=glob.glob(filenames[ifile])[0]
       		 startDate=ff[0:10]
       		 tcx=tcxparser.TCXParser(ff)
                 # get data
                 workoutTime=tcx.duration
                 latitude=str(tcx.latitude)
                 longitude=str(tcx.longitude)
                 timeStamp=tcx.completed_at
                 try:
                          distance=tcx.distance
                 except:
                          distance=1e-31
                 calories=tcx.calories
                 # turn lat and longitude into a city
                 geolocator = Nominatim()
                 location = (geolocator.reverse(latitude+','+longitude)).address
                 # now have to adjust for the right dates
		 print startDate
                 dataModified['Date'].append(startDate )
                 dataModified['Distance'].append(distance)
                 dataModified['Calories'].append(calories)
                 dataModified['ActiveTime'].append(workoutTime)
                 dataModified['Location'].append(location)

    
 except:
     print("no file uploaded")

#
# now load the relevant figures
#
 dateStart=0; dateEnd=0
 if tracker=='Jawbone':
         import readJawBone as PL 
         data=PL.loadData(username, password, location,\
                           data=dataModified)
         
# elif tracker=='Polar Loop':         
#         import dataStats as PL
#         data=PL.loadData(username, password, location, instartDate=dateStart, \
#                          inendDate=dateEnd)
#
# Jimmy's data 
 elif tracker=='Endomondo':         
         import readTapiriik as PL
         data=PL.loadData(username, password, location, dataModified=dataModified)

 dd=data[0]
 temp=data[0]*1.1
 goal=("%.0f" % temp )
 cals=("%.0f" % dd)
 dayofweek=data[2]
 weather=data[1]

 boxwhisker="/static/"+username+"/boxwhisker_Calories_daysofweek.png"
 scatter1="/static/"+username+"/seaborn_Calories_Wind_scatter.png"
 scatter2="/static/"+username+"/seaborn_Calories_MeanTemperature_scatter.png"
 scatter3="/static/"+username+"/seaborn_Calories_Precip_scatter.png"
 os.chdir('/root/Hosting/flaskexample')
 import stat
 os.chmod('/root/Hosting/flaskexample'+boxwhisker, 0o777)
 os.chmod('/root/Hosting/flaskexample'+scatter1,0o777)
 os.chmod('/root/Hosting/flaskexample'+scatter2,0o777)
 os.chmod('/root/Hosting/flaskexample'+scatter3, 0o777)
 print(scatter1)
 
 return render_template("output.html", calories=cals, tracker=tracker, \
                        goal=goal, dayofweek=str(dayofweek),\
                        weather=str(weather), boxwhisker=boxwhisker, \
                        scatter1=scatter1, scatter2=scatter2, \
                        scatter3=scatter3)
