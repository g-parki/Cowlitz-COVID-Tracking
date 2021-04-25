from bs4 import BeautifulSoup as bs
import datetime
import requests
import csv
from COVIDModule import Release

#Open page with links to all historical data
'''
source = requests.get('https://www.co.cowlitz.wa.us/2757/COVID-19-Daily-Data-History').text
soup = bs(source, 'lxml')

items = soup.find_all('li')
items = [item for item in items if "Daily Data Summary for" in item.text]
releases = []
for item in items:
    if len(item.a.text) > 0:
        link = "https://www.co.cowlitz.wa.us/" + item.a['href']
        date = item.a.text.lstrip()
        releases.append(Release(date, link, ""))

releases = [release for release in releases if release.datedate > datetime.datetime(2020,12,31,0,0).date()]
releases.sort(key= lambda x: x.datedate)

for thing in releases:
    print(thing.link)
    print(thing.datestr)
    print(thing.datedate)
    print("")
'''

import tabula
for i in range(1,2):
    #df = tabula.read_pdf(releases[i].link, pages='all')
    df = tabula.read_pdf('https://www.co.cowlitz.wa.us/DocumentCenter/View/22207/17-February-Daily-Data-Summary', pages='all')
    print(df)
    print(df.iloc[3,1])
    print("")
