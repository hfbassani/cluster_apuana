#!/usr/bin/env python3

import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from database import DatabaseConnection
import time

load_dotenv()

### database connection ###

db = DatabaseConnection()
db = db.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
)

GSHEET_KEY_FILE = Path("/home/CIN/mpps/paulaperazzo/cluster_apuana/usage_monitor/gen-lang-client-0851945156-9931994421e6.json")
GSHEET_ID = os.getenv("GSHEET_ID")
TAB_NAME = "utilization"

### utilization table ###

curr_time_delayed = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3600))

query = f"""
    SELECT last_update, ocupation, idle, indisponibility, id_val
    FROM utilization
    WHERE last_update >= '{curr_time_delayed}'
    ORDER  BY last_update DESC;
"""

# query = f"""
#     SELECT last_update, ocupation, idle, indisponibility, id_val
#     FROM utilization
#     WHERE last_update >= '2025-05-01 00:00:01'
#     ORDER  BY last_update DESC;
# """

df = pd.read_sql_query(query, db)
# df["last_update"] = df["last_update"].dt.strftime("%Y-%m-%d %H:%M:%S")

#### connect to google sheets ####
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    GSHEET_KEY_FILE,
    scopes=SCOPES,
)
gc = gspread.authorize(creds)

sh = gc.open_by_key(GSHEET_ID) if "/" not in GSHEET_ID else gc.open_by_url(GSHEET_ID)

try:
    ws = sh.worksheet(TAB_NAME)
except gspread.WorksheetNotFound:
    ws = sh.add_worksheet(title=TAB_NAME, rows=len(df) + 1, cols=len(df.columns))

### send data to sheet ###
set_with_dataframe(
    ws,
    df,
    include_index=False,
    resize=False,
)

print(f"✓ {len(df)} lines sent to {sh.title}/{TAB_NAME}")

### close connection ###
db.close()
