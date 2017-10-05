from flask import Flask
from threading import Thread, Lock
from flask import request
import json
from datetime import datetime
from flask import render_template

app = Flask(__name__)

mylock = Lock()




# Probably will be replaced by a different way to store data
f = open('list_1','r')
rows = [row.strip().split('|||') for row in f.readlines()]

my_dict = dict()
for row in rows:
	my_dict[row[0]] = [row[1],row[2]]



waiting_list = []
processing_list = []
processed_list = []


worker_dict = dict()
worker_status = dict()
worker_lastcheck = dict()

for k in my_dict.keys():
	if my_dict[k][1] == '0':
		waiting_list.append([k,my_dict[k][0],my_dict[k][1]])
	else:
		processed_list.append([k,my_dict[k][0],my_dict[k][1]])


# Sanity Check
print waiting_list
print processed_list

@app.route('/')
def hello_world():
	# Probably won't need lock as it's just a presentation
	with mylock:
		new_l = []

		for k in my_dict.keys():
			obj = my_dict[k]
			new_l.append([k,obj[0],obj[1]])

		w_l = []

		for k in worker_status.keys():
			o = worker_status[k]

			w_l.append([k,o])



	processed_count = len(processed_list)

	return render_template('index.html',rows=new_l,workers=w_l,mc=processed_count)

@app.route('/get_new')
def get_new():
	# Race Condition Sanity Check
	print 'GET NEW METHOD'
	print '1'
	with mylock:
		c_ip = request.remote_addr

		worker_lastcheck[c_ip] = datetime.now()

		print '2'

		if not c_ip in worker_status:
			worker_status[c_ip] = 1


		if worker_status[c_ip] == 2:
			work = worker_dict[c_ip]
			return json.dumps({'name':work[0],'url':work[1]})

		print '3'


		if len(waiting_list) == 0:
			return '[]'
		else:
			c_pair = waiting_list.pop()

			worker_dict[c_ip] = c_pair
			worker_status[c_ip] = 2

			work = worker_dict[c_ip]
		print '4'

	return json.dumps({'name':work[0],'url':work[1]})





@app.route('/submit_data',methods=['POST'])
def submit_data():
	# Race condition debug
	print 'SUBMIT Method'
	with mylock:
		c_ip = request.remote_addr
		print '1'


		# Avoid zombie socket suddenly submitting data
		if worker_status[c_ip] != 2:
			return ''
		print '2'


		# The future 
		f = open('RAW/'+request.form['name'],'w')
		f.write(request.form['data'].encode('utf-8'))
		f.close()

		names = parse_html(request.form['data'])
		add_name_to_list(names)

		print '3'

		name = request.form['name']


		worker_status[c_ip] = 1
		my_dict[name][1] = 1

		processed_list.append(worker_dict[c_ip])
		print '4'


	check_dead_worker()
	print '5'

	return ''

def add_name_to_list(l1):
	for l in l1:
		if not l[0] in my_dict:
			my_dict[l[0]] = [l[1],0]
			waiting_list.append([l[0],l[1],0])




def check_dead_worker():
	# Race condition debugging
	print '\tCHECK DEAD WORKER'
	with mylock:
		print '\t1'
		c_time = datetime.now()
		for k in worker_status.keys():
			print '\t\t2.1'
			diff = c_time - worker_lastcheck[k]

			if diff.seconds > 35:
				worker_status[k] = 0
				print '\t\t2.2'
				waiting_list.append(worker_dict[k])
				print '\t\t2.3'



# Will be handled by Adapter Pattern later on
def parse_html(html):

	PREFIX_URL = 'http://www.4-traders.com'
	data = html.split('Personal Network')[1].split('Linked companies')[1].split('</table')[0]

	rows = data.split('</tr>')[1:-1]


	ret_list = []

	for row in rows:
		name = row.split('<a')[1].split('>')[1].split('<')[0]
		url = PREFIX_URL+row.split('href="')[1].split('"')[0]

		name = name.strip()
		url = url.strip()

		ret_list.append((name,url))

	return ret_list

