import os
import optparse
import requests
import sys
import time
from bs4 import BeautifulSoup as BSoup

def modify(s):
	s = s.strip()
	s = s.replace(u',', ' ').replace(u'\t', u' ').replace(u'\n', u' ')
	s = u' '.join(filter(lambda x: x != u'', s.split(u' ')))

	return s

class PageLoader(object):
	def __init__(self, quiet = False):
		self.source_links = []
		self.key_words = ['location', 'locator', 'store', 'facebook']
		self.quiet = quiet
		self.done_links = set()
		self.folder = 'page_folder'
		
		self.source_file_path = 'links.txt'
		self.trace_file_path = 'record.txt'
		self.store_link_file_path = 'store_links.csv'
		self.no_keyword_store_file_path = 'no_key_word_store.csv'
		self.err_log_file = 'errorLog.txt'
		
		self.read_done_links()
		
	def add_key_words(self, *kw):
		self.key_words += kw

	def prepare_links(self):
		with open(self.source_file_path, 'r') as inFile:
			for line in inFile:
				self.source_links.append(line.strip())
	
	def record_done_links(self, link):
		with open(self.trace_file_path, 'a') as file:
			file.write(link+'\n')
	
	def read_done_links(self):
		if not os.path.isfile(self.trace_file_path):
			return
		with open(self.trace_file_path, 'r') as file:
			for line in file:
				self.done_links.add(line.strip())

	def error_log(self, *message):
		with open(self.err_log_file, 'a') as err_log:
			err_log.write(u','.join(message)+'\n')

	def print_error(self, *message):
		if self.quiet:
			return
		print ','.join(message)

	def print_message(self, *message):
		if self.quiet:
			return
		print ','.join(message)

	def log_store_link(self, *message):
		with open(self.store_link_file_path, 'a') as file:
			file.write((u','.join(message)+'\n').encode('utf-8'))
	
	def log_no_keyword_link(self, *message):
		with open(self.no_keyword_store_file_path, 'a') as file:
			file.write((u','.join(message)+'\n').encode('utf-8'))

	def download(self, fn, content):
		if not os.path.isdir(self.folder):
			os.mkdir(self.folder)
	
		fn.replace('/', '%^')
		fn = os.path.join(self.folder, fn+'.html')
		with open(fn, 'a') as file:
			file.write(content)
	
	def load(self):
		for link in self.source_links:
			if link in self.done_links:
				self.print_message(*[link, 'skipped'])
				continue

			if link == '':
				self.error_log(*['error', 'empty url'])
				self.record_done_links(link)
				continue
			
			self.print_message(*['trying', link])
			res = None
			if link.startswith('http'):
				urlList = [link]
			else:
				urlList = [r'http://'+link, r'http://wwww.'+link]
			error_message = {}

			for url in urlList:
				try:
					res = requests.get(url, timeout = 30)
					break
				except Exception as e:
					error_message[url] = 'Fail to open link or connecting timeout'

			if res is None:
				for error_url in error_message:
					self.print_error(*[link, error_url, modify(error_message[error_url])])
					self.error_log(*[link, error_url, modify(error_message[error_url])])
				self.record_done_links(link)
				continue
			
			#remove http:// from file name by [7:]
			self.download(url[7:], res.content)
			self.record_done_links(link)
	
	def parse(self):
		if not os.path.isdir(self.folder):
			print_message(*['nothing to parse'])
			return
		files = os.walk(self.folder).next()[2]
		for file in files:
			content = ''
			with open(os.path.join(self.folder, file), 'r') as in_file:
				content = in_file.read()
			if content == '':
				continue
			try:
				soup = BSoup(content)
			except Exception as e:
				self.print_error(*[file, modify('BSoup Parsing failed:  '+e.message)])
				self.error_log(*[file, modify('BSoup Parsing failed:  '+e.message)])
				continue
			
			key_word_found = False
			for a in soup('a'):
				for k in self.key_words:
					if k in a.text.lower():
						if 'href' in a.attrs:
							href = a.get('href')
						else:
							href = 'No href(probably loaded by js)'
						self.log_store_link(*[file, href])
						key_word_found = True
			if not key_word_found:
				self.log_no_keyword_link(*[file, 'no key word found'])
				self.print_message(*['No Key', file])
			else:
				self.print_message(*['OK', file])
			
			

if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option('-m', help='load and parse mode default parse', default='parse')
	
	options, args = parser.parse_args()

	pl = PageLoader()	
	if args != []:
		pl.add_key_words(args)

	if options.m == 'load':
		print 'Load page'
		pl.prepare_links()
		pl.load()
	else:
		print 'Parse '
		pl.parse()