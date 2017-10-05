import urllib2
import requests
import json

HOST = 'http://127.0.0.1:5000'


def get_data_from_url(url):

	req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 

	s = urllib2.urlopen(req)
	shtml = s.read()
	s.close()

	return shtml

def report_back(name,data):
	r = requests.post(HOST+'/submit_data', data = {'data':data,'name':name})
	print r
# report_back('dd')


while True:


	print '1'
	f = urllib2.urlopen(HOST+'/get_new')
	html = f.read()
	data = json.loads(html)
	f.close()

	print '2'

	print data['name'], data['url']
	print '3'

	html = get_data_from_url(data['url'])

	print '4'

	print 'Prep send'
	report_back(data['name'], html)



