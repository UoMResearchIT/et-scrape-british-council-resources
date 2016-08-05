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
				
				html = BeautifulSoup(page, 'html.parser')
				html.prettify()
				for link in html.findAll('a', href=True):
					# Filter the list of links for the relevant sub-pages
					ahref = link['href']
					ahref = ahref.split('?', 1)[0]
				
					# Add them to the contentURLs list
					if 'grammar-vocabulary/grammar-videos' in ahref and ahref not in self.contentURLs:
						self.contentURLs.append(ahref)
			
				# Build the home page
				homepage += str(html.find_all('div', class_="content-inner"))
			
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
			page = requests.get('http://learnenglishteens.britishcouncil.org'+url).text
			html = BeautifulSoup(page, 'html.parser')
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
				# Makes the links relative
				videoURL = video['src']
				videoURL = videoURL.split('?', 1)[0]
				videofilename = videoURL.rsplit('/', 1)[-1]
				
				# Save the video
				urllib.request.urlretrieve(video['src'], 'resources/pages/'+subdir+'/'+videofilename) 
				
				# Update the path
				video['src'] = video['src'].replace(video['src'], videofilename)
  				
			# Save the page
			pc = ProcessContent()
			pc.wrapAndWrite(str(content), subdir)

BCFetch()    
    
            