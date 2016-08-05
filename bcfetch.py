#!/usr/bin/env python3

'''
	Fetch content from the British Council pages and wrap in the eTekkatho HTML
	
	1. Get first page
		a. parse the page
			i.  get links
			ii. remove any links that aren't relevant
			iii.save the css file *** just manually add some css styles
		b. get the content div
		c. save the content filet the above steps
	3. End when no more urls in list
	
'''

import urllib
import sys
from bs4 import BeautifulSoup
from bcprocess import ProcessContent
import requests
import os
import html5lib

class BCFetch():
	'Class for wrapping resource content in the eTekkatho HTML header and footer'
	
	name = 'etekkatho-spider'
	startURL = 'http://learnenglishteens.britishcouncil.org/grammar-vocabulary/grammar-videos?page='
	contentURLs = []
	
	# Constructor
	def __init__(self):
		self.startCrawling()
	
	def startCrawling(self):
		# Get the page links
		try:
			for i in range(0,5):
				print('Page:', i)
				homepage = ''
				page = requests.get(self.startURL+str(i)).text
				
				html = BeautifulSoup(page, 'html5lib')
				html.prettify()
				for link in html.findAll('a', href=True):
					# Filter the list of links for the relevant sub-pages
					ahref = link['href']
					ahref = ahref.split('?', 1)[0]
				
					# Add them to the contentURLs list
					if 'grammar-vocabulary/grammar-videos' in ahref and ahref not in self.contentURLs:
						self.contentURLs.append(ahref)
			
				# Build the home page
				homepage += str(html.find('div', class_="content-inner"))
			
			# Makes the links relative
			homepage = BeautifulSoup(homepage, 'html.parser')
			for a in homepage.findAll('a', href=True):
  				a['href'] = a['href'].replace('/grammar-vocabulary/grammar-videos/', '')
			
			# Tidy up the content
			[s.extract() for s in homepage.find_all('h2', class_='element-invisible')]
			[s.extract() for s in homepage.find_all('div', class_='item-list')]
			[s.extract() for s in homepage.find_all('div', class_='views-field-name')]
			
			# Images
			for img in homepage.findAll('img', src=True):
				# Makes the links relative
				imgURL = img['src'].split('?', 1)[0]
				imagefilename = imgURL.rsplit('/', 1)[-1]
				urllib.request.urlretrieve(img['src'], 'resources/pages/'+imagefilename)
				
				# Save the images and update the paths
				img['src'] = img['src'].replace(img['src'], imagefilename)
  				
			# Save the dir page content in the content root folder
			pc = ProcessContent()
			pc.wrapAndWrite(str(homepage), '')
			
			# Parse the content sub-pages
			self.parsePages()
			
		except urllib.error.HTTPError:
			print('http error')
		
	def parsePages(self):
		# Loop over the pages
		self.contentURLs.pop(0)
		print('Processing', len(self.contentURLs), 'pages...')
		for url in self.contentURLs:
			print('------------------------------------------------------')
			print('Working on: ', url)
			# Get the page content
			content = ''
			videoFound = False
			page = requests.get('http://learnenglishteens.britishcouncil.org'+url).text	
			html = BeautifulSoup(page, 'html5lib')
			html.prettify()
			content = html.findAll("div", {"id": "node-article-full-group-content"})
			
			# Create subdir
			subdir = url.rsplit('/', 1)[-1]
			if not os.path.exists('resources/pages/'+subdir):
				os.mkdir('resources/pages/'+subdir);
			
			'''
			yes = html.find('video')
			print(yes)
			'''
			
			# Save media
			for video in content[0].findAll('video', src=True):
				print('>>>> Video found')
				videoFound = True
				# Makes the links relative
				videoURL = video['src']
				videoURL = videoURL.split('?', 1)[0]
				videofilename = videoURL.rsplit('/', 1)[-1]
				
				# Save the video
				urllib.request.urlretrieve(video['src'], 'resources/pages/'+subdir+'/'+videofilename) 
				
				# Update the path
				video['src'] = video['src'].replace(video['src'], videofilename)
  			
			if not videoFound:
				dataVid = content[0].find("div", {"class": "viddler-auto-embed"})
				print('>>>> Viddler found')
				vidID = dataVid['data-video-id']
				
				print('http://www.viddler.com/file/p/'+vidID+'.mp4?vfid=7782055d4424d3d4aadf6dbd12ffa429&ec_rate=63.695603550295864&ec_prebuf=60')
				
				# Save the video
				try:
					urllib.request.urlretrieve('http://www.viddler.com/file/p/'+vidID+'.mp4?vfid=7782055d4424d3d4aadf6dbd12ffa429&ec_rate=63.695603550295864&ec_prebuf=60', 'resources/pages/'+subdir+'/'+vidID+'.mp4') 
								
					videoHTML = '<video width="100%" x-webkit-airplay="allow" type="video/mp4" src="'+vidID+'.mp4" controls="controls"></video>'
				
					mediaContainer = content[0].find("div", {"class": "field-name-field-media"})
					mediaContainer.insert(1, videoHTML)
				except urllib.error.HTTPError:
					print('Error fetching the video file.')
  					
  			# Save files
			for file in content[0].findAll("span", {"class": "file"}):
				print('>>>> File found')
				
				a = file.find('a')
				filename = a['href'].rsplit('/', 1)[-1]
				print(filename)
				
				# Save the file
				urllib.request.urlretrieve(a['href'], 'resources/pages/'+subdir+'/'+filename) 
				
				# Update the path
				a['href'] = a['href'].replace(a['href'], filename)
  			
  			# Tidy up and remove excess content
			[s.extract() for s in content[0].find_all('div',  {"id": "footer-nav"})]
			[s.extract() for s in content[0].find_all('div',  {"class": "field-name-comment-count"})]
			[s.extract() for s in content[0].find_all('div',  {"class": "field-collection-container"})]
			[s.extract() for s in content[0].find_all('div',  {"class": "field-name-rate"})]
			[s.extract() for s in content[0].find_all('div',  {"id": "node-article-full-group-taxonomy"})]
			[s.extract() for s in content[0].find_all('div',  {"class": "sharethis-buttons"})]
  				
			# Save the page
			pc = ProcessContent()
			pc.wrapAndWrite(str(content[0]), subdir)

BCFetch()    
    
            