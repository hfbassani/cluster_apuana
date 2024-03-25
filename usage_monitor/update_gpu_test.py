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
creds = ServiceAccountCredentials.from_json_keyfile_name('../user_management/key.json', scope)
# authorize the clientsheet
client = gspread.authorize(creds)
# create the sheet instance
sheet = client.open('cluster_jobs_log')

# get hostname
n_nodes = 10
hostname = os.popen('hostname').read()
hostname = hostname.replace('\n','').replace('$','')

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
			print(new_line)
			print(len(new_line))
			for col in range(len(new_line)):
				if firstLine: # initialize cols
					log_dict[new_line[col]] = []
					cols.append(new_line[col])
				else:
					log_dict[cols[col]].append(new_line[col])
			firstLine=False
	except:
		print("G")


def update_gpu_data(filepath, n_nodes):
    print('hostname:', hostname)

    print('preparing to aggregate data...')
    time.sleep(10)
    
    # Criar um DataFrame vazio para armazenar os dados
    log_df = pd.DataFrame.from_dict(log_dict)
    log_df.to_csv(filepath + "test.csv")

    # Agregar dados de cada nó
    for node in range(2, n_nodes+1):
        node_df = pd.read_csv(filepath + "gpu_log.csv")
        node_df = node_df.drop(node_df.columns[0], axis=1)
        log_df = pd.concat([log_df, node_df], axis=0, ignore_index=True)

    # Filtrar os dados para manter apenas os últimos sete meses
    log_df['time'] = pd.to_datetime(log_df['time'])
    end_date = log_df['time'].max()
    start_date = end_date - relativedelta(months=7)
    log_df = log_df[(log_df['time'] >= start_date) & (log_df['time'] <= end_date)]
    log_df['time'] = log_df['time'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Escrever os dados em um arquivo CSV local
    log_df.to_csv(filepath + "gpu_log.csv", index=False)

    print('Data aggregated and saved to gpu_log.csv file.')

# Exemplo de uso:
filepath = "/cluster_apuana/usage_monitor/monitor"
n_nodes = 10  # Por exemplo, o número total de nós no seu cluster

# update_gpu_data(filepath, n_nodes)
