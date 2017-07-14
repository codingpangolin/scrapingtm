# Scraping Data from the UK's online Trademark register to a CSV file

The United Kingdom’s Intellectual Property Office (IPO) holds the responsibility of examining and issuing trademarks in the U.K. So that trademark owners and applicants can view data about existing trademarks or the status of an application, the IPO hosts a website which displays all this information. Currently in order to find data a visitor to the website must enter the trademark’s number and then manually record whatever details they were looking for from the content they’re presented with. The Python script presented here aims to make this process simpler: it automatically scrapes data from the pages of one or more trademark and then places all retrieved data in a CSV file. This should make it easier to quickly collect trademark data particularly if its user needs to gather the details of a large number of applications.

## Usage Notes

Before attempting to use the script please make a note of the following points:

* The administrators of the IPO site limit the total number of page requests that can be made against their web server in order to prevent bots from causing an unnecessary load on the server’s resources and thus reducing the site’s overall performance. To this end, IP addresses are blocked downloading data from the IPO (at least without passing a Captcha test) once they have made 167 page requests. How they came to this number, I don’t know, but if you want to download data in bulk you’ll have to limit the total trademarks scraped at a single time to this number and then either wait 24 hours, or find some way to mask your IP address, before attempting to use the script again.
* There’s no way to guarantee that the administrators of the IPO site won’t alter the structure of its HTML at some point in the future. The script presented here can successfully parse the HTML of the IPO site as of June 2017. If the script here fails to work then it may be due to it needing to be altered to retrieve data from a newly formatted version of the IPO site’s HTML.
* Though the script has been tested on a large volume of trademark cases I am not an expert in intellectual property law and cannot guarantee that there will not be potential cases I have not encountered which the script will be unable to retrieve some data from. However, I am confident that the code, as presented, should be able to retrieve data from the majority of trademark cases. Hopefully, even if the script does not meet your needs you should be able to modify it quite easily to retrieve the required data.
* Running the script requires Python 3 and its csv, datetime, requests modules, and the latest version of Beautiful Soup. Most of these are part of Python’s built in library, though Beautiful Soup will have to be installed before the script is able to parse the HTML data downloaded via the requests module.

## CSV Structure

Running the script should produce a CSV file containing all the data scraped from the IPO’s website. All the most popular spreadsheet software, including Microsoft Excel, should be able to open this file. The headers of the CSV file are listed below, alongside a description of the data that will be stored in the related rows:

* TM Name: the trademark’s unique identification number.
* Filed: holds the date which the intellectual property office (IPO) records the trademark application as having been filed.
* Registered: date on which the IPO recognised the trademark as gaining its legally protected status.
* Renewal: date in the future on which payment must be made for the trademark’s protected status to be continued.
* Status: records the stage which the trademark currently holds in its life cycle.
* Details: holds information describing the mark. All protected words and the URLs of images are stored in this cell, each placed on a new line in the row.
* Owner name: the name of the trademark’s applicant.
* Owner address: the applicant’s corresponding address.
* Rep name: name of the firm responsible for maintaining the trademark on behalf of the owner.
* Rep address: the representative’s corresponding address.
* Journal: Issue number of the gazette in which the trademark application was first published.
* Pub Date: Date on which journal containing first publication of application was issued.
* Goods: stores all the classes the trademark covers and the corresponding list of goods/services this includes. All goods are listed in this cell, each one occupying its own new line.

## Instructions: Supplying Target Trademarks

The TM pages to be targeted by the web scraper should be placed in quotation marks inside the empty list with the name tmnumber which appears towards the start of the code. To scrape data from multiple pages with the script enter them into the list separated by a comma. Examples of acceptable program input include:

```python
#Enter data either as a single TM in the list
tmnumber = ['UK00002442039']
#Or as multiple items in the list
tmnumber = ['UK00002442039', 'UK00002442040', 'UK00002442041']
```
If you have TM numbers saved in an external data source, such as a spreadsheet, then a variable containing the numbers could be supplied to the script in the place of the empty list.

For the script to work the TM number supplied in the list must be in the exact same format as that used by the IPO’s website. It must begin with the two letter code identifying whether it is a UK or EU trademark, followed by a series of up to five zeroes, and then the number which uniquely identifies the TM. 

## Controlling Output
By default the script will produce a CSV file named tmdata. To configure the name of the CSV file alter the name assigned to the output file it is created. As a demonstration, to change the name of the CSV file to ourtrademarks, the code that currently reads as:
```python
outputfile = open('tmdata.csv', 'w', newline='')
```
Should be changed to this:
```python
outputfile = open('ourtrademarks.csv', 'w', newline='')
```

Note here that if a file exists in the scripts current directory with the same name as the output file it will be deleted and replace with the CSV file the script generates.

## The web scraper's full code

```python
import bs4
import requests
import csv
from datetime import datetime

tmurl = r'https://trademarks.ipo.gov.uk/ipo-tmcase/page/Results/1/'
#Generate CSV file for program output and write the headers for the scraped
#data values.
outputfile = open('tmdata.csv', 'w', newline='')
outputwriter = csv.writer(outputfile)
outputwriter.writerow(['TM Name', 'Filed', 'Registered', 'Renewal', 'Status',\
                       'Details', 'Owner Name', 'Owner Address', 'Rep Name', \
                       'Rep Address', 'Journal', 'Pub Date', 'Goods'])
#Enter Trademarks to be targeted by the scraper into the empty list.
tmnumber = []

for tm in tmnumber:

    details = filed = goods = journal = owneraddy = ownername = pubdate = \
    registered = renewal = status = tmname = repname = repaddy = ''

    addylist = pubdetails = classdescs = ''
    #Download trademark page from the register.
    try:
        res = requests.get(tmurl + tm)
    except requests.ConnectionError:
        print('Could not scrape data for ' + tm + '. ' + \
              'Connection failed.')
        continue
    #Convert trademark page to beautiful soup object for parsing.
    souptm = bs4.BeautifulSoup(res.text, "lxml")
    
    print('Scraping data for ', tm)
    #Retrieve TM number from downloaded page.
    namesearch = souptm.find_all('h1')
    
    if len(namesearch) >= 1:
    
        tmname = namesearch[0].get_text()
    
    if tmname == 'Search for a trade mark':
        print('No data found for ', tm)
        tmname = tm
        filed = 'No data found.'
    
    #Retrieve application, registration, and renewal dates from downloaded page.
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
    
    #Retrieve trademark's current status from page.
    statussearch = souptm.find_all(class_="offset")
    
    if len(statussearch) >= 1:
        status = statussearch[0].find_all('dd')[0].get_text()
    
    #Retrieve owner name and addresses, and representative name and addresses.
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
    
    #Retrieve Trademark's classes and descriptions of its goods and services.
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
    
    #Retrieve details of mark (pictures of logo or transcriptions of text.)
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
    #Write scraped data to new row in CSV file.
    outputwriter.writerow([tmname, filed, registered, renewal, status, details, \
                           ownername, owneraddy, repname, repaddy, journal, \
                           pubdate, goods])

outputfile.close()
```


