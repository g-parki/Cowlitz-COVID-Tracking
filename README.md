# Cowlitz-COVID-Tracking
Twitter bot to scrape COVID releases from Cowlitz County's website and tweet an updated graph daily

## What for?
I had several issues with how my county reported COVID-19 case counts:
- Releases were irregular. Sometimes daily, often not.
- Releases weren't standardized per day (e.g. 150 cases over 5 days is the same rate as 30 cases in 1 day)
- Releases didn't include any visualizations for trends over time

## How does it work?
The script reads county's website. If it finds the most recent data isn't in the existing CSV, it records the new data,
creates updated COVID-19 case plots, and then tweets it out.

## Samples
### Chart Showing Case Counts
![20201231](https://user-images.githubusercontent.com/61096711/122514381-c0306680-cfc0-11eb-83c2-df92656db58d.png)
### Chart Showing Activity Level Classification
![2020122214dayperpop](https://user-images.githubusercontent.com/61096711/122514409-ccb4bf00-cfc0-11eb-87f5-42398d6eb634.png)
