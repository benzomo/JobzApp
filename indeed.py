# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 15:40:56 2018

@author: benmo
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import html5lib
import shutil
import os, sys, socket
import time
import numpy as np, pandas as pd
import stopit
import re


cName = socket.gethostname()

if cName == 'DESKTOP-HOKP1GT':
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/it0uu1ch.default"
    uofcPath = "D:/benmo/OneDrive - University of Calgary"
else:
    ffProfilePath = "C:/Users/benmo/AppData/Roaming/Mozilla/Firefox/Profiles/vpv78y9i.default"
    uofcPath = "D:/OneDrive - University of Calgary"


old = pd.read_pickle("D:/Data/PyObjects/jobs.pkl")

def get_jobs(old):

    fp = webdriver.FirefoxProfile(ffProfilePath)
    browser = webdriver.Firefox(firefox_profile=fp)
    url = "https://www.indeed.ca/"
    
    todayDate = time.strptime(time.strftime("%d/%m/%Y"),'%d/%m/%Y')
    todayDateNum = time.mktime(todayDate)
    
    titles = ['financial analyst', 'data analyst', 'python c#', 'economics analyst']
    provinces = ['Alberta', 'British Columbia']
    
    jobs_df = pd.DataFrame(old, columns=['Title','Province','Location','Company',
                                         'Description','URL','Date'])


    for province in provinces:
        for title in titles:
    
            browser.get(url)
            
            what = browser.find_element_by_id('text-input-what')
            what.click()
            for i in range(20):
                what.send_keys(Keys.BACKSPACE)
            what.send_keys(title)
            
            where = browser.find_element_by_id('text-input-where')
            where.click()
            for i in range(20):
                where.send_keys(Keys.BACKSPACE)
            where.send_keys(province)
            browser.find_element_by_xpath("//*[@type='submit']").click()
            
            
            browser.find_element_by_xpath("//a[contains(text(), 'date')]").click()
            
            
            stop = False
            page = 1
            
            while stop == False:
            
                stop = len(list(filter(lambda x: ('days ago' in x.text) & (x.text in ['12 days ago',
                                       '13 days ago', '14 days ago', '15 days ago']), 
                            browser.find_elements_by_xpath("//*[contains(text(), 'days ago')]")))) > 0
            
            
                jobs_temp = browser.find_elements_by_xpath("//*[@class='row result clickcard']")
                soups = list(map(lambda x: BeautifulSoup(x.get_attribute('innerHTML'),
                                                                 'html5lib'), jobs_temp))
            
                for i, job in enumerate(jobs_temp):
                    
                    tempdesc = jobs_temp[i].text
                    temploc = soups[i].find(class_="location").getText()
                    tempcompany = soups[i].find(class_="company").getText().replace('\n','').lstrip()
                    
                    
                    jobs_temp[i].find_elements(By.CSS_SELECTOR , 'a')[0].click()
                    
                    WebDriverWait(browser, 10).until(
                                lambda x: x.find_element_by_xpath("//*[@class='job-footer-button-row']"))
                    
                    try:    
                        tempurl = browser.find_element_by_class_name(
                                'job-footer-button-row').find_element_by_tag_name(
                                'span').get_attribute('data-indeed-apply-joburl')
                    except:
                        tempurl = browser.find_element_by_class_name(
                                'job-footer-button-row').find_element_by_tag_name(
                                        'a').get_attribute('href')
                    
                    
                    datetxt = browser.find_element_by_id("auxCol").find_element_by_class_name('date').text
                    
                    try:
                        tempdate = time.strftime("%d/%m/%Y") if 'hour' in datetxt else time.strftime("%d/%m/%Y", time.gmtime(todayDateNum - 60*60*24*int(re.findall(r'\b\d+\b', 
                                           datetxt)[0])))
                    except:
                        tempdate = 'N/A'
                    
                    
                    if tempdesc in jobs_df.Description.tolist():
                        pass
                    else:
                        jobs_df = jobs_df.append(pd.DataFrame(
                                np.array([title, province, temploc, tempcompany, tempdesc, tempurl, tempdate]).reshape(1,-1), 
                                columns=['Title','Province','Location','Company','Description','URL','Date']),
                                ignore_index=True)
                    
                
                page+=1
                try:
                    browser.find_element_by_xpath("//*[@class='pn'][contains(text(), '{p}')]".format(
                            p=page)).click()
                except:
                    stop = True
                
                #ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                
                try:
                    WebDriverWait(browser, 2).until(
                                lambda x: x.find_element_by_id('popover-close-link')) 
                    temp = browser.find_element_by_id('popover-close-link')
                    ActionChains(browser).move_to_element(temp).click().perform()
            
                except:
                    pass
    return jobs_df.values

