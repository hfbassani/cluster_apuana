import sys
import os
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def time_to_seconds(time_str):
        # Check if the time string contains days
        if '-' in time_str:
                # Split the time string into days, hours, minutes, and seconds
                parts = time_str.split('-')
                days = int(parts[0])
                time_parts = parts[1].split(':')
        else:
                # No days, split the time string directly into hours, minutes, and seconds
                days = 0
                time_parts = time_str.split(':')

        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        # Create a timedelta object with the given time components
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        # Get the total number of seconds from the timedelta object
        total_seconds = float(delta.total_seconds())

        return total_seconds


# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('/path/to/key.json', scope)
# authorize the clientsheet
client = gspread.authorize(creds)
# create the sheet instance
sheet = client.open('cluster_jobs_log')

# get job data
log_dict = dict([])
cols = []
firstLine = True
# ReqTRES must always be the last column
with os.popen('sacct --allusers --parsable --delimiter='','' --format State,JobID,Submit,Start,End,Elapsed,Partition,ReqCPUS,ReqMem,ReqTRES --starttime 1970-01-01T0:00:00') as f:
	try:
		for line in f:
			new_line = line.replace('\n','')
			new_line = new_line.split(',')
			# remove the billing,mem,cpu,node values resultant from the ReqTRES flag
			new_line = [x for x in new_line if 'billing' not in x]
			new_line = [x for x in new_line if 'cpu' not in x]
			new_line = [x for x in new_line if 'mem' not in x]
			new_line = [x for x in new_line if 'node' not in x]
			#print(new_line)
			#print(len(new_line))

			# add items to the df
			#gpu_missing = True
			for col in range(len(new_line)-1):
				if firstLine: # initialize cols
					new_col = new_line[col]
					if new_col == 'ReqTRES': # add the gpu column associated with ReqTRES
						new_col = 'ReqGPU'
					cols.append(new_col)
					log_dict[new_col] = []
				else:
					this_val = new_line[col]
					if 'gpu' in this_val: # check gpu data availability and clean its value 
						this_val = this_val.replace('gres/gpu=','')
						#gpu_missing = False
						#print('gpu not missing')
					#print(cols[col])
					#print(this_val)
					if cols[col] == 'ReqMem':
						if 'M' in this_val: # convert from MB to GB
							this_val = str(float(this_val.replace('M',''))/1000)
						# remove the G
						this_val = this_val.replace('G','')
					if cols[col] == 'Elapsed': # convert Elapsed time to seconds
						this_val = time_to_seconds(this_val)
					log_dict[cols[col]].append(this_val)

			#check if gpu data is missing
			if len(log_dict['ReqGPU'])<len(log_dict['JobID']):
				log_dict['ReqGPU'].append('')

			firstLine=False

	except:
		print("G")

# prepare the dataset
log_df = pd.DataFrame.from_dict(log_dict)
# clean log_df(remove duplicates)
log_df['Partition'] = log_df['Partition'].replace('', pd.NA)
log_df = log_df.dropna(subset=['Partition'])
# Replace blank spaces with zero in the 'ReqGPU' column
log_df['ReqGPU'] = log_df['ReqGPU'].replace('', 0)
log_df['ReqGPU'] = log_df['ReqGPU'].astype(int)
# Rename ReqMem
log_df.rename(columns={'ReqMem': 'ReqMem (GB)'}, inplace=True)
# update the worksheet
worksheet = sheet.get_worksheet(0)
worksheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())

print('log worksheet updated!')
