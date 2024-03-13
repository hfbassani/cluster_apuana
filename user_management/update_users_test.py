import sys
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time

# The first step is to classify your uid as Admin. Thus, it is not necessary to use sudo to perform sacctmgr modifications
# example: sudo sacctmgr add user jcss4 account=test_acc partition=long,short,test AdminLevel=Admin

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)

# authorize the clientsheet
client = gspread.authorize(creds)

# create the sheet instance (obs.: follow the steps in  https://stackoverflow.com/questions/38949318/google-sheets-api-returns-the-caller-does-not-have-permission-when-using-serve/49965912#49965912)
sheet = client.open('planilha teste')

worksheet_users = sheet.get_worksheet(0)

# get current users in the user management spreadsheet
worksheet_users_vals = worksheet_users.get_all_values()
worksheet_users_vals = worksheet_users_vals[2:]
current_users = []

for row in worksheet_users_vals:
	user = row[1].split('@')
	current_users.append(user[0])

print('current_users', current_users)

# get current users in the slurm database
current_users_slurmdbd = []
with os.popen("sacctmgr -nrp show User") as f:
	try:
		print('f', f)
		for line in f:
			new_line = line.replace('\n','')
			new_line = new_line.split('|')
			current_users_slurmdbd.append(new_line[0])
	except:
		print("G")

print('current_users_slurmdbd', current_users_slurmdbd)
# verify if there are new users and add them to the slurm database
new_users = list(set(current_users)-set(current_users_slurmdbd))
if len(new_users) > 0:
	print("new_users = " + str(new_users))
	
	for new_user in new_users:
		print(new_user)

		### previous row to add users ###
		# find user row
		# row_idx = current_users.index(new_user)
		# row = worksheet_users_vals[row_idx]
		# add user to the database
		# print("sacctmgr -i add user " + row[1] + " account=" + row[4] + " partition=" + row[5])

		# os.system("sacctmgr -i add user " + new_user + " account=test_acc partition=long,short")
	# adjust associations
	# os.system("sacctmgr -i modify user set qos=singlegpu where partition=long")
	# os.system("sacctmgr -i modify user set qos=doublegpu where partition=short")
	# os.system("sacctmgr -i modify user set qos=normal where partition=test")

else:
	print('no new users to add')
