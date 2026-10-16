#import subprocess
import re
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta
import paramiko
import re

load_dotenv()

import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    
    def connect(self, host, user, password, database):
        try:
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=database,
            )

            print('Connected to database!!')

            return self.connection
        
        except Exception as e:
            print('Error connecting to database: ', e)
            return None


    def close(self):
        self.connection.close()
        print('Connection closed!!')

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

## get job logs info ###
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(manager_ip, username=user, password=password)
    print('connected to manager')

    current_date = datetime.now().date()
    zero_time = datetime.combine(current_date, datetime.min.time())

    # Execute the command
    stdin, stdout, stderr = ssh_client.exec_command(
        f'sacct --allusers --parsable --delimiter=\",\" --format State,JobID,Submit,Start,End,Elapsed,Partition,ReqCPUS,ReqMem,ReqTRES --starttime "2026-01-01" --endtime {current_date + timedelta(days=1)}'
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
