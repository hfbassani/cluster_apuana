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

# def CpuGpuJobsByMonth():
#     def fetch_data(query):
#         cursor.execute(query)
#         columns = [desc[0] for desc in cursor.description]
#         data = cursor.fetchall()
#         return pd.DataFrame(data, columns=columns)

#     ### query to get the number of jobs executed per month with and without GPU ###
#     query = """
#         SELECT DATE_TRUNC('month', submit) AS month,
#         COUNT(*) FILTER (WHERE reqgpu = 0) AS cpu_only,
#         COUNT(*) FILTER (WHERE reqgpu > 0) AS cpu_gpu
#         FROM job_log
#         GROUP BY month
#         ORDER BY month;
#     """

#     df = fetch_data(query)

#     df["month"] = pd.to_datetime(df["month"])

#     plt.figure(figsize=(10, 6))
#     sns.set_style("whitegrid")
#     plt.plot(df["month"], df["cpu_only"], marker="o", color="red", label="Apenas CPU")
#     plt.plot(df["month"], df["cpu_gpu"], marker="o", color="green", label="CPU e GPU")
#     plt.xlabel("Mês")
#     plt.ylabel("Número de Jobs")
#     plt.title("Número de Jobs: Apenas CPU vs CPU e GPU ao Longo do Tempo")
#     plt.legend()
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.show()
#     plt.savefig('jobs_cpu_gpu_by_month.png')

#     cursor.close()
#     conn.close()

#     return "Jobs CPU e GPU por mês plotados com sucesso!"

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

def CpuGpuJobsByDay():
    def fetch_data(query):
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    ### Query para obter jobs diários (Apenas CPU vs GPU) em 2026 ###
    query = """
        SELECT 
            DATE_TRUNC('day', submit) AS day_ref,
            COUNT(*) FILTER (WHERE reqgpu = 0) AS cpu_only,
            COUNT(*) FILTER (WHERE reqgpu > 0) AS cpu_gpu
        FROM job_log
        WHERE submit >= '2026-01-01 00:00:00' AND submit <= '2026-12-31 23:59:59'
        GROUP BY day_ref
        ORDER BY day_ref;
    """

    df = fetch_data(query)

    # Convertendo para datetime
    df["day_ref"] = pd.to_datetime(df["day_ref"])

    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # Plotando os dados diários
    plt.plot(df["day_ref"], df["cpu_only"], marker="o", markersize=3, 
             linewidth=1, color="red", label="Apenas CPU", alpha=0.8)
    plt.plot(df["day_ref"], df["cpu_gpu"], marker="o", markersize=3, 
             linewidth=1, color="green", label="CPU e GPU", alpha=0.8)
    
    plt.xlabel("Data")
    plt.ylabel("Número de Jobs por Dia")
    plt.title("Volume Diário de Jobs: Apenas CPU vs CPU e GPU (2026)")
    plt.legend()
    
    # Melhorando a legibilidade do eixo X
    plt.xticks(rotation=45)
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('jobs_cpu_gpu_by_day_2026.png')
    plt.show()

    cursor.close()
    conn.close()

    return "Jobs CPU e GPU diários plotados com sucesso!"

if __name__ == "__main__":
    CpuGpuJobsByDay()
