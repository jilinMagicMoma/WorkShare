
import requests

def download_page(url, path_name):
	try:
		res = requests.get(url, timeout=30)
		if res.ok:
			return res.content
		else:
			return None
	except Exception as e:
		print 'Fail to open page:', url
		return None

def validate_url(url):
	try:
		res = requests.get(url, timeout=30)
		if res.ok:
			return True
		else:
			return False
	except:
		return False
