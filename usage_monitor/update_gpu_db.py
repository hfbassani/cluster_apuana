#import subprocess
import re
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta
import paramiko
from database import DatabaseConnection
import re

load_dotenv()

# connect to postgres database
db = DatabaseConnection()
db = db.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
)

### getting the nodes ips from the database ###
cur = db.cursor()
cur.execute("SELECT host_name FROM hosts")
nodes = cur.fetchall()
ips = [node[0] for node in nodes]
nodes_ips = ips[:10]
manager_ip = ips[-1]

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
            memory = memory.replace('MiB', '')
            memory = int(memory)
    
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

        ### get node state ### 
        stdin, stdout, stderr = ssh_client.exec_command('sinfo --Format=NodeHost,StateCompact')
        stdout.channel.recv_exit_status()
        next(stdout)
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        for line in stdout:
            fields = line.strip().split()
            hostname, state = fields

            db.cursor().execute(
                "INSERT INTO node_state (hostname, state, last_updated) "
                "VALUES (%s, %s, %s)",
                (hostname, state, time)
            )

            db.commit()
        
        print('node state saved!')

    except Exception as e:
        print(f'Error connecting to node {ip}: {str(e)}')
    
    finally:
        ssh_client.close()
    

def time_to_seconds(time_str):
    """
        this function converts a time string to seconds
        in case of time passes 24 hours
    """
    # elapse provides this format: 1-06:16:30
    days_match = re.match(r'(\d+)-(\d+):(\d+):(\d+)', time_str)
    if days_match:
        days = days_match.group(1)
        hours = days_match.group(2)
        minutes = days_match.group(3)
        seconds = days_match.group(4)

        format_time = f"{days} days {hours}:{minutes}:{seconds}"
    else:
        # No days, split the time string directly into hours, minutes, and seconds
        if len(time_str.split(':')) == 2:
            hours = 0
            minutes = time_str.split(':')[0]
            seconds = time_str.split(':')[1]
        else:
            hours = time_str.split(':')[0]
            minutes = time_str.split(':')[1]
            seconds = time_str.split(':')[2]

        format_time = f"{hours}:{minutes}:{seconds}"

    return format_time


def format_time(seconds):
    """
        this function converts seconds to hours
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


## get the queue info ###
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(manager_ip, username=user, password=password)
    print('connected to manager')

    stdin, stdout, stderr = ssh_client.exec_command('squeue --Format=JobID,Name,UserName,State,TimeUsed,NodeList')
    stdout.channel.recv_exit_status()
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    next(stdout)

    for line in stdout:
        fields = line.strip().split()
        
        if len(fields) < 6:
            continue
        
        print("fields", fields, time)
        job_id, name, user, state, time_user, nodelist = fields
        job_id = int(job_id)
        time_user = time_to_seconds(time_user)
        
        db.cursor().execute(
            'INSERT INTO queue (jobid, name, "USER", state, time, nodelist, last_updated) '
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (job_id, name, user, state, time_user, nodelist, time)
        )

        db.commit()

    print('queue info saved!')

except Exception as e:
    print(f'Error getting queue information: {str(e)}')


try:
    current_date = datetime.now().date()
    zero_time = datetime.combine(current_date, datetime.min.time())
    zero_time = zero_time.strftime('%Y-%m-%dT%H:%M:%S')

    ### get utilization info ###
    start_date = date(2024, 1, 1)
    curr_date = date.today()
    yesterday_date = curr_date - timedelta(days=1)
    curr_date = curr_date.strftime('%Y-%m-%dT%H:%M:%S')
    yesterday_date = yesterday_date.strftime('%Y-%m-%dT%H:%M:%S')

    this_date = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    stdin, stdout, stderr = ssh_client.exec_command(f'sreport cluster Utilization Start={yesterday_date} End={curr_date} -t Percent -P')
    output = stdout.readlines()

    if len(output) > 5:
        data_line = output[5].strip()
        data_parts = data_line.split('|')
        
        if len(data_parts) >= 5:
            ocupacao = float(data_parts[1].replace('%', ''))
            indisponibilidade = float(data_parts[2].replace('%', ''))
            ociosidade = float(data_parts[4].replace('%', ''))
            
            today = datetime.now().date()

            sql_query = 'INSERT INTO utilization (last_update, ocupation, idle, indisponibility) VALUES (%s, %s, %s, %s)'
            sql_data = (today, ocupacao, ociosidade, indisponibilidade)

            db.cursor().execute(sql_query, sql_data)

            db.commit()
            print('utilization info saved!')
        else:
            print('Error: Unexpected format in data line')
    else:
        print('Error: Not enough lines in output')

except Exception as e:
    print(f'Error connecting to manager: {str(e)}')

## get job logs info ###
try:
    current_date = datetime.now().date()
    zero_time = datetime.combine(current_date, datetime.min.time())
    today = datetime.now().date()
    yesterday_date = today - timedelta(days=1)
    yesterday_date = yesterday_date.strftime('%Y-%m-%dT%H:%M:%S')

    # Execute the command
    stdin, stdout, stderr = ssh_client.exec_command(
        f'sacct --allusers --parsable --delimiter=\",\" --format State,JobID,Submit,Start,End,Elapsed,Partition,ReqCPUS,ReqMem,ReqTRES --starttime {yesterday_date}'
    )

    # Capture the error output
    error_output = stderr.read().decode()
    if error_output:
        print(f"Error output: {error_output}")

    stdout.channel.recv_exit_status()
    next(stdout)

    for line in stdout:
        fields = line.strip().split(',')
        for f in range(len(fields)):
            if fields[f] in (None, 'None'):
                fields[f] = zero_time

        state, job_id, submit, start, end, elapsed, partition, req_cpus, req_mem, req_gpu = fields[:10]
        state = state.split(" ")[0]
        job_id = job_id.split('_')[0]
        req_mem = req_mem.replace('M', '').replace('G', '')
        req_gpu = req_gpu.replace('billing=', '')
        elapsed = time_to_seconds(elapsed)

        if end == 'Unknown':
            end = '1970-01-01T00:00:00'
        if start == 'Unknown':
            start = '1970-01-01T00:00:00'
        
        if not isinstance(job_id, int):
            job_id = int(job_id.split('.')[0])

        if req_cpus == '':
            req_cpus = 0
        if req_gpu == '':
            req_gpu = 0
        if req_mem == '':
            req_mem = 0
        
        if partition == '':
            partition = 'None'

        print(state, job_id, submit, start, end, elapsed, partition, req_cpus, req_mem, req_gpu)

        db.cursor().execute(
            'INSERT INTO job_log (state, jobid, submit, start, "End", elapsed, partition, reqcpus, reqmem, reqgpu) '
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (state, job_id, submit, start, end, elapsed, partition, req_cpus, req_mem, req_gpu)
        )

        db.commit()
        print('job info saved!')

except Exception as e:
    print(f'Error connecting to manager: {str(e)}')


ssh_client.close() # close the client
db.close() # close the connection
