# Scraping Data From The EUIPO's Trademark Register with Python

The European Union Intellectual Property Office is responsible for registering Trademarks (TMs) in the EU. Its website provides a featured called eSearch Plus, enabling users to locate data about TMs on the EUIPO’s database. A series of methods are provided in this guide, illustrating how data can be scraped automatically from pages on the EUIPO’s site.

Content about TMs on eSearch Plus is loaded using techniques based around Ajax. All of the data about TMs is dynamical HTML generated using Javascript. As the Javascript segments are interpreted by the browser after the page has loaded, technologies used to parse HTML, such as Beautiful Soup, cannot be used here. Such parsing tools will only be able to retrieve the page’s preloaded content, the elements which appear before the Javascript code, which displays the majority of information on the page, is executed. 

## Downloading all of a TM's data

The TM data that Javascript populates the page with is loaded from a JSON file which the EUIPO’s server returns when the user selects the TM through its search feature. It’s possible to retrieve this JSON file by appending the TM’s number to the URL on the IPO site shown in the segment of code below. This code downloads the JSON file from the site using Python’s Requests module. The code utilises the module’s JSON decoder, allowing for the JSON object to be parsed so that particular values within it can be accessed. Within the JSON object is a large dictionary data structure containing virtually all the information about the trademark. This dictionary is passed to a variable in the code below which will be manipulated throughout the rest of this tutorial to illustrate how to access various content about the TM.

```python
#The address on the EUIPO site where a TMs data can be found stored as a JSON object.
url = r'https://euipo.europa.eu/copla//trademark/data/withOppoRelations/'
#Assign the TM's number to the following variable
tmnumber = ''
#Explain
json = requests.get(url+tm).json()
#Explain
tmdict = json['entity']
```

## Handling the TM's date data

All the dates held inside the JSON object are stored as Javascript date objects. These represent dates in Unix time, recording the amount of time which has elapsed in milliseconds since the 1st of January 1970. The code below illustrates how to access all time objects from the dictionary of TM data and then looks at how they can be converted into another format with the use of Python’s time module. First the Unix time variable is retrieved from the dictionary; then its value is passed to the module’s gmtime function which will convert it from Unix to UTC format. The function only accepts data in seconds, hence the original date object by a hundred when given as an argument to gmtime. The UTC value return by gmtime is then converted to dd/mm/yyyy date format by the strftime function. If a different date format is desired, alter the string in the function’s first argument as desired.

```python
#Retrieving the TM's application date from the dictionary.
#Change the first argument of the function to output desired time format.
appdate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['filingdate']/1000))
#Retrieving and converting TM registration date from the dictionary.
regdate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['regdate']/1000))
#Retrieving and converting TM expiry date from the dictionary.
expirydate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['expirydate']/1000))
```

## Accessing all data from a segment on a TM's page

Pages for individual trademarks are divided into segments which list out all data for various aspects of a mark, such as its publications, any priority claims associated with it, and oppositions filed against it. All of the data shown in these segments are normally stored as a number of dictionaries within a list stored within the trademark’s JSON object. The code below shows how all of the data stored in one of these lists can be accessed. In this case all data related to the trademark’s goods and services is retrieved from the list of dictionaries and then placed in a new list. Afterwards, the new list’s content is concatenated together, with each list item being placed on a new line, so all goods data can appear within a single cell of a spreadsheet, should that be the desired output of the web scraper.
```python
#Access the list containing information about the TM's goods and services from the TM's data dictionary.
allgoods = tmdict['gs']['defaultValue']['values']
#Create empty list which the loop below will append goods data to.
goodslist = []
#Iterate over list containing dictionaries of TM goods data. Accessing class numbers and their associated services, 
#concatenating them into single string, appending string to goods list.
for i in allgoods:
  goodslist.append(str(i['number']) + ': '+ i['value'])
#Converting list of goods and services output by above loop to single text string.
goods = "\n".join(goodslist)
```
        
## Accessing a specific data value from a TM page's segment
While the technique above will work to retrieve all the data from a segment, in some cases only a single value may be required. To show how this can be accomplished the following code outlines a means of accessing just the trademark’s first date of publication (its section A.1 publication) from all of the publication data in the JSON object. The technique passes a generator expression to the next function, iterating through the list containing dictionaries until it locates dictionary whose section key is paired with the value ‘A.1’. If a value meeting this criterion is found the next function will return the appropriate dictionary, otherwise it will return a default value of false.
```python
#Retrieve dictionary containing section with name of 'A.1' in list of TM's publications.
#Return result as a list.
firstpublist = [next((item for item in tmdict['publications'] if item['section'] == 'A.1'), 'False')]
#Assign bulleting number from returned dictionary to a variable.
firstpubno = firstpublist[0]['bulletinNumber']
#Conver Javascript time object to dd/mm/yyyy date format.
firstpubdate = time.strftime('%d/%m/%Y', time.gmtime(firstpublist[0]['date']/1000))
````

## Full script for scraping data from EUIPO TM register and storing data in CSV file

```python
import requests
import time
import csv

url = r'https://euipo.europa.eu/copla//trademark/data/withOppoRelations/'

tmnumber = []

outputfile = open('euiposcrape.csv', 'w', newline='')
outputwriter = csv.writer(outputfile)
outputwriter.writerow(['tmnumber','application date','registration date',\
                       'expiry date', 'application type', 'nature', 'status',\
                       'publication date', 'publication number', 'goods', 'owner'])


for tm in tmnumber:
    
    tmnumber = appdate = regdate = expirydate = apptype = \
    nature = status = firstpubdate = firstpubno = goods = owneraddress = ''


    try:
        json = requests.get(url+tm).json()
    except requests.ConnectionError:
        print('Could not scrape data for ' + tm + '. ' + \
              'Connection failed.')
        continue
    
    try:
        message = json['message']
        if message == '404 Not Found':
            print('Could not scrape data for ' + tm + '. ' + \
              'Search on EUIPO returned no results.')
            continue
    except KeyError:
        pass
    
    try:
        tmdict = json['entity']
    except KeyError:
        pass
    
    print('Scraping data for ', tm)
    #Scraping trademark number.
    try:
        tmnumber = tmdict['number']
    except KeyError:
        pass
    #Scraping application date.
    try:
        appdate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['filingdate']/1000))
    except (KeyError, ValueError):
        pass
    #Scraping registration date.
    try:
        regdate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['regdate']/1000))
    except (KeyError, ValueError):
        pass
    #Scraping trademark expiry date.
    try:
        expirydate = time.strftime('%d/%m/%Y', time.gmtime(tmdict['expirydate']/1000))
    except (KeyError, ValueError):
        pass
    #Scraping application type data.
    try:
        apptype = tmdict['feature']
    except KeyError:
        pass
    #Scraping nature of application info.
    try:
        nature = tmdict['kind']
    except KeyError:
        pass
    #Scraping status data.
    try:
        status = tmdict['status']
    except KeyError:
        pass
    
    
    #Retrieving details of first publication
    try:
        firstpublist = [next((item for item in tmdict['publications'] if item['section'] == 'A.1'), 'False')]
        if firstpublist != 'False':
            
            firstpubno = firstpublist[0]['bulletinNumber']
        
            firstpubdate = time.strftime('%d/%m/%Y', time.gmtime(firstpublist[0]['date']/1000))
    
    except (TypeError, ValueError, KeyError):
        pass
    #Retrieving goods and services data.
    try:
        allgoods = tmdict['gs']['defaultValue']['values']
    except KeyError:
        pass
    
    goodslist = []
    
    #Scraping goods data.
    try:
        for i in allgoods:
            goodslist.append(str(i['number']) + ': '+ i['value'])
        
        goods = "\n".join(goodslist)
        
        #Retrieving owner address data.
        owneraddress = tmdict['applicants'][0]['address']['postalAddress']
    except (TypeError, ValueError, KeyError):
        pass

    outputwriter.writerow([tmnumber, appdate, regdate, expirydate, apptype,\
                           nature, status, firstpubdate, firstpubno, goods,\
                           owneraddress])

outputfile.close() 
```
        
