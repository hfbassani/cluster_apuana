import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = conn.cursor()

def JobsExecutionsByMonth():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    ### query to get the number of jobs executed per month ###
    query_qtd_jobs = """
        SELECT DATE_TRUNC('month', submit) AS month,
        COUNT(*) AS total_jobs
        FROM job_log
        GROUP BY month
        ORDER BY month;
    """

    df_qtd_jobs = fetch_data(query_qtd_jobs)

    df_qtd_jobs["month"] = pd.to_datetime(df_qtd_jobs["month"])

    plt.figure(figsize=(10, 5))
    plt.plot(df_qtd_jobs["month"], df_qtd_jobs["total_jobs"], marker="o", color="green", linestyle="-")
    plt.xlabel("Mês")
    plt.ylabel("Quantidade de Jobs")
    plt.title("Quantidade de Jobs Executados por Mês")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.savefig('jobs_executions_by_month.png')
    plt.show()

    cursor.close()
    conn.close()

    return "Jobs Executions by Month plotted successfully!"

cursor = conn.cursor()

def JobsExecutionsByDay():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    ### Query para quantidade de jobs diários em 2026 ###
    query_qtd_jobs = """
        SELECT 
            DATE_TRUNC('day', submit) AS day_ref,
            COUNT(*) AS total_jobs
        FROM job_log
        WHERE submit >= '2026-01-01 00:00:00' AND submit <= '2026-12-31 23:59:59'
        GROUP BY day_ref
        ORDER BY day_ref;
    """

    df_qtd_jobs = fetch_data(query_qtd_jobs)

    # Convertendo a coluna retornada
    df_qtd_jobs["day_ref"] = pd.to_datetime(df_qtd_jobs["day_ref"])

    plt.figure(figsize=(10, 5))
    # Usando a nova coluna day_ref para o plot
    plt.plot(df_qtd_jobs["day_ref"], df_qtd_jobs["total_jobs"], 
             marker="o", markersize=3, color="green", linestyle="-", linewidth=1.5)
    
    plt.xlabel("Data")
    plt.ylabel("Quantidade de Jobs")
    plt.title("Quantidade Diária de Jobs Executados (2026)")
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Salvando antes de mostrar para evitar arquivos vazios
    plt.savefig('jobs_executions_by_day_2026.png')
    plt.show()

    cursor.close()
    conn.close()

    return "Jobs Executions by Day (2026) plotted successfully!"

if __name__ == "__main__":
    print(JobsExecutionsByDay())
