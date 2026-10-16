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

# def AvgReqCpuGpu():
#     def fetch_data(query):
#         cursor.execute(query)
#         columns = [desc[0] for desc in cursor.description]
#         data = cursor.fetchall()
#         return pd.DataFrame(data, columns=columns)

#     ### avg req cpu and gpu by month ###

#     query_avg_req = """
#         WITH job_steps AS (
#             SELECT
#                 jobid,
#                 submit,
#                 reqcpus,
#                 reqgpu
#             FROM job_log
#         ),
#         unique_jobs AS (
#             SELECT
#                 jobid,
#                 MIN(submit) AS submit,
#                 AVG(reqcpus) AS avg_reqcpus,
#                 AVG(reqgpu)  AS avg_reqgpu
#             FROM job_steps
#             GROUP BY jobid
#         ),
#         monthly_avg AS (
#             SELECT
#                 DATE_TRUNC('month', submit) AS month,
#                 AVG(avg_reqcpus)::numeric(10,2) AS avg_cpu,
#                 AVG(avg_reqgpu)::numeric(10,2) AS avg_gpu
#             FROM unique_jobs
#             GROUP BY DATE_TRUNC('month', submit)
#         )
#         SELECT month, avg_cpu, avg_gpu
#         FROM monthly_avg
#         ORDER BY month;
#     """

#     df = fetch_data(query_avg_req)
#     df["month"] = pd.to_datetime(df["month"])
#     df = df[df["month"] >= "2026-01-01"]

#     plt.figure(figsize=(10, 6))
#     sns.set_style("whitegrid")
#     plt.plot(df["month"], df["avg_cpu"], marker="o", color="red", label="Req CPU")
#     plt.plot(df["month"], df["avg_gpu"], marker="o", color="green", label="Req GPU")
#     plt.xlabel("Mês")
#     plt.ylabel("Requisições Média")
#     plt.title("Requisições Média GPU/CPU por Mês")
#     plt.legend()
#     plt.xticks(rotation=45)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig('avg_jobs_cpu_gpu_by_month.png')
#     plt.show()

#     cursor.close()
#     conn.close()

#     return "plot saved"

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

def AvgReqCpuGpu():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    ### Média diária de requisição de CPU e GPU para 2026 ###
    query_avg_req = """
        WITH unique_jobs AS (
            SELECT
                jobid,
                MIN(submit) AS submit,
                MAX(reqcpus) AS reqcpus,
                MAX(reqgpu) AS reqgpu
            FROM job_log
            WHERE submit >= '2026-01-01 00:00:00' AND submit <= '2026-12-31 23:59:59'
            GROUP BY jobid
        ),
        daily_avg AS (
            SELECT
                DATE_TRUNC('day', submit) AS day_ref,
                AVG(reqcpus)::numeric(10,2) AS avg_cpu,
                AVG(reqgpu)::numeric(10,2) AS avg_gpu
            FROM unique_jobs
            GROUP BY day_ref
        )
        SELECT day_ref, avg_cpu, avg_gpu
        FROM daily_avg
        ORDER BY day_ref;
    """

    df = fetch_data(query_avg_req)
    
    # Conversão de data consistente com os outros scripts
    df["day_ref"] = pd.to_datetime(df["day_ref"])

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Plotagem diária
    plt.plot(df["day_ref"], df["avg_cpu"], marker="o", markersize=3, color="red", label="Média Req CPU")
    plt.plot(df["day_ref"], df["avg_gpu"], marker="o", markersize=3, color="green", label="Média Req GPU")
    
    plt.xlabel("Data")
    plt.ylabel("Requisições Médias")
    plt.title("Média Diária de Recursos Requisitados (2026)")
    plt.legend()
    
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig('avg_jobs_cpu_gpu_by_day.png')
    plt.show()

    cursor.close()
    conn.close()

    return "plot diário salvo com sucesso"

if __name__ == "__main__":
    AvgReqCpuGpu()
