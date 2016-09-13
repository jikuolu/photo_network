
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 13:59:21 2016

@author: Jikuo Lu
"""

#import urllib
import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup as bs
from urlparse import urljoin
from collections import defaultdict
#from ediblepickle import checkpoint

#getting links to all photo pages
urls = []
def photolinks(n):
    for page in range(n):
        url = "http://www.newyorksocialdiary.com/party-pictures?page=" + str(page)
        response = requests.get(url, params={"limit": 1000, "offset": 0})
        response.text[:1000] + "..."
        soup = bs(response.text)
        for link in soup.find_all('a'):
            urls.append(link.get('href'))
photolinks(30)


#This part gets the real links
urlbase = "http://www.newyorksocialdiary.com/"
regex_v = re.compile(r"\/party-pictures\/20", re.VERBOSE)
photourl = []
for element in urls:
    m = regex_v.match(str(element))
    if m:
        year = re.match(r"\/party-pictures\/(\d+)", str(element))
        if int(year.group(1)) < 2015: 
            photourl.append(urljoin(urlbase, element))
    else:
        continue


#this part get the text for photos
captions = list()
dic = defaultdict()
f = open("rawtext.txt", "w")
def writenames(soup):
    names = soup.find_all('div', attrs = {'align':'center','class':'photocaption'})
    names.extend(soup.find_all('div',attrs={'id':'photocaption'}))
    names.extend(soup.find_all('td',attrs={'class':'photocaption'}))#,'valign':'top'
    names.extend(soup.find_all('span',attrs={'class':'photocaption'}))
#    names.extend(soup.find_all('font',attrs={'size':'1'}))
    for el in names:
        line = re.search(r'>((.|\n)*)<',str(el))
        line = line.group(1).rstrip()
        captions.append(line)
        with open("rawtext.txt", "a") as file:
            file.write(line+'\n')
#This part filters data to date as specified
for url in photourl:
    response = requests.get(url, params={"limit": 1000, "offset": 0})
    response.text[:1000] + "..."
    soup = bs(response.text)
    dates = soup.find_all('div', attrs = {'class':'panel-pane pane-node-created'})
    for date in dates:
        properdate = datetime.strptime(date.text.strip(),'%A, %B %d, %Y')
        if properdate < datetime.strptime('2014-12-01', '%Y-%m-%d'):        
            writenames(soup)
#pickle the data
#f = open('captions.p', 'w')   # Pickle file is newly created where foo1.py is
#pickle.dump(captions, f)          # dump data to f
f.close()  
          
#use regular expression to get names from captions

import re
names = open('simpleraw.txt','r')
def text_to_names(names,n=[]):
    namelist=''    
    for line in names:
        line=line.strip()
#        print line
        n = n + re.findall(r',\s([A-Z]\w+)\s+and\s[A-Z]\w+\s([A-Z]\w+)',line)
        n = n + re.findall(r'^([A-Z]\w+)\s+and\s[A-Z]\w+\s([A-Z]\w+)',line)
        n = n + re.findall(r'([A-Z]\w+)\s+([A-Z]\w+)[\n,]',line)
        n = n + re.findall(r'([A-Z]\w+)\s+[A-Z]\.\s([A-Z]\w+)',line)
        n = n + re.findall(r'([A-Z]\w+)\s+\w+\s([A-Z]\w+)',line)  
        for (fname, lname) in n:
            namelist += ('%s %s,'%(fname, lname))
    return n
namelist = text_to_names(names)
print namelist
#this part extract a dictionary of dictionary from name captions
def list_to_dict(namelist, person={}):
#    names = namelist.split(',')
    for name in names:
    #    person[name] =
        if name not in person:
            person[name] = {}
        for other in names:
            if other not in person[name]:            
                person[name][other] = 1
            person[name][other] += 1
    print person
    return person
        
namedict = list_to_dict(namelist)

#this part printout the final results
def popularity(namedict = {}):
    connections =  {}
    for key in namedict:
        connections[key] = len(namedict[key]) - 1
    for name in sorted(connections, key=connections.get, reverse=True)[:100]:
        print name, connections[name]
def bestfriend(namedict = {}):
    bestfriend = {}
    for nameA in namedict:    
        for nameB in namedict[nameA]:
            if nameA != nameB:
                bestfriend[nameA,nameB] = namedict[nameA][nameB]
    for friends in sorted(bestfriend, key=bestfriend.get, reverse=True)[:100]:
        print friends, bestfriend[friends]

popularity(namedict)
bestfriend(namedict)
