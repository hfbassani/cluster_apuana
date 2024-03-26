import subprocess
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
            # Construir o comando SSH com o comando nvidia-smi
            comando_ssh = f'sshpass -p "{senha}" ssh -o StrictHostKeyChecking=no {usuario}@{ip} "nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used"'
            
            # Executar o comando SSH e capturar a saída
            saida = subprocess.check_output(comando_ssh, shell=True, stderr=subprocess.STDOUT).decode()
            
            # Ler a saída do comando e escrever no arquivo CSV
            for line in saida.strip().split('\n'):
                index, nome, temperatura, memoria = line.strip().split(',')
                writer.writerow({'IP': ip, 'Index': index, 'Nome': nome, 'Temperatura_GPU': temperatura, 'Memoria_Usada': memoria})
        except Exception as e:
            print(f'Erro ao conectar ao nó {ip}: {str(e)}')
