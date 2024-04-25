#import subprocess
import csv
from dotenv import load_dotenv
import os
from datetime import datetime
import paramiko
from database import DatabaseConnection


load_dotenv()

db = DatabaseConnection()
db = db.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

print("connectedjhsdjasd")

# db.close()

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

# .csv file name
output_csv = './monitor/gpu_log.csv'

# open csv file to add new data
# with open(output_csv, 'a', newline='') as csvfile:
# define all headers
fieldnames = ['index', 'name', 'temperature_gpu', 'memory_used', 'hostname', 'time']
# writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

# connect to each node with ssh 
for ip in nodes_ips:
    try:
        # ssh command to access the node and get data
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=user, password=password)

        print('connected to node ', ip)
        
        # Executar o comando nvidia-smi
        stdin, stdout, stderr = ssh_client.exec_command('nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used')

        # get time and hostname
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        hostname = ip.split('.')[0]
        
        # read the output and write it to the csv file
        for line in stdout:
            index, name, temperature, memory = line.strip().split(',')
            db.cursor().execute(
                "INSERT INTO gpu_log (index, name, temperature_gpu, memory_used, hostname, time) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (index, name, temperature, memory, hostname, time)
            )

            db.commit()
            print("foi")
            # writer.writerow({'index': index, 'name': name, 'temperature_gpu': temperature, 'memory_used': memory, 'hostname': hostname, 'time': time})
    except Exception as e:
        print(f'Erro ao conectar ao nó {ip}: {str(e)}')

db.close()

print('gpu state saved!')
