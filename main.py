from bs4 import BeautifulSoup as bs
from datetime import date, datetime
import requests
import csv
import pandas as pd
import COVIDModule

#load daily data page
try:
    source = requests.get('https://www.co.cowlitz.wa.us/2749/COVID-19-Daily-Data-Summary').text
    soup = bs(source, 'lxml')
except:
    COVIDModule.SendMessage("Website not available")
    raise Exception("Website not available")

try:
    #find current date in data page. currently found in the third column of the first table
    websiteDate = soup.find_all('td')[2].text
    #Convert to format 12/17/2020
    #Starts in format "Tuesday, December 17, 2020"
    websiteDateStr = datetime.strptime(websiteDate, "%A, %B %d, %Y").date().strftime("%m/%d/%Y")
except:
    COVIDModule.SendMessage("Issue parsing today's date")
    raise Exception("Issue parsing today's date")

#load local CSV
df = pd.read_csv('covidData.csv')

#Append current data if it's not in the CSV dataset    
if not websiteDateStr in df['Date'].values:

    with open('covidData.csv', 'a') as csv_file:
        csv_writer = csv.writer(csv_file)

        try:
            #Get the count for today - two columns after a column saying "Active Cases"
            todayCount = soup.find('td', text= 'Active Cases').findNext('td').findNext('td').text
        except:
            COVIDModule.SendMessage("Issue parsing active cases")
            raise Exception("Issue parsing active cases")

        #Open the web page containing the links to historical data
        source = requests.get('https://www.co.cowlitz.wa.us/2757/COVID-19-Daily-Data-History').text
        soup = bs(source, 'lxml')

        #Find line with today's date in the text and obtain the link
        line = soup.find('a', text = websiteDateStr)
        link = "https://www.co.cowlitz.wa.us" + line['href']

        #Record today's data in the CSV
        csv_writer.writerow([websiteDateStr, todayCount, link])


    import matplotlib
    import matplotlib.pyplot as plt
    import os

    df = pd.read_csv('covidData.csv')
    df = df.reindex(columns= ['Date', 'New Cases', 'Daily Average', 'Seven Day Average', 'Fourteen Day Sum'])
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    #Calculate daily average based on the difference between reporting dates
    difference = df.diff(axis=0)['Date']
    df['Daily Average'] = df['New Cases']/difference.dt.days
    df.dropna(inplace=True, subset=['Daily Average'])

    #Make the date the index, then add rows for the missing dates using .asfreq
    df = df.set_index(['Date'])
    df.sort_index(inplace=True)
    df = df.asfreq(freq='1D') #Adds a record for each day currently not in the 

    #Backfill daily average
    df['Daily Average'] = df['Daily Average'].bfill()

    #Calculate 7-day average from rolling average of daily column
    df['Seven Day Average'] = df['Daily Average'].rolling(7).mean()
    #Create dataframe for 14-day average before removing NA
    df['Reporting Date'] = df.index
    df = df.last('5M')
    fourteenDayDF = df.copy()
    #Drop NA's from original dataframe
    df.dropna(inplace=True, subset=['Seven Day Average'])

    #Calculate values for fourteenDayDF then drop NA
    fourteenDayDF['Fourteen Day Sum'] = fourteenDayDF['Daily Average'].rolling(14).sum()*100000/110593
    fourteenDayDF.dropna(inplace=True, subset=['Fourteen Day Sum'])

    
    #Tabulate components of first chart: Most recent date, most recent cases, a filename, chart title, and x-labels
    mostRecentCases = int(df.last('1D')['New Cases'].values[0])
    mostRecentDate = pd.to_datetime(str(df.last('1D').index.values[0])) #Returns datetime

    filefriendlyDate = mostRecentDate.strftime("%Y%m%d") #Format example 20201219
    filelocation = f"{os.getcwd()}\\Graphs\\{filefriendlyDate}.png" #Complete file path for new graph

    mostRecentDate = mostRecentDate.strftime("%m/%d/%Y") #Convert to string
    chartTitle = f"Cowlitz County COVID-19 Cases Per Day      Most Recent: {mostRecentCases} cases on {mostRecentDate}"

    #Generate list of labels by filtering for Mondays in the dataframe
    filter = (df['Reporting Date'].dt.weekday == 0)
    #Create dataframe from filter
    mondaysDF = df.loc[filter].copy()
    #Move index into list
    xlabels = mondaysDF.index.tolist()
    #Create two lists for x ticks- one in datetime format for connecting to the index, and one in string to be the text label
    xlabels = [pd.to_datetime(str(x)).date() for x in xlabels]
    xlabelsText = [x.strftime("%m/%d/%Y") for x in xlabels]


    #Create plot of daily cases/7 day average
    plt.figure(figsize=(16,9))
    axes = plt.gca()
    axes.set_ylim([0,120])
    axes.tick_params(axis='y', labelsize=12)

    #Add line plot of seven day average, and fill in the area beneath it
    plt.plot(df.index.values, df['Seven Day Average'], color='orangered', linewidth = 3, label='Seven Day Rolling Average')
    plt.fill_between(df.index.values, df['Seven Day Average'], alpha = .10, color='orangered')

    #Add bar chart of raw new cases
    plt.bar(df.index.values, df['New Cases'], color='grey')

    #Add legend and title
    plt.legend(loc="upper center", fontsize = 14)
    plt.title(label=chartTitle, fontsize = 16)

    #Add y-axis grid lines
    plt.grid(axis='y')

    #Add x-axis ticks for every Monday
    plt.xticks(ticks=xlabels, labels=xlabelsText, rotation = 70, horizontalalignment = 'center', va='top')

    plt.savefig(filelocation, dpi=400)
    #plt.show()


    #Compose Tweet and send
    message = f'Cowlitz County reported {mostRecentCases} new cases on {mostRecentDate}. Link to official data here: {link}'
    COVIDModule.PostMediaTweet(filelocation, message)


    #Tabulate components of second chart
    from matplotlib.lines import Line2D

    #Generate colored lines to be used in legend
    colors = ['red', 'gold', 'green']
    custom_lines = [Line2D([0], [0], color = item, lw=11, alpha= .5) for item in colors]
    legendLabels = ["HIGH COVID Activity: Greater than 350 cases per 100,000 population in 14-day period", "MODERATE COVID Activity: 50 to 350 cases per 100,000 population in 14-day period",
    "LOW COVID Activity: Fewer than 50 cases per 100,000 population in 14-day period"]

    #Generate x labels from Mondays
    #Generate list of labels by filtering for Mondays in the dataframe
    filter = (fourteenDayDF['Reporting Date'].dt.weekday == 0)
    #Create dataframe from filter
    mondaysDF = fourteenDayDF.loc[filter].copy()
    #Move index into list
    xlabels = mondaysDF.index.tolist()
    #Create two lists for x ticks- one in datetime format and one in string
    xlabels = [pd.to_datetime(str(x)).date() for x in xlabels]
    xlabelsText = [x.strftime("%m/%d/%Y") for x in xlabels]

    mostRecentFourteenValue = int(fourteenDayDF.last('1D')['Fourteen Day Sum'].values[0])
    filelocation = f"{os.getcwd()}\\Graphs\\{filefriendlyDate}14dayperpop.png"
    fourteenDaysAgo = pd.to_datetime(str(fourteenDayDF.last('14D').index.values[0]))
    fourteenDaysAgo = fourteenDaysAgo.strftime("%m/%d/%Y")
    chartTitle = f"Cowlitz County 14-Day COVID Cases Per 100,000 Population\nMost Recent: ~{mostRecentFourteenValue} cases per 100,000 people {fourteenDaysAgo} thru {mostRecentDate}"

    #Thresholds here: https://www.doh.wa.gov/Portals/1/Documents/1600/coronavirus/DecisionTree-K12schools.pdf
    activityLevelThresholds = [50,350]

    #Create plot of 14 day totals per 100,000 pop
    plt.figure(figsize=(16,9))
    axes = plt.gca()
    axes.tick_params(axis='y', labelsize=12)

    plt.plot(fourteenDayDF.index.values, fourteenDayDF['Fourteen Day Sum'], color='steelblue', linewidth = 3, zorder=3)
    plt.fill_between(fourteenDayDF.index.values, fourteenDayDF['Fourteen Day Sum'], alpha = .40, color='slategrey', zorder=2)

    plt.legend(custom_lines, legendLabels, loc='center left', fontsize = 12, framealpha=1)
    plt.title(label=chartTitle, fontsize = 16)
    plt.grid(axis='y')
    plt.yticks(ticks=range(0, 650, 50))
    plt.xticks(ticks=xlabels, labels=xlabelsText, rotation = 70, horizontalalignment = 'center', va='top')
    plt.gca().axhspan(ymin = 0, ymax = activityLevelThresholds[0], facecolor='green', alpha=.15, zorder= 1)
    plt.gca().axhspan(ymin = activityLevelThresholds[0], ymax = activityLevelThresholds[1], facecolor='gold', alpha=.15, zorder= 1)
    plt.gca().axhspan(ymin = activityLevelThresholds[1], ymax = 600, facecolor='red', alpha=.15, zorder= 1)

    plt.savefig(filelocation, dpi=400, facecolor='white')

    #Compose tweet and send
    if int(mostRecentFourteenValue) > activityLevelThresholds[1]:
        activityLevel = 'HIGH'
    elif int(mostRecentFourteenValue) < activityLevelThresholds[0]:
        activityLevel = 'LOW'
    else:
        activityLevel = 'MODERATE'

    message = f"COVID activity \"{activityLevel}\" per DOH guidelines to educators. DOH guide here: https://www.doh.wa.gov/Portals/1/Documents/1600/coronavirus/DecisionTree-K12schools.pdf"
    COVIDModule.PostMediaTweet(filelocation, message)
    

#Find all list items containing daily data info - used for original batch scrape
"""     
items = soup.find_all('li')
items = [item for item in items if "Daily Data Summary for" in item.text]
releases = []
for item in items:
    if len(item.a.text) > 0:
        link = "https://www.co.cowlitz.wa.us/" + item.a['href']
        date = item.a.text.lstrip()
        releases.append(Release(date, link, ""))

releases = [release for release in releases if release.datedate >= datetime.datetime(2020,9,28,0,0).date()]
releases.sort(key= lambda x: x.datedate)

import tabula

for release in releases:
    print(release.datestr)
    print(release.datedate)
    print(release.link)

    try:
        df = tabula.read_pdf(release.link, pages='all')
    except:
        print("Error with link\n")
        error_writer.writerow([release.datestr, "Link", release.link])
        continue
    
    try:
        #CSV format: Date, New Cases, Link
        activeCaseLine = df[1]['Cowlitz County COVID-19 Case Update'][4]
        release.cases = activeCaseLine.split("+ ")[1]
        print(release.cases, "\n")
        csv_writer.writerow([release.datestr, release.cases, release.link])
    except:
        #CSV format: Date, Error, Supporting Info
        print("Error with format\n")
        error_writer.writerow([release.datestr, "Format", release.link])
        continue
"""