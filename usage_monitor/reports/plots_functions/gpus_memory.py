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

# def GpusMemory():
#     def fetch_data(query):
#         cursor.execute(query)
#         cols = [desc[0] for desc in cursor.description]
#         rows = cursor.fetchall()
#         return pd.DataFrame(rows, columns=cols)

#     ### get gpu memory usage from the database ###
#     query_gpu_mem = """
#     WITH recent_gpus AS (
#         SELECT
#             CONCAT(hostname, ':', name) AS gpu_id,
#             memory_used
#         FROM gpu_log
#         WHERE time >= NOW() - INTERVAL '2 months'
#     )
#     SELECT
#         gpu_id,
#         AVG(memory_used::numeric) AS avg_mem_usage
#     FROM recent_gpus
#     GROUP BY gpu_id
#     ORDER BY avg_mem_usage DESC;
#     """

#     df = fetch_data(query_gpu_mem)

#     plt.figure(figsize=(12, 6))
#     sns.set_style("whitegrid")
#     sns.barplot(x="gpu_id", y="avg_mem_usage", data=df, palette="viridis")
#     plt.xlabel("GPU (hostname:name)")
#     plt.ylabel("Média de Memória Utilizada (MiB)")
#     plt.title("Uso Médio de Memória das GPUs (Últimos 2 meses)")
#     plt.xticks(rotation=45, ha="right")
#     plt.tight_layout()
#     plt.savefig('gpus_memory.png')
#     plt.show()

#     cursor.close()
#     conn.close()

#     return "Gpus Memory plotted successfully!"

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

def GpusMemory():
    def fetch_data(query):
        cursor.execute(query)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=cols)

    ### Query para uso médio de memória por GPU em 2026 ###
    query_gpu_mem = """
    WITH gpus_2026 AS (
        SELECT
            CONCAT(hostname, ':', name) AS gpu_id,
            memory_used
        FROM gpu_log
        -- Filtro fixo para o ano de 2026
        WHERE time >= '2026-01-01 00:00:00' AND time <= '2026-12-31 23:59:59'
    )
    SELECT
        gpu_id,
        AVG(memory_used::numeric)::numeric(10,2) AS avg_mem_usage
    FROM gpus_2026
    GROUP BY gpu_id
    ORDER BY avg_mem_usage DESC;
    """

    df = fetch_data(query_gpu_mem)

    # Verificação simples para evitar erro se o DF estiver vazio
    if df.empty:
        print("Nenhum dado encontrado para o período de 2026.")
        return "No data to plot"

    plt.figure(figsize=(12, 7))
    sns.set_style("whitegrid")
    
    # Criando o gráfico de barras
    # Nota: usei 'hue' para evitar o aviso de depreciação do seaborn
    plot = sns.barplot(x="gpu_id", y="avg_mem_usage", data=df, hue="gpu_id", palette="viridis", legend=False)
    
    plt.xlabel("GPU (hostname:name)")
    plt.ylabel("Média de Memória Utilizada (MiB)")
    plt.title("Uso Médio de Memória por Instância de GPU (2026)")
    
    # Ajuste fino para os nomes das GPUs no eixo X não encavalarem
    plt.xticks(rotation=45, ha="right", fontsize=9)
    
    plt.tight_layout()
    plt.savefig('gpus_memory_2026.png')
    plt.show()

    cursor.close()
    conn.close()

    return "Gpus Memory 2026 plotted successfully!"

if __name__ == "__main__":
    GpusMemory()
