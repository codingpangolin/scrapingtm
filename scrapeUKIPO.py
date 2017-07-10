# -*- coding: utf-8 -*-

import bs4
import requests
import csv
from datetime import datetime

tmurl = r'https://trademarks.ipo.gov.uk/ipo-tmcase/page/Results/1/'

outputfile = open('tmdata.csv', 'w', newline='')
outputwriter = csv.writer(outputfile)
outputwriter.writerow(['TM Name', 'Filed', 'Registered', 'Renewal', 'Status',\
                       'Details', 'Owner Name', 'Owner Address', 'Rep Name', \
                       'Rep Address', 'Journal', 'Pub Date', 'Goods'])

tmnumber = []

for tm in tmnumber:

    details = filed = goods = journal = owneraddy = ownername = pubdate = \
    registered = renewal = status = tmname = repname = repaddy = ''

    addylist = pubdetails = classdescs = ''
    
    try:
        res = requests.get(tmurl + tm)
    except requests.ConnectionError:
        print('Could not scrape data for ' + tm + '. ' + \
              'Connection failed.')
        continue
    
    souptm = bs4.BeautifulSoup(res.text, "lxml")
    
    print('Scraping data for ', tm)
    
    namesearch = souptm.find_all('h1')
    
    if len(namesearch) >= 1:
    
        tmname = namesearch[0].get_text()
    
    if tmname == 'Search for a trade mark':
        print('No data found for ', tm)
        tmname = tm
        filed = 'No data found.'
    
    tminfo = souptm.find_all(class_="column-one-third")
    
    if len(tminfo) >=1:
        
        try:
            filed = tminfo[0].find_all('dd')[0].get_text()
            filed = datetime.strptime(filed, '%d %B %Y').strftime('%d/%m/%Y')
        except (IndexError, ValueError):
            pass
        
        try:
            registered = tminfo[1].find_all('dd')[0].get_text()
            registered = datetime.strptime(registered, '%d %B %Y').strftime('%d/%m/%Y')
        except (IndexError, ValueError):
            registered = ''
            pass
        
        try:
            renewal = tminfo[2].find_all('dd')[0].get_text()
            renewal = datetime.strptime(renewal, '%d %B %Y').strftime('%d/%m/%Y')
        except (IndexError, ValueError):
            renewal = ''
            pass
    
    statussearch = souptm.find_all(class_="offset")
    
    if len(statussearch) >= 1:
        status = statussearch[0].find_all('dd')[0].get_text()
    
    alladdys = souptm.find("div", {"id": "tab-3"})
    
    try:
        addylist = alladdys.find_all('dl')
    except AttributeError:
        pass
    
    if len(addylist) >=1:
    
        try:
            ownername = addylist[0].find('dt').get_text()
            
            owneraddy = addylist[0].find('dd').get_text()
            
            repname = addylist[1].find('dt').get_text()
            
            repaddy = addylist[1].find('dd').get_text()
        except (AttributeError, IndexError):
            pass
    
    allpub = souptm.find("div", {"id": "tab-4"})
    
    try:
        pubdetails = allpub.find_all('dd')
    except AttributeError:
        pass
    
    if len(pubdetails) >= 1:
    
        try:
            journal = pubdetails[0].get_text().strip()
        except (AttributeError, IndexError):
            pass
        
        try:
            pubdate = pubdetails[1].get_text()
            pubdate = datetime.strptime(pubdate, '%d %B %Y').strftime('%d/%m/%Y')
        except (AttributeError, IndexError, ValueError):
            pass
    
    classsearch = souptm.find("div", {"id": "tab-2"})
    
    try:
        classnos = classsearch.find_all(class_='subsection__title')
    except (AttributeError):
        pass
    
    try:
        classdescs = classsearch.find_all(class_='no-print')
    except (AttributeError):
        pass
    
    if len(classdescs) >=1 and len(classnos) >=1:
        good_list = []
        
        for a, b in zip(classnos, classdescs):
            goods = a.get_text() + ': ' + b.get_text()
            good_list.append(goods)
            
        goods = "\n".join(good_list)
    
    slides = souptm.find_all(class_='slide')
    
    if len(slides) >= 1:
    
        tmdetails = []
        
        for i in slides:
            try:
                if len(i.find_all('a', {'id' : 'lightbox-2-1'})) == 1:
                    link = i.find_all('a', href=True)
                    tmdetails.append(link[0]['href'])
                elif len(i.find_all('dd')) >=1:
                    word = i.find_all('dd')[0].get_text()
                    tmdetails.append(word)
            except (AttributeError, IndexError):
                pass
                
        details = "\n".join(tmdetails)
    
    outputwriter.writerow([tmname, filed, registered, renewal, status, details, \
                           ownername, owneraddy, repname, repaddy, journal, \
                           pubdate, goods])

outputfile.close()    