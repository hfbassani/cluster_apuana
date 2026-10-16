#import subprocess
from dotenv import load_dotenv
import os
from datetime import datetime
import paramiko
import socket
from pathlib import Path
import csv

load_dotenv()

user = os.getenv('SSH_USER')  # get user from .env file
password = os.getenv('SSH_PASSWORD')  # get password from .env file

### get node name
node = socket.gethostname()
ip = f"{node}.cin.ufpe.br"

### connect to ssh
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, username=user, password=password)
    
    print(f"connected to {ip}")

except Exception as e:
    print(f"error connecting to node {node}", e)

### connect to each node with ssh ###
try:
    ### get the gpu data ###
    stdin, stdout, stderr = ssh_client.exec_command('nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used,power.draw')
    csv_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/gpu_data.csv")

    # get time and hostname
    time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    hostname = ip.split('.')[0]

    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with csv_path.open("a", newline="") as f:
        writer = csv.writer(f)

        # read the output and save on csv database 
        for line in stdout:
            index, name, temperature, memory, power_watts = [x.strip() for x in line.split(",")]
            memory = memory.replace('MiB', '')
            memory = int(memory)
            
            power_watts = power_watts.replace('W', '').strip()
            power_watts = float(power_watts)

            writer.writerow([
                name,
                temperature,
                memory,
                hostname,
                time,
                power_watts,
            ])
        
        print('gpu state saved!')

    ### get the disk data ###
    stdin, stdout, stderr = ssh_client.exec_command('df -H')
    stdout.channel.recv_exit_status()
    time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    csv_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/disk_data.csv")
    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    next(stdout)

    with csv_path.open("a", newline="") as f:
        writer = csv.writer(f)

        for line in stdout:
            fields = line.strip().split()[:6]

            if(len(fields) == 6):
                filesystem, size, used, avail, usepercent, mounted = fields
                usepercent = usepercent.replace('%', '')

                writer.writerow([
                    filesystem,
                    size,
                    used,
                    avail,
                    usepercent,
                    mounted,
                    time
                ])
            
            else:
                print('Error getting disk information')
        
        print('disk state saved!')

    if (node == "cluster-node1"):
        ### get node state ### 
        stdin, stdout, stderr = ssh_client.exec_command('sinfo --Format=NodeHost,StateCompact')
        stdout.channel.recv_exit_status()
        next(stdout)
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        csv_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/node_state.csv")
        file_exists = csv_path.exists()
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with csv_path.open("a", newline="") as f:
            writer = csv.writer(f)

            for line in stdout:
                fields = line.strip().split()
                hostname, state = fields

                writer.writerow([
                    hostname,
                    state,
                    time
                ])
            
            print('node state saved!')
    else:
        print("Information collected")

except Exception as e:
    print(f'Error connecting to node {ip}: {str(e)}')

finally:
    ssh_client.close()
