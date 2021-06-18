# Cowlitz-COVID-Tracking
Twitter bot to scrape COVID releases from Cowlitz County's website and tweet an updated graph daily

## What for?
I had several issues with how my county reported COVID-19 case counts:
- Releases were irregular. Sometimes daily, often not.
- Releases weren't standardized per day (e.g. 150 cases over 5 days is the same rate as 30 cases in 1 day)
- Releases didn't included any visualizations for trends over time

## How does it work?
The script reads county's website. If it finds the most recent data isn't in the existing CSV, it records the new data,
creates updated COVID-19 case plots, and then tweets it out.
