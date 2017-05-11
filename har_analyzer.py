#--------------------------------------------------------------------
# Tim Zhang
# CSE534: Final Project
# ===
# This Python3 program implements a HAR analyzer which utilizes the
# haralyzer library for basic parsing of HAR files and analysis.
# 
# After parsing and storing the data various charts are generated.
# ===
# COMMAND LINE ARGUMENTS:
# 1. 'extractData' flag will extract data from HAR files and store
#    in analytics.txt file
# 2. 'printExtraction' flag will output extraction details
# 3. 'generateCharts' flag will construct charts from data
#--------------------------------------------------------------------
import sys
import json
from haralyzer import HarParser, HarPage
import numpy as np
import matplotlib.pyplot as plt

#--------------------------------------------------------------------
# Parses HAR file via haralyzer along with custom logic to isolate
# the main HTML document of the website.
# ---
# RETURNS: Dictionary of gathered HAR statistics
#--------------------------------------------------------------------
def parse_HAR(path, website):
	statistics = {}

	with open(path, 'r') as f:
		har_parser = HarParser(json.loads(f.read()))
		page = har_parser.pages[0]

		# Gather HAR statistics
		statistics['url'] = website
		statistics['html_load'] = page.html_load_time
		statistics['css_load'] = page.css_load_time
		statistics['js_load'] = page.js_load_time
		statistics['image_load'] = page.image_load_time
		statistics['page_size'] = page.page_size
		statistics['text_size'] = page.text_size
		statistics['js_size'] = page.js_size
		statistics['image_size'] = page.image_size

		# Gather HTML document size
		for html_file in page.html_files:
			content = str(html_file).lower()

			# Only consider the content which is the HTML document
			if "!doctype html" in content:

				# Try URL with www.
				if "'headers': [{'value': 'www." + website + "', 'name': 'host'}" in content or "'headers': [{'name': 'host', 'value': 'www." + website + "'}" in content:
					print('Main HTML file size ' + str(html_file['response']['content']['size']) + ' bytes')
					statistics['main_html_size'] = html_file['response']['content']['size']
					break

				# Try without www.
				elif "'headers': [{'value': '" + website + "', 'name': 'host'}" in content or "'headers': [{'name': 'host', 'value': '" + website + "'}" in content:
					print('Main HTML file size ' + str(html_file['response']['content']['size']) + ' bytes')
					statistics['main_html_size'] = html_file['response']['content']['size']
					break

				else:
					statistics['main_html_size'] = -1

			else:
				statistics['main_html_size'] = -1

		return statistics

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
sites_dir = 'Websites/'

#--------------------------------------------------------------------
# Iterate over HAR files and save metrics
#--------------------------------------------------------------------
successful = 0  # Tracks number of successfully generated mobile and desktop HTML docs
success = []    # Holds names of successful websites
failed = []     # Holds URLs of failed websites

if sys.argv[1] == 'extractData':

	for category in categories:

		if category == '':
			category = 'All'
		else:
			category = category.split('/')[2]

		category_successful = 0  # Number of sucesses in a particular category

		sites = open(sites_dir + category + '/sites.txt', 'r').read()
		sites = sites.split('\n')[:-1]

		# Get HAR analytics from each site
		for site in sites:
			print('\nAnalysing Desktop ' + str(site))
			desktop = parse_HAR(har_dir + '/' + category + '/Desktop/' + site + '.har', site)

			print('\nAnalysing Mobile ' + str(site))
			mobile = parse_HAR(har_dir + '/' + category + '/Mobile/' + site + '.har', site)

			# Check if the main HTML file was extractable
			if 'main_html_size' in desktop and 'main_html_size' in mobile:

				# Unable to extract the HTML resource
				if int(desktop['main_html_size']) < 0 or int(mobile['main_html_size']) < 0:
					failed.append(site)
					print('Bad extraction...')
				
				else:
					successful += 1
					category_successful += 1
					open(sites_dir + category + '/analytics.txt', 'a+').write(str(desktop) + '\n' + str(mobile) + '\n---\n')

			# Unable to load the website
			else:
				failed.append(site)
				print('Bad website...')

			print('==========')

		success.append(category_successful)

#--------------------------------------------------------------------
# Display program status measurements
#--------------------------------------------------------------------
if sys.argv[2] == 'printExtraction' and sys.arv[1] == 'extractData':
	# Display total successful measurements
	print('Successfully extracted ' + str(successful) + ' main HTML resources.')
	print(successful)

	# Display category specific measurements
	i = 0
	for category in categories:
		if category == '':
			category = 'All'
		else:
			category = category.split('/')[2]

		print('\tSuccessfully extracted ' + str(success[i]) + ' in ' + str(category))
		i += 1

	# Display failed websites
	print('\n---------\nFailed websites:')

	for site in failed:
		print(site)

#--------------------------------------------------------------------
# Analyze saved data from analytics.txt
#--------------------------------------------------------------------
data = {}  # Holds data gathered for each category

for category in categories:

	if category == '':
		category = 'All'
	else:
		category = category.split('/')[2]

	# General counters
	total = 0        # Total number of sites in category
	insensitive = 0  # Number of mobile insensitive sites in category

	# Data size metrics
	insensitive_page_reduction = 0   # 
	insensitive_html_reduction = 0   # 
	insensitive_js_reduction = 0     # 
	insensitive_image_reduction = 0  # 

	aware_page_reduction = 0         # 
	aware_html_reduction = 0         # 
	aware_js_reduction = 0           # 
	aware_image_reduction = 0        # 

	# Page load metrics
	insensitive_html_load_reduction = 0   #
	insensitive_css_load_reduction = 0    #
	insensitive_js_load_reduction = 0     #
	insensitive_image_load_reduction = 0  #

	aware_html_load_reduction = 0         #
	aware_css_load_reduction = 0          #
	aware_js_load_reduction = 0           #
	aware_image_load_reduction = 0        #

	# Parse analytics.txt file
	sites = open(sites_dir + category + '/analytics.txt', 'r').read()
	sites = sites.split('---\n')[:-1]

	# Generate per-site measurements
	for site in sites:
		desktop = json.loads(site.split('\n')[0].replace("'", "\""))
		mobile = json.loads(site.split('\n')[1].replace("'", "\""))

		total += 1

		# If the main HTML document has the same size the site is mobile indifferent
		if desktop['main_html_size'] == mobile['main_html_size']:
			insensitive += 1
			insensitive_page_reduction += desktop['page_size'] - mobile['page_size']
			insensitive_html_reduction += desktop['text_size'] - mobile['text_size']
			insensitive_js_reduction += desktop['js_size'] - mobile['js_size']
			insensitive_image_reduction += desktop['image_size'] - mobile['image_size']

			insensitive_html_load_reduction += desktop['html_load'] - mobile['html_load']
			insensitive_css_load_reduction += desktop['css_load'] - mobile['css_load']
			insensitive_js_load_reduction += desktop['js_load'] - mobile['js_load']
			insensitive_image_load_reduction += desktop['image_load'] - mobile['image_load']
		
		# Else, gather mobile sensitive metrics
		else:
			aware_page_reduction += desktop['page_size'] - mobile['page_size']
			aware_html_reduction += desktop['text_size'] - mobile['text_size']
			aware_js_reduction += desktop['js_size'] - mobile['js_size']
			aware_image_reduction += desktop['image_size'] - mobile['image_size']

			aware_html_load_reduction += desktop['html_load'] - mobile['html_load']
			aware_css_load_reduction += desktop['css_load'] - mobile['css_load']
			aware_js_load_reduction += desktop['js_load'] - mobile['js_load']
			aware_image_load_reduction += desktop['image_load'] - mobile['image_load']

	# Store measurements
	data[category] = {'aware': 1 - (insensitive / total),
					  'insensitive_page_reduction': (insensitive_page_reduction / insensitive) * 0.001,
					  'insensitive_html_reduction': (insensitive_html_reduction / insensitive) * 0.001,
					  'insensitive_js_reduction': (insensitive_js_reduction / insensitive) * 0.001,
					  'insensitive_image_reduction': (insensitive_image_reduction / insensitive) * 0.001,

					  'aware_page_reduction': (aware_page_reduction / (total - insensitive)) * 0.001,
					  'aware_html_reduction': (insensitive_html_reduction / (total - insensitive)) * 0.001,
					  'aware_js_reduction': (insensitive_js_reduction / (total - insensitive)) * 0.001,
					  'aware_image_reduction': (insensitive_image_reduction / (total - insensitive)) * 0.001,

					  'insensitive_html_load_reduction': (insensitive_html_load_reduction / insensitive),
					  'insensitive_css_load_reduction': (insensitive_css_load_reduction / insensitive),
					  'insensitive_js_load_reduction': (insensitive_js_load_reduction / insensitive),
					  'insensitive_image_load_reduction': (insensitive_image_load_reduction / insensitive),

					  'aware_html_load_reduction': (aware_html_load_reduction / (total - insensitive)),
					  'aware_css_load_reduction': (insensitive_css_load_reduction / (total - insensitive)),
					  'aware_js_load_reduction': (insensitive_js_load_reduction / (total - insensitive)),
					  'aware_image_load_reduction': (insensitive_image_load_reduction / (total - insensitive))}

	# Output results
	print('CATEGORY: ' + category)
	print('Mobile insensitive sites: ' + str(insensitive)) 
	print('Total sites: ' + str(total))
	print('Proportion of insensitive sites: ' + str(insensitive / total) + '\n')

	print('Average mobile insensitive data reduction: ' + str(data[category]['insensitive_page_reduction']) + ' KB')
	print('Average mobile insensitive HTML reduction: ' + str(data[category]['insensitive_html_reduction']) + ' KB')
	print('Average mobile insensitive JS reduction: ' + str(data[category]['insensitive_js_reduction']) + ' KB')
	print('Average mobile insensitive image reduction: ' + str(data[category]['insensitive_image_reduction']) + ' KB\n')

	print('Average mobile aware data reduction: ' + str(data[category]['aware_page_reduction']) + ' KB')
	print('Average mobile aware HTML reduction: ' + str(data[category]['aware_html_reduction']) + ' KB')
	print('Average mobile aware JS reduction: ' + str(data[category]['aware_js_reduction']) + ' KB')
	print('Average mobile aware image reduction: ' + str(data[category]['aware_image_reduction']) + ' KB\n')

	print('Average mobile insensitive HTML load time reduction: ' + str(data[category]['insensitive_html_load_reduction']) + ' ms')
	print('Average mobile insensitive CSS load time reduction: ' + str(data[category]['insensitive_css_load_reduction']) + ' ms')
	print('Average mobile insensitive JS load time reduction: ' + str(data[category]['insensitive_js_load_reduction']) + ' ms')
	print('Average mobile insensitive image load time reduction: ' + str(data[category]['insensitive_image_load_reduction']) + ' ms\n')

	print('Average mobile aware HTML load time reduction: ' + str(data[category]['aware_html_load_reduction']) + ' ms')
	print('Average mobile aware CSS load time reduction: ' + str(data[category]['aware_css_load_reduction']) + ' ms')
	print('Average mobile aware JS load time reduction: ' + str(data[category]['aware_js_load_reduction']) + ' ms')
	print('Average mobile aware image load time reduction: ' + str(data[category]['aware_image_load_reduction']) + ' ms\n===========\n')

#--------------------------------------------------------------------
# Plot data
#--------------------------------------------------------------------
if sys.argv[3] == 'generateCharts':

	#--------------------------------------------------------------------
	# All vs random
	#--------------------------------------------------------------------
	# Plot All vs Random awareness bar chart
	objects = ('All', 'Random')
	y_pos = np.arange(len(objects))
	awareness = [data['All']['aware'], data['Random']['aware']]
	 
	plt.bar(y_pos, awareness, align='center', alpha=0.5)
	plt.xticks(y_pos, objects)
	plt.ylabel('Proportion')
	plt.xlabel('Categories')
	plt.title('Proportion of Mobile Aware Websites: All vs Random')
	 
	plt.show()

	# Plot All vs Random data reduction
	n_groups = 2

	reduction_all = (data['All']['aware_page_reduction'], data['All']['insensitive_page_reduction'])

	reduction_random = (data['Random']['aware_page_reduction'], data['Random']['insensitive_page_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in Data: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random HTML data reduction
	n_groups = 2

	reduction_all = (data['All']['aware_html_reduction'], data['All']['insensitive_html_reduction'])

	reduction_random = (data['Random']['aware_html_reduction'], data['Random']['insensitive_html_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in HTML Data: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random JS data reduction
	n_groups = 2

	reduction_all = (data['All']['aware_js_reduction'], data['All']['insensitive_js_reduction'])

	reduction_random = (data['Random']['aware_js_reduction'], data['Random']['insensitive_js_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in JS Data: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random Image data reduction
	n_groups = 2

	reduction_all = (data['All']['aware_image_reduction'], data['All']['insensitive_image_reduction'])

	reduction_random = (data['Random']['aware_image_reduction'], data['Random']['insensitive_image_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in Image Data: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random HTML load reduction
	n_groups = 2

	reduction_all = (data['All']['aware_html_load_reduction'], data['All']['insensitive_html_load_reduction'])

	reduction_random = (data['Random']['aware_html_load_reduction'], data['Random']['insensitive_html_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in HTML Load Time: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random CSS load reduction
	n_groups = 2

	reduction_all = (data['All']['aware_css_load_reduction'], data['All']['insensitive_css_load_reduction'])

	reduction_random = (data['Random']['aware_css_load_reduction'], data['Random']['insensitive_css_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in CSS Load Time: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random JS load reduction
	n_groups = 2

	reduction_all = (data['All']['aware_js_load_reduction'], data['All']['insensitive_js_load_reduction'])

	reduction_random = (data['Random']['aware_js_load_reduction'], data['Random']['insensitive_js_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in JS Load Time: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	# Plot All vs Random Image load reduction
	n_groups = 2

	reduction_all = (data['All']['aware_image_load_reduction'], data['All']['insensitive_image_load_reduction'])

	reduction_random = (data['Random']['aware_image_load_reduction'], data['Random']['insensitive_image_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_all, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 error_kw=error_config,
	                 label='All')

	rects2 = plt.bar(index + bar_width, reduction_random, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 error_kw=error_config,
	                 label='Random')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in Image Load Time: All vs Random')
	plt.xticks(index + bar_width / 2, ('Aware', 'Insensitive'))
	plt.legend()

	plt.show()

	#--------------------------------------------------------------------
	# All categories
	#--------------------------------------------------------------------
	# Plot all categories awareness bar chart
	objects = ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random')
	y_pos = np.arange(len(objects))

	awareness = [data['All']['aware'], data['Arts']['aware'], data['Business']['aware'], data['Computers']['aware'], 
	             data['Games']['aware'], data['Health']['aware'], data['Home']['aware'], data['Shopping']['aware'],
	             data['News']['aware'], data['Recreation']['aware'], data['Science']['aware'], data['Random']['aware']]
	 
	plt.bar(y_pos, awareness, align='center', alpha=0.5)
	plt.xticks(y_pos, objects)
	plt.ylabel('Proportion')
	plt.xlabel('Categories')
	plt.title('Proportion of Mobile Aware Websites: All Categories')
	 
	plt.show()

	# Plot all categories data reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_page_reduction'], data['Arts']['aware_page_reduction'], 
					   data['Business']['aware_page_reduction'], data['Computers']['aware_page_reduction'],
					   data['Games']['aware_page_reduction'], data['Health']['aware_page_reduction'],
					   data['Home']['aware_page_reduction'], data['Shopping']['aware_page_reduction'],
					   data['News']['aware_page_reduction'], data['Recreation']['aware_page_reduction'],
					   data['Science']['aware_page_reduction'], data['Random']['aware_page_reduction'])

	reduction_insensitive = (data['All']['insensitive_page_reduction'], data['Arts']['insensitive_page_reduction'], 
		                     data['Business']['insensitive_page_reduction'], data['Computers']['insensitive_page_reduction'],
		                     data['Games']['insensitive_page_reduction'], data['Health']['insensitive_page_reduction'],
		                     data['Home']['insensitive_page_reduction'], data['Shopping']['insensitive_page_reduction'],
		                     data['News']['insensitive_page_reduction'], data['Recreation']['insensitive_page_reduction'],
		                     data['Science']['insensitive_page_reduction'], data['Random']['insensitive_page_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in Data: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories HTML data reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_html_reduction'], data['Arts']['aware_html_reduction'], 
					   data['Business']['aware_html_reduction'], data['Computers']['aware_html_reduction'],
					   data['Games']['aware_html_reduction'], data['Health']['aware_html_reduction'],
					   data['Home']['aware_html_reduction'], data['Shopping']['aware_html_reduction'],
					   data['News']['aware_html_reduction'], data['Recreation']['aware_html_reduction'],
					   data['Science']['aware_html_reduction'], data['Random']['aware_html_reduction'])

	reduction_insensitive = (data['All']['insensitive_html_reduction'], data['Arts']['insensitive_html_reduction'], 
		                     data['Business']['insensitive_html_reduction'], data['Computers']['insensitive_html_reduction'],
		                     data['Games']['insensitive_html_reduction'], data['Health']['insensitive_html_reduction'],
		                     data['Home']['insensitive_html_reduction'], data['Shopping']['insensitive_html_reduction'],
		                     data['News']['insensitive_html_reduction'], data['Recreation']['insensitive_html_reduction'],
		                     data['Science']['insensitive_html_reduction'], data['Random']['insensitive_html_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in HTML Data: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories JS data reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_js_reduction'], data['Arts']['aware_js_reduction'], 
					   data['Business']['aware_js_reduction'], data['Computers']['aware_js_reduction'],
					   data['Games']['aware_js_reduction'], data['Health']['aware_js_reduction'],
					   data['Home']['aware_js_reduction'], data['Shopping']['aware_js_reduction'],
					   data['News']['aware_js_reduction'], data['Recreation']['aware_js_reduction'],
					   data['Science']['aware_js_reduction'], data['Random']['aware_js_reduction'])

	reduction_insensitive = (data['All']['insensitive_js_reduction'], data['Arts']['insensitive_js_reduction'], 
		                     data['Business']['insensitive_js_reduction'], data['Computers']['insensitive_js_reduction'],
		                     data['Games']['insensitive_js_reduction'], data['Health']['insensitive_js_reduction'],
		                     data['Home']['insensitive_js_reduction'], data['Shopping']['insensitive_js_reduction'],
		                     data['News']['insensitive_js_reduction'], data['Recreation']['insensitive_js_reduction'],
		                     data['Science']['insensitive_js_reduction'], data['Random']['insensitive_js_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in JS Data: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories Image data reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_image_reduction'], data['Arts']['aware_image_reduction'], 
					   data['Business']['aware_image_reduction'], data['Computers']['aware_image_reduction'],
					   data['Games']['aware_image_reduction'], data['Health']['aware_image_reduction'],
					   data['Home']['aware_image_reduction'], data['Shopping']['aware_image_reduction'],
					   data['News']['aware_image_reduction'], data['Recreation']['aware_image_reduction'],
					   data['Science']['aware_image_reduction'], data['Random']['aware_image_reduction'])

	reduction_insensitive = (data['All']['insensitive_image_reduction'], data['Arts']['insensitive_image_reduction'], 
		                     data['Business']['insensitive_image_reduction'], data['Computers']['insensitive_image_reduction'],
		                     data['Games']['insensitive_image_reduction'], data['Health']['insensitive_image_reduction'],
		                     data['Home']['insensitive_image_reduction'], data['Shopping']['insensitive_image_reduction'],
		                     data['News']['insensitive_image_reduction'], data['Recreation']['insensitive_image_reduction'],
		                     data['Science']['insensitive_image_reduction'], data['Random']['insensitive_image_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('KB')
	plt.title('Average Reduction in Image Data: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories HTML load time reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_html_load_reduction'], data['Arts']['aware_html_load_reduction'], 
					   data['Business']['aware_html_load_reduction'], data['Computers']['aware_html_load_reduction'],
					   data['Games']['aware_html_load_reduction'], data['Health']['aware_html_load_reduction'],
					   data['Home']['aware_html_load_reduction'], data['Shopping']['aware_html_load_reduction'],
					   data['News']['aware_html_load_reduction'], data['Recreation']['aware_html_load_reduction'],
					   data['Science']['aware_html_load_reduction'], data['Random']['aware_html_load_reduction'])

	reduction_insensitive = (data['All']['insensitive_html_load_reduction'], data['Arts']['insensitive_html_load_reduction'], 
		                     data['Business']['insensitive_html_load_reduction'], data['Computers']['insensitive_html_load_reduction'],
		                     data['Games']['insensitive_html_load_reduction'], data['Health']['insensitive_html_load_reduction'],
		                     data['Home']['insensitive_html_load_reduction'], data['Shopping']['insensitive_html_load_reduction'],
		                     data['News']['insensitive_html_load_reduction'], data['Recreation']['insensitive_html_load_reduction'],
		                     data['Science']['insensitive_html_load_reduction'], data['Random']['insensitive_html_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in HTML Load Time: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories CSS load time reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_css_load_reduction'], data['Arts']['aware_css_load_reduction'], 
					   data['Business']['aware_css_load_reduction'], data['Computers']['aware_css_load_reduction'],
					   data['Games']['aware_css_load_reduction'], data['Health']['aware_css_load_reduction'],
					   data['Home']['aware_css_load_reduction'], data['Shopping']['aware_css_load_reduction'],
					   data['News']['aware_css_load_reduction'], data['Recreation']['aware_css_load_reduction'],
					   data['Science']['aware_css_load_reduction'], data['Random']['aware_css_load_reduction'])

	reduction_insensitive = (data['All']['insensitive_css_load_reduction'], data['Arts']['insensitive_css_load_reduction'], 
		                     data['Business']['insensitive_css_load_reduction'], data['Computers']['insensitive_css_load_reduction'],
		                     data['Games']['insensitive_css_load_reduction'], data['Health']['insensitive_css_load_reduction'],
		                     data['Home']['insensitive_css_load_reduction'], data['Shopping']['insensitive_css_load_reduction'],
		                     data['News']['insensitive_css_load_reduction'], data['Recreation']['insensitive_css_load_reduction'],
		                     data['Science']['insensitive_css_load_reduction'], data['Random']['insensitive_css_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in CSS Load Time: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories JS load time reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_js_load_reduction'], data['Arts']['aware_js_load_reduction'], 
					   data['Business']['aware_js_load_reduction'], data['Computers']['aware_js_load_reduction'],
					   data['Games']['aware_js_load_reduction'], data['Health']['aware_js_load_reduction'],
					   data['Home']['aware_js_load_reduction'], data['Shopping']['aware_js_load_reduction'],
					   data['News']['aware_js_load_reduction'], data['Recreation']['aware_js_load_reduction'],
					   data['Science']['aware_js_load_reduction'], data['Random']['aware_js_load_reduction'])

	reduction_insensitive = (data['All']['insensitive_js_load_reduction'], data['Arts']['insensitive_js_load_reduction'], 
		                     data['Business']['insensitive_js_load_reduction'], data['Computers']['insensitive_js_load_reduction'],
		                     data['Games']['insensitive_js_load_reduction'], data['Health']['insensitive_js_load_reduction'],
		                     data['Home']['insensitive_js_load_reduction'], data['Shopping']['insensitive_js_load_reduction'],
		                     data['News']['insensitive_js_load_reduction'], data['Recreation']['insensitive_js_load_reduction'],
		                     data['Science']['insensitive_js_load_reduction'], data['Random']['insensitive_js_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in JS Load Time: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()

	# Plot all categories Image load time reduction
	n_groups = 12

	reduction_aware = (data['All']['aware_image_load_reduction'], data['Arts']['aware_image_load_reduction'], 
					   data['Business']['aware_image_load_reduction'], data['Computers']['aware_image_load_reduction'],
					   data['Games']['aware_image_load_reduction'], data['Health']['aware_image_load_reduction'],
					   data['Home']['aware_image_load_reduction'], data['Shopping']['aware_image_load_reduction'],
					   data['News']['aware_image_load_reduction'], data['Recreation']['aware_image_load_reduction'],
					   data['Science']['aware_image_load_reduction'], data['Random']['aware_image_load_reduction'])

	reduction_insensitive = (data['All']['insensitive_image_load_reduction'], data['Arts']['insensitive_image_load_reduction'], 
		                     data['Business']['insensitive_image_load_reduction'], data['Computers']['insensitive_image_load_reduction'],
		                     data['Games']['insensitive_image_load_reduction'], data['Health']['insensitive_image_load_reduction'],
		                     data['Home']['insensitive_image_load_reduction'], data['Shopping']['insensitive_image_load_reduction'],
		                     data['News']['insensitive_image_load_reduction'], data['Recreation']['insensitive_image_load_reduction'],
		                     data['Science']['insensitive_image_load_reduction'], data['Random']['insensitive_image_load_reduction'])

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = .3

	opacity = 0.4
	error_config = {'ecolor': '0.3'}

	rects1 = plt.bar(index, reduction_aware, bar_width,
	                 alpha=opacity,
	                 color='#48FA91',
	                 error_kw=error_config,
	                 label='Aware')

	rects2 = plt.bar(index + bar_width, reduction_insensitive, bar_width,
	                 alpha=opacity,
	                 color='#1993CE',
	                 error_kw=error_config,
	                 label='Insensitive')

	plt.xlabel('Categories')
	plt.ylabel('ms')
	plt.title('Average Reduction in Image Load Time: All Categories')
	plt.xticks(index + bar_width / 2, ('All', 'Arts', 'Business', 'Computers', 'Games', 'Health', 'Home', 'Shopping', 'News', 'Recreation', 'Science', 'Random'))
	plt.legend()

	plt.show()