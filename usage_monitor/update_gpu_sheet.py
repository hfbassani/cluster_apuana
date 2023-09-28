# WARNING:
#- Schedule the synchronized execution of this script through crontab on each host (cluster-node[1-10]).
#- Currently, cluster-node1 is the central node that aggregates information from each node.

import sys
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/CIN/jcss4/log_jobs/cluster-jobcompletion-log-724376385825.json', scope)
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

filepath = '/home/CIN/jcss4/usage_monitor/monitor/'
log_df = pd.DataFrame.from_dict(log_dict)
log_df.to_csv(filepath + hostname + ".csv")
print('gpu state saved!')

# aggregate information through cluster-node1
if hostname=='cluster-node1':
	# update node_state sheet
	worksheet = sheet.get_worksheet(3)
	state_info_raw = os.popen('sinfo --Format=NodeHost,StateCompact').read()
	# parser
	state_info = state_info_raw.split('\n')
	state_dict = dict([]) 
	for line in state_info:
		line_final = line.split(' ')
		line_final = list(filter(None, line_final)) # remove blank spaces
		if len(state_dict.keys()) == 0:
			cols = line_final
			state_dict[cols[0]] = []
			state_dict[cols[1]] = []
			state_dict['last_updated'] = []
		elif len(line_final) > 0: # if there are elements in this line...
			state_dict[cols[0]].append(line_final[0])
			state_dict[cols[1]].append(line_final[1])
			state_dict['last_updated'].append(now) 
	state_df = pd.DataFrame.from_dict(state_dict)
	# push updates
	worksheet.clear()
	worksheet.update([state_df.columns.values.tolist()] + state_df.values.tolist())
	print('state worksheet updated!')

	# update queue sheet
	worksheet = sheet.get_worksheet(4)
	squeue_raw = os.popen('squeue --Format=JobID,Name,UserName,State,TimeUsed,NodeList').read()
	# parser
	squeue = squeue_raw.split('\n')
	squeue_dict = dict([])
	for line in squeue:
		line_final = line.split(' ')
		line_final = list(filter(None, line_final)) # remove blank spaces
		if len(squeue_dict.keys()) == 0:
			cols = line_final
			for col_idx in range(len(cols)):
				squeue_dict[cols[col_idx]] = []
			squeue_dict['last_updated'] = []
		elif len(line_final) > 0: # if there are elements in this line...
			for col_idx in range(len(cols)):
				squeue_dict[cols[col_idx]].append(line_final[col_idx])
			squeue_dict['last_updated'].append(now)
	state_df = pd.DataFrame.from_dict(squeue_dict)
	# push updates
	worksheet.clear()
	worksheet.update([state_df.columns.values.tolist()] + state_df.values.tolist())
	print('queue worksheet updated!')

	# update the disk usage sheet
	worksheet = sheet.get_worksheet(2)
	# get disk usage data
	output_disk = os.popen('df -H').read()
	# Split the output into lines
	lines = output_disk.split('\n')
	# Get the header line
	header = lines[0].split()
	header.pop()
	header.append('time') # append current time col
	# Find the index of the Truenas03 machine
	index = next(i for i, line in enumerate(lines[1:]) if line.startswith('truenas'))
	# Get the values for the Truenas03  line
	values = lines[index + 1].split()
	values.append(now) # add current time
	# Create a DataFrame with the extracted columns
	disk_df = pd.DataFrame([values], columns=header)
	# append new data to the end of the file
	df = pd.DataFrame(worksheet.get_all_records())
	#print(df)
	# maintain data from the last seven months 
	df['time'] = pd.to_datetime(df['time']) # Convert the 'time' column to datetime format
	end_date = df['time'].max()  # Get the maximum date in the 'time' column
	start_date = end_date - relativedelta(months=7)  # Calculate the start date by subtracting 7 months
	df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]  # apply the 'last week only' filter
	df['time'] = df['time'].dt.strftime('%Y-%m-%dT%H:%M:%S') # convert the column back to the string format
	# Remove '%' character and transform 'Use%' values to float
	#df['Use%'] = df['Use%'].str.rstrip('%').astype(float)
	disk_df['Use%'] = disk_df['Use%'].str.rstrip('%').astype(float)
	# push updates
	worksheet.update([df.columns.values.tolist()] + df.values.tolist() + disk_df.values.tolist())
	#print(df)
	#print(disk_df)
	#worksheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())
	print('disk usage worksheet updated!')



	# update gpu sheet
	# sleep for 10s (this gives enough time for all nodes to send information to the monitor directory)
	print('preparing to aggregate data...')
	time.sleep(10)
	# aggregate node data
	for node in range(2,n_nodes+1):
		node_df = pd.read_csv(filepath + "cluster-node" + str(node) + ".csv")
		node_df = node_df.drop(node_df.columns[0], axis=1)
		#print(node_df)
		log_df = pd.concat([log_df, node_df], axis=0, ignore_index=True)
	# update the worksheet
	#print(log_df)
	worksheet = sheet.get_worksheet(1)
	# append new data to the end of the file
	df = pd.DataFrame(worksheet.get_all_records())
	# maintain data from the last seven months 
	df['time'] = pd.to_datetime(df['time']) # Convert the 'time' column to datetime format
	end_date = df['time'].max()  # Get the maximum date in the 'time' column
	start_date = end_date - relativedelta(months=7)  # Calculate the start date by subtracting 7 months
	df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]  # apply the 'last week only' filter
	df['time'] = df['time'].dt.strftime('%Y-%m-%dT%H:%M:%S') # convert the column back to the string format
	# push updates
	worksheet.update([df.columns.values.tolist()] + df.values.tolist() + log_df.values.tolist())
	#worksheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())
	print('gpu worksheet updated!')
