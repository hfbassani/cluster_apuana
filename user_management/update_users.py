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
sheet = client.open('Registro de Usuários Cluster Apuana  (respostas)')

worksheet_users = sheet.get_worksheet(0)

# get current users in the user management spreadsheet
worksheet_users_vals = worksheet_users.get_all_values()
df_worksheet = pd.DataFrame(worksheet_users_vals[1:], columns=worksheet_users_vals[0])
df_worksheet = df_worksheet.rename(columns={"Nome Orientador ou Pesquisador Responsável.\nSe aluno de graduação utilizando para projeto da disciplina, indique o nome do professor da disciplina.": "orientador"})
df_users = df_worksheet[['Email', "orientador"]]
df_users["Email"] = df_users["Email"].str.split('@').str[0]
df_users = df_users[~df_users["orientador"].isnull()]
df_users = df_users[~df_users["Email"].isnull()]
# remove any row that the column "orientador" ends with xxx
df_users = df_users[~df_users["orientador"].str.endswith('xxx')]
current_users = df_users["Email"].tolist()
advisors = df_users["orientador"].unique().tolist()
print('current_users', current_users)
print('Length:', len(current_users))
print('advisors', advisors)

# get current users in the slurm database
current_users_slurmdbd = []
with os.popen("sacctmgr -nrp show User") as f:
	try:
		for line in f:
			new_line = line.replace('\n','')
			new_line = new_line.split('|')
			current_users_slurmdbd.append(new_line[0])
	except Exception as e:
		print("Error: ", e)

# verify if there are new users and add them to the slurm database
new_users = list(set(current_users)-set(current_users_slurmdbd))
if len(new_users) > 0:
	print("new_users = " + str(new_users))
	
	for new_user in new_users:
		user_advisor = df_users[df_users["Email"] == new_user]["orientador"].values[0]
		print(f"Adding user {new_user} for account: {user_advisor}_group")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=debug,qos=complex")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=install,qos=simple")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=short-simple,qos=simple")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=short-complex,qos=complex")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=long-simple,qos=simple")
		os.system(f"sudo -A sacctmgr -i add user {new_user} account={user_advisor}_group partition=long-complex,qos=complex")

else:
	print('no new users to add')
