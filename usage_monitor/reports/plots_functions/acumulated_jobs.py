# import os
# import psycopg2
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from dotenv import load_dotenv

# load_dotenv()

# conn = psycopg2.connect(
#     host=os.getenv('DB_HOST'),
#     user=os.getenv('DB_USER'),
#     password=os.getenv('DB_PASSWORD'),
#     database=os.getenv('DB_NAME')
# )

# cursor = conn.cursor()

# def AccumulatedJobs():
#     def fetch_data(query):
#         cursor.execute(query)
#         columns = [desc[0] for desc in cursor.description]
#         data = cursor.fetchall()
#         return pd.DataFrame(data, columns=columns)

#     ### query accumulated jobs ###
#     query_cumulative_jobs = """
#         WITH unique_jobs AS (
#             SELECT jobid, MIN(submit) AS submit
#             FROM job_log
#             GROUP BY jobid
#         )
#         SELECT DATE_TRUNC('month', submit) AS month,
#         COUNT(*) AS jobs_in_month,
#         SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', submit)) AS cumulative_jobs
#         FROM unique_jobs
#         GROUP BY month
#         ORDER BY month;
#     """

#     df_cumulative = fetch_data(query_cumulative_jobs)

#     df_cumulative["month"] = pd.to_datetime(df_cumulative["month"])
#     df_cumulative = df_cumulative[df_cumulative["month"] >= "2026-01-01"]

#     plt.figure(figsize=(10, 6))
#     sns.set_style("whitegrid")
#     plt.plot(df_cumulative["month"], df_cumulative["cumulative_jobs"], marker="o", color="green", linestyle="-")
#     plt.xlabel("Mês")
#     plt.ylabel("Número de Jobs")
#     plt.title("Crescimento Acumulado de Jobs")
#     plt.xticks(rotation=45)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig('jobs_acumulados.png')
#     plt.show()

#     cursor.close()
#     conn.close()

#     return "Jobs acumulados ploted successfully!!"

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

def AccumulatedJobs():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    ### query acumulada diária para 2026 ###
    query_cumulative_jobs = """
        WITH unique_jobs AS (
            SELECT jobid, MIN(submit) AS submit
            FROM job_log
            WHERE submit >= '2026-01-01 00:00:00' AND submit <= '2026-12-31 23:59:59'
            GROUP BY jobid
        ),
        jobs_per_day AS (
            SELECT 
                DATE_TRUNC('day', submit) AS day_ref,
                COUNT(*) AS jobs_in_day
            FROM unique_jobs
            GROUP BY day_ref
        )
        SELECT 
            day_ref,
            SUM(jobs_in_day) OVER (ORDER BY day_ref) AS cumulative_jobs
        FROM jobs_per_day
        ORDER BY day_ref;
    """

    df_cumulative = fetch_data(query_cumulative_jobs)

    # Convertendo a coluna retornada pelo banco
    df_cumulative["day_ref"] = pd.to_datetime(df_cumulative["day_ref"])

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Plotando usando a nova coluna 'day_ref'
    plt.plot(df_cumulative["day_ref"], df_cumulative["cumulative_jobs"], 
             marker="o", markersize=3, color="green", linestyle="-")
    
    plt.xlabel("Data")
    plt.ylabel("Número Total de Jobs")
    plt.title("Crescimento Diário Acumulado de Jobs (2026)")
    
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig('jobs_acumulados_diario.png')
    plt.show()

    cursor.close()
    conn.close()

    return "Jobs acumulados plotados com sucesso!"

if __name__ == "__main__":
    print(AccumulatedJobs())
