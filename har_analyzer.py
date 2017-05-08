#--------------------------------------------------------------------
# Tim Zhang
# CSE534: Final Project
# ===
# This Python3 program implements a HAR analyzer which utilizes the
# haralyzer library for basic parsing of HAR files and some analysis.
# 
# ===
# COMMAND LINE ARGUMENTS:
#--------------------------------------------------------------------
import sys
import json
from haralyzer import HarParser, HarPage

#--------------------------------------------------------------------
# Parses HAR file via haralyzer along with custom logic to isolate
# the main HTML document of the website.
#--------------------------------------------------------------------
def parse_HAR(path, website):
	with open(path, 'r') as f:
		har_parser = HarParser(json.loads(f.read()))

		for page in har_parser.pages:
			print("Page URL " + str(page.url))
			print("Page hostname " + str(page.hostname))
			print("HTML load time " + str(page.html_load_time) + " miliseconds")
			print("CSS load time " + str(page.css_load_time) + " miliseconds")
			print("JS load time " + str(page.js_load_time) + " miliseconds")
			print("Image load time " + str(page.image_load_time) + " miliseconds")
			print("Page size " + str(page.page_size) + ' bytes')
			print("Text size " + str(page.text_size) + ' bytes')
			print("JS size " + str(page.js_size) + ' bytes')
			print("Image size " + str(page.image_size) + ' bytes')

			for html_file in page.html_files:
				content = str(html_file).lower()

				# Only consider the content which is the HTML document
				if "!doctype html" in content:

					# Try URL with www.
					if "'headers': [{'value': 'www." + website + "', 'name': 'host'}" in content or "'headers': [{'name': 'host', 'value': 'www." + website + "'}" in content:
						print(html_file['response']['content']['size'])

					# Try without www.
					elif "'headers': [{'value': '" + website + "', 'name': 'host'}" in content or "'headers': [{'name': 'host', 'value': '" + website + "'}" in content:
						print(html_file['response']['content']['size'])

			print('\n')

#--------------------------------------------------------------------
# Global resources
#--------------------------------------------------------------------
# HAR categories
categories = ['', 'category/Top/Arts', 'category/Top/Business', 'category/Top/Computers', 
			  'category/Top/Games', 'category/Top/Health', 'category/Top/Home', 
			  'category/Top/Shopping', 'category/Top/News', 'category/Top/Recreation', 
			  'category/Top/Science', 'category/Selected/Random']

# File directories
har_dir = 'HAR/'

#--------------------------------------------------------------------
# Iterate over HAR files and save metrics
#--------------------------------------------------------------------
parse_HAR(har_dir + '/Random/Desktop/allure.com.har', 'allure.com')
parse_HAR(har_dir + '/Random/Mobile/allure.com.har', 'allure.com')
