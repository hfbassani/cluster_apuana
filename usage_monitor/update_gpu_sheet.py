# WARNING:
#- Schedule the synchronized execution of this script through crontab on each host (cluster-node[1-10]).
#- Currently, cluster-node1 is the central node that aggregates information from each node.


import sys
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('/path/to/key.json', scope)
# authorize the clientsheet
client = gspread.authorize(creds)
# create the sheet instance
sheet = client.open('cluster_jobs_log')

# get hostname
n_nodes = 10
hostname = os.popen('hostname').read()
hostname = hostname.replace('\n','').replace('$','')


# get job data
log_dict = dict([])
cols = []
firstLine = True
now = time.strftime("%Y-%m-%dT%H:%M:%S")
with os.popen('nvidia-smi --format=csv --query-gpu=index,name,temperature.gpu,memory.used') as f:
	try:
		for line in f:
			new_line = line.replace('\n','')
			new_line = new_line.split(',')
			if firstLine:
				new_line.append('hostname')
				new_line.append('time')
			else:
				new_line.append(hostname)
				new_line.append(now)
			#print(new_line)
			#print(len(new_line))
			for col in range(len(new_line)):
				if firstLine: # initialize cols
					log_dict[new_line[col]] = []
					cols.append(new_line[col])
				else:
					log_dict[cols[col]].append(new_line[col])
			firstLine=False
	except:
		print("G")

filepath = '/home/CIN/user_id/usage_monitor/monitor/'
log_df = pd.DataFrame.from_dict(log_dict)
log_df.to_csv(filepath + hostname + ".csv")
print('gpu state saved!')

# aggregate information through cluster-node1
if hostname=='cluster-node1':
	# sleep for 10s (this gives enough time for all nodes to send information to the monitor directory)
	print('preparing to aggregate data...')
	time.sleep(10)
	# aggregate node data
	for node in range(2,n_nodes+1):
		node_df = pd.read_csv(filepath + "cluster-node" + str(node) + ".csv")
		node_df = node_df.drop(node_df.columns[0], axis=1)
		print(node_df)
		log_df = pd.concat([log_df, node_df], axis=0, ignore_index=True)
	# update the worksheet
	#print(log_df)
	worksheet = sheet.get_worksheet(1)
	# append new data to the end of the file
	df = pd.DataFrame(worksheet.get_all_records())
	worksheet.update([df.columns.values.tolist()] + df.values.tolist() + log_df.values.tolist())
	#worksheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())
	print('log worksheet updated!')
