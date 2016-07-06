# ActiveMe
This is my Insight Data Science Project 
hosted at loisks.xyz
The naming conventions are awful, sorry! 

you will want to use ./run.py under the hosting folder
The webpage info (input/output) is under the templates folder in flaskexample
The plots are sent to static in flaskexample

In flaskexample, scripts that control each tracker:
dataStats.py -> PolarLoop
readJawBone.py -> Jawbone
readTapiriik.py -> Endomondo
webScrapeFunctions.py -> weatherunderground API
views2.py -> controlling script 
plottingFunctions.py -> makes the plots and runs the predictive model

Currently, the app works for Endomondo and Jawbone data. The Polar Loop stuff works on mac OSX but was having compatability issues with linux based FireFox (Ugh!). 
