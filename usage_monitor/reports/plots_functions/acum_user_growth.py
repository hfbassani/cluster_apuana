# import pandas as pd
# import matplotlib.pyplot as plt

# def CumulativeUserGrowth():
#     # file_path = "/Users/paulaperazzo/Documents/apuana/cluster_apuana/usage_monitor/reports/user_files/user_forms_21-04-26.csv"
#     file_path = "usage_monitor/reports/user_files/user_forms_21-04-26.csv"
#     df = pd.read_csv(file_path)

#     df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce')

#     df_unique = df.drop_duplicates(subset=['Endereço de e-mail'])
#     df_unique['month'] = df_unique['Carimbo de data/hora'].dt.to_period('M').dt.to_timestamp()

#     monthly_counts = df_unique.groupby('month').size().reset_index(name='registrations')
#     monthly_counts['cumulative_registrations'] = monthly_counts['registrations'].cumsum()
#     print(monthly_counts)

#     plt.figure(figsize=(10,6))
#     plt.plot(monthly_counts['month'], monthly_counts['cumulative_registrations'], marker='o', linestyle='-', color='green')
#     plt.xlabel('Mês')
#     plt.ylabel('Número Acumulado de Usuários')
#     plt.title('Crescimento Acumulado de Usuários Registrados no Cluster')
#     plt.xticks(rotation=45)
#     plt.grid(True)

#     for idx, row in monthly_counts.iterrows():
#         plt.text(row['month'], row['cumulative_registrations'], str(row['cumulative_registrations']), fontsize=9, ha='center', va='bottom')

#     plt.tight_layout()
#     plt.savefig('user_growth.png')
#     plt.show()

#     return "Cumulative User Growth plotted successfully!"

import pandas as pd
import matplotlib.pyplot as plt

def CumulativeUserGrowth():
    # Caminho do arquivo conforme sua estrutura atual
    file_path = "usage_monitor/reports/user_files/user_forms_21-04-26.csv"
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return "Erro: Arquivo CSV não encontrado."

    # Conversão da data do formulário
    df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce')

    # 1. Remover duplicados para contar apenas usuários únicos
    df_unique = df.drop_duplicates(subset=['Endereço de e-mail']).copy()

    # 2. Criar a coluna de mês
    df_unique['month'] = df_unique['Carimbo de data/hora'].dt.to_period('M').dt.to_timestamp()

    # 3. FILTRO: Garantir que estamos olhando apenas para 2026
    # Nota: Se você quiser o acumulado "desde sempre" mas exibindo apenas 2026, 
    # o cálculo do cumsum deve ser feito antes do filtro. 
    # Se quiser começar do zero em 2026, o filtro vem antes.
    
    # Aqui vamos calcular o acumulado de todo o período e filtrar a exibição para 2026:
    monthly_counts = df_unique.groupby('month').size().reset_index(name='registrations')
    monthly_counts = monthly_counts.sort_values('month')
    monthly_counts['cumulative_registrations'] = monthly_counts['registrations'].cumsum()

    # Agora filtramos para mostrar apenas os meses de 2026 no gráfico
    monthly_2026 = monthly_counts[monthly_counts['month'] >= "2026-01-01"].copy()

    if monthly_2026.empty:
        return "Aviso: Nenhum registro encontrado para o ano de 2026."

    print(monthly_2026)

    plt.figure(figsize=(10,6))
    plt.plot(monthly_2026['month'], monthly_2026['cumulative_registrations'], 
             marker='o', linestyle='-', color='green', linewidth=2)
    
    plt.xlabel('Mês')
    plt.ylabel('Número Acumulado de Usuários')
    plt.title('Crescimento Acumulado de Usuários Registrados (2026)')
    
    # Formatação do eixo X para mostrar os meses de 2026
    plt.xticks(monthly_2026['month'], [d.strftime('%b/%Y') for d in monthly_2026['month']], rotation=45)
    
    plt.grid(True, linestyle='--', alpha=0.7)

    # Adicionando os rótulos de valor acima dos pontos
    for idx, row in monthly_2026.iterrows():
        plt.text(row['month'], row['cumulative_registrations'], 
                 str(int(row['cumulative_registrations'])), 
                 fontsize=10, fontweight='bold', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('user_growth_2026.png')
    plt.show()

    return "Cumulative User Growth 2026 plotted successfully!"

if __name__ == "__main__":
    print(CumulativeUserGrowth())
