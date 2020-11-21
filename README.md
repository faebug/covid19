## Covid 19 reports based on data.gov.uk

COVID-19 data from data.gov.uk. "Average" is a short-hand way to refer to the moving cumulative total COVID-19 positive test cases over 7 days given as a daily reported figure. Figures are calculated by using:
* Daily numbers of ''newCasesByPublishDate'' from data.gov.uk
* Adding up the past 7 days reported cases for each date
* Dividing by the ONS latest estimated population, multiplying by 100,000. E.g. Gateshead ONS official population estimate is 202,055
Sources:
1. [Developers guide](https://coronavirus.data.gov.uk/developers-guide)
2. [mid-2019: April 2020 local authority district codes](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland)

Created using Pywikibot and [Plotly](https://plotly.com/python). Last 28 days are shown with average calculated for the 7 days inclusive before each data point plotted. Will continue to automatically update on a daily basis while figures are high (i.e. above 100).

**From 16 November 2020** the data systematically changed to count cases *locally* regardless of where someone was registered with a GP. Probably due to the very high population density of students in Newcastle Upon Tyne, this had a dramatic effect of appearing to trebling cases overnight, when the reality was that cases in the city had been massively under reported. Refer to [PHE official statement](https://www.gov.uk/government/publications/covid-19-geographical-allocation-of-positive-cases/geographical-allocation-of-positive-covid-19-cases).

Note that [NYTimes](https://www.nytimes.com/interactive/2020/world/europe/united-kingdom-coronavirus-cases.html#map) is a good comparison, which uses the same datasets, but thier ONS census data is from 2011, so the figures are different when calculating *total cases/population \* 100,000*, but should give identical trend lines.
