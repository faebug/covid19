#!/usr/bin/python
# -*- coding: utf-8 -*-

NOTICE='''
Generate 7-day moving average charts from coronavirus.data.gov for selected regions.
Sort location key by latest 7-day average cases.
Locally save in PNG and SVG, upload SVG only to Commons.

date: December 2020
author: Fae

Notes
LTLA = Lower Tier Local Authority
Population data from ONS, latest available
Covid data live from data.gov
'''
from requests import get
import plotly
import plotly.graph_objects as go
import pywikibot, urllib2, re, sys, os
from colorama import Fore, Back, Style
from colorama import init
init()

def up(source, pagetitle, desc, comment, iw):
	if source[:4] == 'http':
		source_url=source; source_filename=None
		# Resolve url redirects to find end target (the API will not do this)
		headers = { 'User-Agent' : 'Mozilla/5.0' }
		req = urllib2.Request(source_url, None, headers)
		res = urllib2.urlopen(req)
		source_url = res.geturl()
	else:
		source_url=None; source_filename=source

	if iw:
		site.upload(pywikibot.FilePage(site, 'File:' + pagetitle),
			source_filename=source_filename,
			source_url=source_url,
			comment=comment,
			text=desc,
			ignore_warnings = True,
			chunk_size= 400000,#1048576,
			#async = True,
			)
	else:
		site.upload(pywikibot.FilePage(site, 'File:' + pagetitle),
			source_filename=source_filename,
			source_url=source_url,
			comment=comment,
			text=desc,
			ignore_warnings = False,
			chunk_size = 400000,#1048576,
			#async = True,
			)

def get_data(url):
    response = get(url, timeout=10)
    if response.status_code >= 400:
        raise RuntimeError('Request failed: {}'.format(response.text))
    return response.json()

def get_line(area):
	ctype = "newCasesByPublishDate" # "cumCasesBySpecimenDate" #" #newCasesBySpecimenDate
	endpoint = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=ltla;areaName=' + area + '&structure={"date":"date","cases":"' + ctype + '"}'
	try:
		data = get_data(endpoint)
	except Exception as e:
		print Fore.MAGENTA, str(e)
		print Fore.CYAN + endpoint
		print area, Fore.WHITE
		return ''
	return data

def get_chart(info):
	chart = []
	for line in info[2:]:
		area, colour, population = line[0],line[1],line[2]
		linedata = get_line(area)
		linedata = linedata['data'][:35]
		last = sum([l['cases'] for l in linedata[0:7]])
		last = int((last * 100000.)/population)
		chart.append({
			"area":area,
			"colour":colour,
			"population":population,
			"data":linedata,
			"last":last
			})
	chart = sorted(chart, key=lambda x: x['last'], reverse=True)
	return chart

def addline(area, linecolour, population, data, last):
	global fig, endpoint, reportdate, triggerline
	reportdate = data[0]['date']
	cumA = []
	cumD = []
	cumL = []
	rmax = 28
	#if area == 'Newcastle upon Tyne':
	#	rmax = 28-4
	for r in range(0,rmax):
		cum = sum([data[c]['cases'] for c in range(r, r+7)])
		cum = int((cum * 100000.)/population)
		#if cum>1000:
		#	continue
		# Can check pop data in use by float(data['data'][r]['cases'])/float(data['data'][r]['cum'])
		cumD.append(data[r]['date'])
		cumP =cum
		cumA.append(cumP)
		if r % 7 == 0:
			cumL.append(cumP)
		else:
			cumL.append('')
		if cum>90:
			if triggerline==0:
				triggerline = 1  
	if triggerline>0 and triggerline<99:
		fig.add_trace(go.Scatter(x=[cumD[0], cumD[-1]], y=[100., 100.],
			line=dict(color="black", width=4, dash="dash"),
			showlegend=False,
			hoverinfo='skip'))
		triggerline = 100
	fig.add_trace(go.Scatter(x=cumD, y=cumA, name="{} {}".format(area, last), line=dict(color=linecolour, width=4), showlegend = True))
	fig.add_trace(go.Scatter(x=cumD, text=cumL, y=cumA, name=area, marker=dict(color=linecolour, size=8), mode='markers+text', textposition='top center', showlegend=False))

defaulttext = u"""== {{int:filedesc}} ==
{{information
|description = {{en|1=COVID-19 data from data.gov.uk. Figures are calculated by using:
* Daily numbers of ''newCasesByPublishDate'' from data.gov.uk
* Adding up the past 7 days reported cases for each date
* Dividing by the ONS latest estimated population, multiplying by 100,000. E.g. Gateshead ONS official population estimate is 202,055
Sources:
# https://coronavirus.data.gov.uk/developers-guide
# https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland (mid-2019: April 2020 local authority district codes)
Created using [[mw:Pywikibot|Pywikibot]] and [https://plotly.com/python/ Plotly]. Last 28 days are shown with average calculated for the 7 days inclusive before each data point plotted. Will continue to automatically update on a daily basis while figures are high (i.e. above 100).

Note that [https://www.nytimes.com/interactive/2020/world/europe/united-kingdom-coronavirus-cases.html#map NYTimes] is a good comparison, which uses the same datasets, but their ONS census data is from 2011, so the figures are "artificially" higher as these population figures will always be larger when calculating <code>''total cases/population * 100,000''</code>, but will give identical trend lines.}}
|date = 2020-09-28
|source = {{own}}
|author = Fæ
}}

== {{int:license-header}} ==
{{Cc-zero}}


[[Category:COVID-19 testing in the United Kingdom]]
[[Category:Images uploaded by Fæ]]
"""

chartArr = [
	[
		"COVID19 cases in Central London, 7 day total",
		#https://en.wikipedia.org/wiki/List_of_sub-regions_used_in_the_London_Plan
		"covidlondoncentral",
		('Camden', 'yellow', 270029.),
		#('City of London', 'darkblue', 9721.),
		('Kensington and Chelsea', 'purple', 156129.),
		('Islington', 'green', 242467.),
		('Lambeth', 'blue', 326034.),
		('Southwark', 'firebrick', 318830.),
		('Westminster', 'indigo', 261317.),
		],
	[
		"COVID-19 in Tyne and Wear metropolitan districts, 7 day avg per 100,000",
		"covidtyneandwear",
		('Newcastle upon Tyne', 'firebrick', 302820.),
		('Gateshead', 'purple', 202055.),
		('North Tyneside', 'orange', 207913.),
		('South Tyneside', 'blue', 150976.),
		('Sunderland', 'green', 277705.),
		('County Durham', 'indigo', 530094.),
		('Northumberland', 'darkblue', 320274),
		],
	[
		"COVID-19 cases in South London, 7 day total",
		"covidlondonsouth",
		('Bromley', 'blue', 386710.),
		('Croydon', 'firebrick', 386710.),
		('Kingston upon Thames', 'green', 177507.),
		('Merton', 'darkblue', 206548.),
		('Sutton', 'purple', 206349.),
		('Wandsworth', 'orange', 329677.),
		],
	[
		"COVID-19 cases in North London, 7 day total",
		"covidlondonnorth",
		('Barnet', 'darkblue', 395869.),
		('Enfield', 'green', 333794.),
		('Haringey', 'firebrick', 268647.),
		],
	[
		"COVID-19 cases in East London, 7 day total",
		"covidlondoneast",
		("Barking and Dagenham", 'darkblue', 212906.),
		("Bexley", "blue", 248287.),
		("Greenwich", "green", 287942.),
		#("Hackney", "red", 281120.), Repeated error getting Hackney
		("Havering", 'orange', 259552.),
		("Lewisham", 'magenta', 305842.),
		("Newham", 'olive', 353134.),
		("Redbridge",'plum', 305222.),
		("Tower Hamlets",'yellow', 324745.),
		("Waltham Forest",'beige', 276983.),
		],
	[
		"COVID-19 cases in West London, 7 day total",
		"covidlondonwest",
		("Brent", 'darkblue', 329771.),
		("Ealing", 'plum', 341806.),
		("Hammersmith and Fulham", 'orange', 185143.),
		("Harrow", 'yellow', 251160.),
		("Richmond upon Thames", 'blue', 198019.), 
		("Hillingdon", 'olive', 306870.),
		("Hounslow", 'red', 271523.),
		],
			]

if __name__ == '__main__':
	# AreaTypes region, utla, ltla, nation
	site = pywikibot.Site('commons','commons')
	# Populations are ONS MYE 2019
	for info in chartArr:
		fig = go.Figure()
		triggerline = 0
		title = info[0]
		filename = info[1]
		chartdata = get_chart(info)
		for line in chartdata:
			addline(line['area'], line['colour'], line['population'], line['data'], line['last'])
		fig.update_layout(title=title + ' to ' + reportdate,
			xaxis_title = "Date",
			yaxis_title="Cases per 100,000 people, 7 day total")
		fig.update_yaxes(rangemode="tozero")
		#fig.show()
		#continue
		page = pywikibot.ImagePage(site, u'File:' + title + '.svg')
		if page.exists() and len(sys.argv)<2:
			dd = None
			html = page.get()
			hist = page.getFileVersionHistory()
			comments = ":".join([c["comment"] for c in hist][:7])
			if re.search(reportdate, comments):
				print Fore.MAGENTA, "Date of {} found in upload history".format(reportdate), Fore.WHITE
				continue
			else:
				dd = re.sub("\|date = .*", "|date = " + reportdate, html, flags=re.I)
		else:
			print Fore.MAGENTA, "Creating page", page.title(), Fore.WHITE
			dd = defaulttext
		home = os.path.expanduser("~")
		local =    home + "/Downloads/TEMP/"+filename+".svg"
		localpng = home + "/Downloads/TEMP/"+filename+".png"
		fig.write_image(local, format="svg", width=1024, height = 768)
		fig.write_image(localpng, format="png", width=1024, height = 768)
		comment = "Update for " + reportdate
		pywikibot.setAction(comment)
		if len(sys.argv)<2:
			up(local, title, dd, "COVID-19 stats update for " + reportdate, True)
