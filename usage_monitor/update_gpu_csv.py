import subprocess
import csv
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# nodes ips list
nodes_ips = [
    'cluster-node1.cin.ufpe.br', 
    'cluster-node2.cin.ufpe.br', 
    'cluster-node3.cin.ufpe.br', 
    'cluster-node4.cin.ufpe.br', 
    'cluster-node5.cin.ufpe.br', 
    'cluster-node6.cin.ufpe.br', 
    'cluster-node7.cin.ufpe.br', 
    'cluster-node8.cin.ufpe.br', 
    'cluster-node9.cin.ufpe.br', 
    'cluster-node10.cin.ufpe.br'
]
user = os.getenv('SSH_USER')  # get user from .env file
password = os.getenv('SSH_PASSWORD')  # get password from .env file

print(user)
print(password)

# .csv file name
output_csv = './monitor/gpu_log.csv'

# open csv file to add new data
with open(output_csv, 'a', newline='') as csvfile:
    # define all headers
    fieldnames = ['index', 'name', 'temperature_gpu', 'memory_used', 'hostname', 'time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # write headers
    writer.writeheader()
    
    # connect to each node with ssh 
    for ip in nodes_ips:
        try:
            # ssh command to access the node and get data
            comando_ssh = f'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {user}@{ip} "nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used"'
            print(f'Conectando ao nó {ip}...')
            
            # execute ssh command
            output = subprocess.check_output(comando_ssh, shell=True, stderr=subprocess.STDOUT).decode()
            print('saida ', output)

            # get time and hostname
            time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            hostname = ip.split('.')[0]
            
            # read the output and write it to the csv file
            for line in output.strip().split('\n'):
                index, name, temperature, memory = line.strip().split(',')
                writer.writerow({'index': index, 'name': name, 'temperature_gpu': temperature, 'memory_used': memory, 'hostname': hostname, 'time': time})
        except Exception as e:
            print(f'Erro ao conectar ao nó {ip}: {str(e)}')