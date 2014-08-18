#-*- coding: utf-8 -*-

#checking if an url is openable

import os
import requests
import sys

if len(sys.argv) < 2:
	print 'please provide the file path'
	exit(0)

file = sys.argv[1]

if not os.path.isfile(file):
	print 'fail to find the file by file-path, please check its existence'
	exit(0)
	
allLinks = []
with open(file, 'r') as f:
	allLinks += map(lambda x: x.strip(), f.readlines())

def log(url):
	with open('available.txt', 'a') as f:
		f.write(url+'\n')
def eLog(url):
	with open('fail.txt', 'a') as f:
		f.write(url+'\n')
for url in allLinks:
	try:
		res = requests.get(url, timeout = 30)
		if res.ok:
			log(url)
		else:
			eLog(url)
	except Exception as e:
		print url, 'timeout!'
		eLog(url)

