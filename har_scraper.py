#--------------------------------------------------------------------
# Tim Zhang
# CSE534: Final Project
# ===
# This Python3 program implements a HAR scraper which runs over
# BrowserMob Proxy and Selenium with FireFox's Modify Headers plugin.
#
# Top websites from Alexa ranking are considered wrt their desktop
# and mobile assets.
#
# The URLs are gathered using the BeautifulSoup API and specific
# categories of content are investigated.
# ===
# COMMAND LINE ARGUMENTS:
# 1. 'scrapeAlexa' flag will scrape URLs from Alexa
# 2. Comma separated list of categories to be ignored during HAR
#    generation, used to selectively generate HAR files
#--------------------------------------------------------------------
from browsermobproxy import Server
from selenium import webdriver
import json
import httplib2
from bs4 import BeautifulSoup
import sys
import os.path

#--------------------------------------------------------------------
# Global resources
#--------------------------------------------------------------------
# Categories from Alexa
categories = ['', 'category/Top/Arts', 'category/Top/Business', 'category/Top/Computers', 
			  'category/Top/Games', 'category/Top/Health', 'category/Top/Home', 
			  'category/Top/Shopping', 'category/Top/News', 'category/Top/Recreation', 
			  'category/Top/Science']

# File directories
sites_dir = 'Websites/'
har_dir = 'HAR/'

#--------------------------------------------------------------------
# Scrape websites from Alexa
#--------------------------------------------------------------------
if sys.argv[1] == 'scrapeAlexa':
	http = httplib2.Http()
	all_sites = open(sites_dir + 'all_sites.txt', 'a+') # For tracking global info

	# Get top sites for each category
	for category in categories:
		if category == '':
			sites = open(sites_dir + 'All/sites.txt', 'w+')	
			print('Saving All contents to file.')
		else:
			sites = open(sites_dir + category.split('/')[2] + '/sites.txt', 'w+')		
			print('Saving ' + category.split('/')[2] + ' contents to file.')

		status, response = http.request('http://www.alexa.com/topsites/' + category)
		soup = BeautifulSoup(response, 'html.parser')

		for link in soup.find_all('div', attrs = {'class': 'site-listing'}):
			site = link.find('div', attrs = {'class': 'DescriptionCell'}).find('a').getText().replace("Https://", "").replace("www.", "")

			# Handle trailing /
			if site[-1] == '/':
				site = site[:-1]

		    # Only consider front pages
			if '/' in site:
				continue

			sites.write(site + '\n')
			all_sites.write(site.lower() + '\n')

		sites.close()

#--------------------------------------------------------------------
# Configure BrowserMob Proxy server
#--------------------------------------------------------------------
server = Server("browsermob-proxy-master/browsermob-dist/target/browsermob-proxy-2.1.5-SNAPSHOT/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy()

# Setup proxy FireFox browser
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())

driver = webdriver.Firefox(firefox_profile = profile)

# Add modify headers plugin
profile.add_extension("{b749fc7c-e949-447f-926c-3f4eed6accfe}.xpi")
profile.set_preference("modifyheaders.headers.count", 1)
profile.set_preference("modifyheaders.headers.action0", "Add")
profile.set_preference("modifyheaders.headers.name0", "User-Agent")
profile.set_preference("modifyheaders.headers.value0", "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3")
profile.set_preference("modifyheaders.headers.enabled0", True)
profile.set_preference("modifyheaders.config.active", True)
profile.set_preference("modifyheaders.config.alwaysOn", True)

mobile_driver = webdriver.Firefox(firefox_profile = profile)

# Set timeouts
driver.set_page_load_timeout(60)
mobile_driver.set_page_load_timeout(60)

#--------------------------------------------------------------------
# Get HAR files for each website in each category
#--------------------------------------------------------------------
categories.append('category/Selected/Random')

for category in categories:
	# Get site URLs from saved file
	if category == '':
		category = 'All'
	else:
		category = category.split('/')[2]

	# Skip categories already gathered
	if category in sys.argv[2].split(','):
		continue

	sites = open(sites_dir + category + '/sites.txt', 'r').read()
	sites = sites.split('\n')[:-1]

	print('Generating HAR files for ' + category + ' category...')

	# Get HAR for every site
	for site in sites:	
		website = 'http://www.' + site
		desktop_path = har_dir + '/' + category + '/desktop/' + site + '.har'
		mobile_path = har_dir + '/' + category + '/mobile/' + site + '.har'

		# Skip websites already gathered
		if os.path.isfile(desktop_path) or os.path.isfile(mobile_path):
			print('\t' + website + " HAR files already generated...")
			continue

		print('\tGenerating HAR file for ' + site + '...')

		# Get HAR file
		proxy.new_har(website, options = {'captureHeaders': True, 'captureContent': True})

		# Handle website timeout event, caused by ads
		try:
			driver.get(website)
		except Exception as e:
			print('\t' + website + ' timed out...')

		result = json.dumps(proxy.har, ensure_ascii=False)

		# Get mobile HAR file
		proxy.new_har(website, options = {'captureHeaders': True, 'captureContent': True})

		# Handle website timeout event
		try:
			mobile_driver.get(website)
		except Exception as e:
			print('\t' + website + ' mobile timed out...')

		mobile_result = json.dumps(proxy.har, ensure_ascii = False)

		# Write results to file
		with open(desktop_path, 'w') as f:
			f.write(result)

		with open(mobile_path, 'w') as f:
			f.write(mobile_result)

	print('Completed genrating HAR files for ' + category + ' category...\n')

#--------------------------------------------------------------------
# Shutdown services
#--------------------------------------------------------------------
driver.quit()
mobile_driver.quit()
server.stop()