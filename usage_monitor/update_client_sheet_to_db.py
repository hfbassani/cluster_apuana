#import subprocess
from dotenv import load_dotenv
import os
from datetime import timedelta
import paramiko
from database import DatabaseConnection
from pathlib import Path
import pandas as pd

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
manager_ip = ips[-1]

user = os.getenv('SSH_USER')  # get user from .env file
password = os.getenv('SSH_PASSWORD')  # get password from .env file

### connect to manager via ssh
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(manager_ip, username=user, password=password)
    print('connected to manager')

except Exception as e:
    print("Could not connect to manager ", e)

### database inserts
try:
    print("disk data table")
    
    disk_data_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/disk_data.csv")
    df = pd.read_csv(disk_data_path)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    now = pd.Timestamp.now()
    df["time"] = df["time"].fillna(now)

    df = df[df["time"] >= now - timedelta(minutes=10)]
    
    df["usepercent"] = pd.to_numeric(df["usepercent"], errors="coerce")
    
    req_cols = ["filesystem", "size", "used", "avail", "usepercent", "mounted"]
    df = df.dropna(subset=req_cols)
    
    df["usepercent"] = df["usepercent"].astype(int)

    insert_sql = """
        INSERT INTO filesystem_data
        (filesystem, size, used, avail, usepercent, mounted, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for row in df.itertuples(index=False):
        cur.execute(
            insert_sql,
            (row.filesystem, row.size, row.used,
            row.avail, row.usepercent, row.mounted, row.time)
        )

    print("disk data table successful!")
    db.commit()

except Exception as e:
    print("Could not insert table into database: ", e)

try:
    print("gpu data table")
    
    gpu_data_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/gpu_data.csv")
    df = pd.read_csv(gpu_data_path, on_bad_lines='skip')

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    now = pd.Timestamp.now()
    df["time"] = df["time"].fillna(now)

    df = df[df["time"] >= now - timedelta(minutes=10)]

    req_cols = ["name" ,"temperature_gpu", "memory_used", "hostname", "time", "power_watts"]
    df = df.dropna(subset=req_cols)
    df["temperature_gpu"] = df["temperature_gpu"].astype(int)
    df["power_watts"] = df["power_watts"].astype(int)

    insert_sql = """
        INSERT INTO gpu_log 
        (name, temperature_gpu, memory_used, hostname, time, power_watts)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    for row in df.itertuples(index=False):
        cur.execute(
            insert_sql,
            (
                row.name, 
                row.temperature_gpu, 
                row.memory_used, 
                row.hostname, 
                row.time,
                row.power_watts,
            )
        )

    print("gpu data table successful!")
    print(f"power {row.power_watts}")
    db.commit()

except Exception as e:
    print("Could not insert table gpu_log into database: ", e)

try:
    print("node state data table")
    
    node_state_data_path = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/var/node_state.csv")
    df = pd.read_csv(node_state_data_path)

    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")

    now = pd.Timestamp.now()
    df["last_updated"] = df["last_updated"].fillna(now)

    df = df[df["last_updated"] >= now - timedelta(minutes=10)]

    req_cols = ["hostname", "state", "last_updated"]
    df = df.dropna(subset=req_cols)

    insert_sql = """
        INSERT INTO node_state 
        (hostname, state, last_updated)
        VALUES (%s, %s, %s)
    """

    for row in df.itertuples(index=False):
        cur.execute(
            insert_sql,
            (
                row.hostname, 
                row.state, 
                row.last_updated, 
            )
        )

    print("node state table successful!")

    db.commit()

except Exception as e:
    print("Could not insert table node_state into database: ", e)

# close connections
ssh_client.close()
db.close()
