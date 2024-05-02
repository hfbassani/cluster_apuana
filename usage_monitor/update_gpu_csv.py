#import subprocess
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import paramiko
from database import DatabaseConnection


load_dotenv()

# connect to postgres database
db = DatabaseConnection()
db = db.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
)

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

manager_ip = ['slurm-manager1.cin.ufpe.br']

user = os.getenv('SSH_USER')  # get user from .env file
password = os.getenv('SSH_PASSWORD')  # get password from .env file

### connect to each node with ssh ###
for ip in nodes_ips:
    try:
        # ssh command to access the node and get data
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=user, password=password)

        print('connected to node ', ip)
        
        ### get the gpu data ###
        stdin, stdout, stderr = ssh_client.exec_command('nvidia-smi --format=csv,noheader --query-gpu=index,name,temperature.gpu,memory.used')

        # get time and hostname
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        hostname = ip.split('.')[0]
        
        # read the output and save on postgres database 
        for line in stdout:
            index, name, temperature, memory = line.strip().split(',')
            db.cursor().execute(
                "INSERT INTO gpu_log (name, temperature_gpu, memory_used, hostname, time) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, temperature, memory, hostname, time)
            )

            db.commit()
        
        print('gpu state saved!')
        
        ### get the disk data ###
        stdin, stdout, stderr = ssh_client.exec_command('df -H')
        stdout.channel.recv_exit_status()
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        next(stdout)

        for line in stdout:
            fields = line.strip().split()[:6]
            print(fields)

            if(len(fields) == 6):
                filesystem, size, used, avail, usepercent, mounted = fields
                usepercent = usepercent.replace('%', '')
                print(filesystem, size, used, avail, usepercent, mounted)

                db.cursor().execute(
                    "INSERT INTO filesystem_data (filesystem, size, used, avail, usepercent, mounted, time) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (filesystem, size, used, avail, usepercent, mounted, time)
                )

                db.commit()
            
            else:
                print('Error getting disk information')
            
            print('disk state saved!')


    except Exception as e:
        print(f'Erro ao conectar ao nó {ip}: {str(e)}')

### get the queue info ###
try:
    stdin, stdout, stderr = ssh_client.exec_command('squeue --Format=JobID,Name,UserName,State,TimeUsed,NodeList')
    stdout.channel.recv_exit_status()
    time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    next(stdout)

    for line in stdout:
        fields = line.strip().split()
        job_id, name, user, state, time_user, nodelist = fields
        job_id = int(job_id)
        
        db.cursor().execute(
            'INSERT INTO queue (jobid, name, "USER", state, time, nodelist, last_updated) '
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (job_id, name, user, state, time_user, nodelist, time)
        )

        db.commit()

    print('queue info saved!')

except Exception as e:
    print(f'Error getting queue information: {str(e)}')

ssh_client.close()

### get job logs info ###
try:
    current_date = datetime.now().date()
    zero_time = datetime.combine(current_date, datetime.min.time())
    zero_time = zero_time.strftime('%Y-%m-%dT%H:%M:%S')

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(manager_ip[0], username=user, password=password)
    print('connected to manager')

    stdin, stdout, stderr = ssh_client.exec_command('sacct --allusers --parsable --delimiter='','' --format State,JobID,Submit,Start,End,Elapsed,Partition,ReqCPUS,ReqMem,ReqTRES --starttime 2024-01-01T0:00:00')
    next(stdout)

    for line in stdout:
        fields = line.strip().split(',')

        for f in range(len(fields)):
            if fields[f] == None or fields[f] == 'None':
                fields[f] = zero_time

        state, job_id, submit, start, end, elapsed, partition, req_cpus, req_mem, req_gpu = fields[:10]
        state = state.split(" ")[0]
        job_id = job_id.split('_')[0]
        req_mem = req_mem.replace('M', '').replace('G', '')
        req_gpu = req_gpu.replace('billing=', '')

        db.cursor().execute(
            'INSERT INTO job_log (state, jobid, submit, start, "End", elapsed, partition, reqcpus, reqmem, reqgpu) '
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (state, job_id, submit, start, end, elapsed, partition, req_cpus, req_mem, req_gpu)
        )

        db.commit()
        print('job info saved!')

except Exception as e:
    print(f'Error connecting to manager: {str(e)}')

ssh_client.close()
db.close() # close the connection
