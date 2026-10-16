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

# def AccumulatedJobsCPUvsGPU():
#     def fetch_data(query):
#         cursor.execute(query)
#         columns = [desc[0] for desc in cursor.description]
#         data = cursor.fetchall()
#         return pd.DataFrame(data, columns=columns)

#     ### query acum gpu and cpu jobs ###
#     query_acumulado = """
#         WITH unique_jobs AS (
#             SELECT
#                 jobid,
#                 MIN(submit) AS submit,
#                 CASE WHEN MAX(reqgpu) > 0 THEN 1 ELSE 0 END AS is_gpu
#             FROM job_log
#             GROUP BY jobid
#         ),
#         jobs_per_month AS (
#             SELECT
#                 DATE_TRUNC('month', submit) AS month,
#                 SUM(CASE WHEN is_gpu = 0 THEN 1 ELSE 0 END) AS cpu_count,
#                 SUM(CASE WHEN is_gpu = 1 THEN 1 ELSE 0 END) AS gpu_count
#             FROM unique_jobs
#             GROUP BY DATE_TRUNC('month', submit)
#         )
#         SELECT
#             month,
#             SUM(cpu_count) OVER (ORDER BY month) AS cpu_cumulative,
#             SUM(gpu_count) OVER (ORDER BY month) AS gpu_cumulative
#         FROM jobs_per_month
#         ORDER BY month;
#     """

#     df = fetch_data(query_acumulado)

#     df["month"] = pd.to_datetime(df["month"])

#     plt.figure(figsize=(10, 6))
#     sns.set_style("whitegrid")
#     plt.plot(df["month"], df["cpu_cumulative"], marker="o", color="red", label="Apenas CPU (acumulado)")
#     plt.plot(df["month"], df["gpu_cumulative"], marker="o", color="green", label="CPU e GPU (acumulado)")
#     plt.xlabel("Mês")
#     plt.ylabel("Número de Jobs Acumulados")
#     plt.title("Número de Jobs: Apenas CPU vs CPU e GPU (Valores Acumulados)")
#     plt.legend()
#     plt.xticks(rotation=45)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig('acumulated_jobs_cpu_gpu.png')
#     plt.show()

#     cursor.close()
#     conn.close()

#     return "ploted and saved"

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

def AccumulatedJobsCPUvsGPU():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    # Alterei o alias para "data_ref" para evitar confusão com palavras reservadas
    query_acumulado = """
       WITH unique_jobs AS (
        SELECT
            jobid,
            MIN(submit) AS submit,
            CASE WHEN MAX(reqgpu) > 0 THEN 1 ELSE 0 END AS is_gpu
        FROM job_log
        WHERE submit >= '2026-01-01 00:00:00' AND submit <= '2026-12-31 23:59:59'
        GROUP BY jobid
    ),
    jobs_per_day AS (
        SELECT
            DATE_TRUNC('day', submit) AS day,
            SUM(CASE WHEN is_gpu = 0 THEN 1 ELSE 0 END) AS cpu_count,
            SUM(CASE WHEN is_gpu = 1 THEN 1 ELSE 0 END) AS gpu_count
        FROM unique_jobs
        GROUP BY DATE_TRUNC('day', submit)
    )
    SELECT
        day AS data_ref, 
        SUM(cpu_count) OVER (ORDER BY day) AS cpu_cumulative,
        SUM(gpu_count) OVER (ORDER BY day) AS gpu_cumulative
    FROM jobs_per_day
    ORDER BY day;
    """

    df = fetch_data(query_acumulado)

    # Converte para datetime (removi o TO_CHAR da query para o pandas lidar com o objeto de data puro)
    df["data_ref"] = pd.to_datetime(df["data_ref"])

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Atualizado para usar df["data_ref"]
    plt.plot(df["data_ref"], df["cpu_cumulative"], marker="o", markersize=3, color="red", label="Apenas CPU (acumulado)")
    plt.plot(df["data_ref"], df["gpu_cumulative"], marker="o", markersize=3, color="green", label="CPU e GPU (acumulado)")
    
    plt.xlabel("Data")
    plt.ylabel("Número de Jobs Acumulados")
    plt.title("Número de Jobs em 2026: Apenas CPU vs CPU e GPU (Acumulado Diário)")
    plt.legend()
    
    # Melhora a formatação das datas no eixo X
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig('acumulated_jobs_cpu_gpu.png')
    plt.show()

    cursor.close()
    conn.close()

    return "ploted and saved"

# Se for rodar o script diretamente:
if __name__ == "__main__":
    AccumulatedJobsCPUvsGPU()