# webScrapeFunctions.py
#
# use Selenium to get the useful bits from the Polar Flow website
#
# LKS, June 2016, Part of the Inisght Data Science Program
#
import numpy as np
from selenium import webdriver
import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import datetime

# after first login this flips to True and you don't need to keep logging in 
#loginGlobal=False
ffprofile = webdriver.FirefoxProfile()
adblockfile='/Users/loisks/Desktop/Old Firefox Data/4fo05kgu.default/extensions/adblockultimate@adblockultimate.net.xpi'
ffprofile.add_extension(adblockfile)

ffprofile.set_preference("extensions.adblockplus.currentVersion", "4")
wd = webdriver.Firefox(ffprofile)

 #for debugging
#wd= webdriver.PhantomJS(executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs') # for silent displays

def loginOnce():      
      loginURL='https://flow.polar.com/login'
     # wd = webdriver.Firefox(ffprofile)
      wd.get(loginURL)
      time.sleep(2) # empricallly 2 seconds worked well, this can be adjusted
      username = wd.find_element_by_id("email")
      password = wd.find_element_by_id("password")

      #
      # put in your own login information!
      username.send_keys("loisks@umich.edu")
      password.send_keys("poppy33!")
      
      wd.find_element_by_id("login").click()
      time.sleep(2)
      loginGlobal=True # flips to true
      print( "Successful Login" )
      return None

def getTrackerData(inURL):
      # inURL = url with appropriate date attached
      # returns: a dictionary with Steps, ActiveTime, Distance, Calories, SleepTotal, GoodSleep
      parameters=['Steps', 'ActiveTime', 'Distance', 'Calories', 'SleepTotal', 'GoodSleep']
      dataDicts={}
      #
      # login if you haven't already
      loginOnce()

      # get the appropriate page of data    
      wd.get(inURL)
      time.sleep(2)
      #
      # we are interested in steps, total active time, distance, calories,
      # amount of sleep, and amount of good sleep (percentage)
      
      StepsElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[2]/span[1]'
      ActiveTimeElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[1]/span[1]'
      #ActivityPercentageElement='//*[@id="slider-activity-goal"]/div/div[2]/div[1]/div[2]/div/div/div[2]'
      DistanceElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[3]/span[1]'
      CaloriesElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[4]/span[1]'
      AmountSleepElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[6]/span[1]'
      AmountGoodSleepElement='//*[@id="activity-summary"]/div[1]/div[1]/div/div[7]/span[1]'
      ElementArray=[StepsElement,ActiveTimeElement,DistanceElement,CaloriesElement,AmountSleepElement, AmountGoodSleepElement]

      for iElem in range(len(parameters)):
          try:
              dataDicts[iElem]= wd.find_elements_by_xpath(ElementArray[iElem])[0].text
          except:
              if iElem==4 or iElem==1:
                  dataDicts[iElem]='0 hours 0 minutes' # a nan of sorts
              else:
                    dataDicts[iElem]=0

      # return the dictionary, which is a dictionary to account for the strings
     # wd.close()
      return dataDicts 


def getWeatherData(date, location):
    #  date = date for consideration, in python datetime
    #  location = string for location
    #
    # use weather underground for historical data
    wlink='https://www.wunderground.com/history/'
    #
    # go there
    #adblockfile='/Users/loisks/Desktop/Old Firefox Data/4fo05kgu.default/extensions/adblockultimate@adblockultimate.net.xpi'
    #ffprofile.add_extension(adblockfile)
    #ffprofile.set_preference("extensions.adblockplus.currentVersion", "4")
    #wd = webdriver.Firefox(ffprofile)
    wd.get(wlink)
    
          
    #
    # put in the location
    #
    # select the appropriate date
    selectMonth = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[1]'))
    selectMonth.select_by_visible_text(datetime.datetime.strftime(date, '%B'))
    selectDay = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[2]'))
    selectDay.select_by_visible_text(str(date.day))
    selectYear = Select(wd.find_element_by_xpath('//*[@id="trip"]/div[3]/select[3]'))
    selectYear.select_by_visible_text(str(date.year))
    #
    #
    site = wd.find_element_by_id("histSearch")
    site.send_keys(location)

    # FIX THIS I DONT LIKE IT! 
    try:
        pleaseClick=wd.find_element_by_id("autocomplete_item_template")
        pleaseClick.click()
    except:
      try:
         pleaseClick=wd.find_element_by_id("wuSearch")
         pleaseClick.click()       
      except:
        pleaseClick=wd.find_element_by_id("history-station-search-row")
        pleaseClick.click()
        pleaseClick.click()
    
       
    wd.find_element_by_xpath('//*[@id="trip"]/input[5]').click()
    time.sleep(3)
    
    #
    # now collect the appropriate data
    # note mean Temperature is in F
    #
    # get the right tags

    tagNames=wd.find_elements_by_css_selector("#historyTable")
    print tagNames
    stag=''.join([x.encode('UTF8') for x in tagNames[0].text])
    broken=stag.split('\n')
    import re
    
    for istr in range(len(broken)):
          if broken[istr][0:16]=='Mean Temperature':
                      meanTemperature=float(broken[istr][16:20])
          elif broken[istr][0:15]=='Min Temperature':
                minTemperature=float(broken[istr][15:18])
          elif broken[istr][0:15]=='Max Temperature':
                maxTemperature=float(broken[istr][15:18])
          elif broken[istr][0:13]=='Precipitation':
                try: 
                      findStart=re.search("\d", broken[istr+1])
                      FS=findStart.start()
                      precipitation=float(broken[istr+1][FS:FS+4])
                except:
                      try:
                            precipitation=float(broken[istr+1][14:17])
                      except:
                            precipitation=0
          elif broken[istr][0:10]=='Wind Speed':
                wind = float(broken[istr][10:13])
    # awesome now return the data
   # wd.close()
    time.sleep(1)
    return([meanTemperature, maxTemperature, minTemperature, precipitation, wind])


#wd.close()
