import sys
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('/path/to/keyfile/key.json', scope)
# authorize the clientsheet
client = gspread.authorize(creds)
# create the sheet instance
sheet = client.open('cluster_jobs_log')

# get job data
log_dict = dict([])
cols = []
firstLine = True
with os.popen('sacct --allusers --parsable --delimiter='','' --format State,JobID,Start,Elapsed,End,Partition --starttime 1970-01-01T0:00:00') as f:
	try:
		for line in f:
			new_line = line.replace('\n','')
			new_line = new_line.split(',')
			#print(new_line)
			#print(len(new_line))
			for col in range(len(new_line)-1):
				if firstLine: # initialize cols
					log_dict[new_line[col]] = []
					cols.append(new_line[col])
				else:
					log_dict[cols[col]].append(new_line[col])
			firstLine=False
	except:
		print("G")

# update the worksheet
log_df = pd.DataFrame.from_dict(log_dict)
worksheet = sheet.get_worksheet(0)
worksheet.update([log_df.columns.values.tolist()] + log_df.values.tolist())

print('log worksheet updated!')
