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


def update_gpu_data(filepath, n_nodes):
    if hostname == 'cluster-node1':
        print('preparing to aggregate data...')
        time.sleep(10)
        
        # Criar um DataFrame vazio para armazenar os dados
        log_df = pd.DataFrame()

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
filepath = "/monitor/"
n_nodes = 10  # Por exemplo, o número total de nós no seu cluster

update_gpu_data(filepath, n_nodes)
