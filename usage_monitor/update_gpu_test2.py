import paramiko
import csv
from dotenv import load_dotenv
import os

load_dotenv()

# Lista de IPs dos nodos do cluster
nodos_ips = [
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
usuario = os.getenv('USUARIO')  # usuario
senha = os.getenv('SENHA')  # É recomendável utilizar chaves SSH para autenticação

# Nome do arquivo CSV de saída
output_csv = './monitor/test.csv'

# Abrir o arquivo CSV para escrita
with open(output_csv, 'w', newline='') as csvfile:
    # Definir o cabeçalho do arquivo CSV
    fieldnames = ['IP', 'Index', 'Nome', 'Temperatura_GPU', 'Memoria_Usada']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Escrever o cabeçalho no arquivo CSV
    writer.writeheader()
    
    # Conexão SSH e execução do comando nvidia-smi em cada nó
    for ip in nodos_ips:
        try:
            # Conectar ao nó via SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(ip, username=usuario, password=senha)
            
            # Executar o comando nvidia-smi
            stdin, stdout, stderr = ssh_client.exec_command('nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used')
            
            # Ler a saída do comando e escrever no arquivo CSV
            for line in stdout:
                index, nome, temperatura, memoria = line.strip().split(',')
                writer.writerow({'IP': ip, 'Index': index, 'Nome': nome, 'Temperatura_GPU': temperatura, 'Memoria_Usada': memoria})
            
            # Fechar a conexão SSH
            ssh_client.close()
        except Exception as e:
            print(f'Erro ao conectar ao nó {ip}: {str(e)}')
