# import pandas as pd
# import matplotlib.pyplot as plt

# def UserSubscByMonth():
#     # file_path = "/Users/paulaperazzo/Documents/apuana/cluster_apuana/usage_monitor/reports/user_files/user_forms_21-04-26.csv"
#     file_path = "usage_monitor/reports/user_files/user_forms_21-04-26.csv"
#     df = pd.read_csv(file_path)

#     df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce')

#     df_unique = df.drop_duplicates(subset=['Endereço de e-mail'])
#     df_unique['month'] = df_unique['Carimbo de data/hora'].dt.to_period('M').dt.to_timestamp()

#     monthly_counts = df_unique.groupby('month').size().reset_index(name='registrations')
#     print(monthly_counts)

#     plt.figure(figsize=(10,6))
#     plt.plot(monthly_counts['month'], monthly_counts['registrations'], marker='o', linestyle='-', color='green')
#     plt.xlabel('Mês')
#     plt.ylabel('Número Acumulado de Usuários')
#     plt.title('Crescimento Acumulado de Usuários Registrados no Cluster')
#     plt.xticks(rotation=45)
#     plt.grid(True)

#     for idx, row in monthly_counts.iterrows():
#         plt.text(row['month'], row['registrations'], str(row['registrations']), fontsize=9, ha='center', va='bottom')

#     plt.tight_layout()
#     plt.savefig('user_subs_by_month.png')
#     plt.show()

#     return "User Subscriptions by Month plotted successfully!"

import pandas as pd
import matplotlib.pyplot as plt

def UserSubscByMonth():
    # Caminho do arquivo conforme sua estrutura no MacBook
    file_path = "usage_monitor/reports/user_files/user_forms_21-04-26.csv"
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return "Erro: Arquivo CSV não encontrado."

    # Conversão da data do formulário
    df['Carimbo de data/hora'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce')

    # Remover duplicados para contar apenas novos usuários únicos
    df_unique = df.drop_duplicates(subset=['Endereço de e-mail']).copy()
    
    # Criar a coluna de mês
    df_unique['month'] = df_unique['Carimbo de data/hora'].dt.to_period('M').dt.to_timestamp()

    # Agrupar por mês
    monthly_counts = df_unique.groupby('month').size().reset_index(name='registrations')

    # FILTRO: Apenas o ano de 2026
    monthly_2026 = monthly_counts[monthly_counts['month'] >= "2026-01-01"].copy()

    if monthly_2026.empty:
        return "Aviso: Sem novas inscrições registradas em 2026."

    print(monthly_2026)

    plt.figure(figsize=(10,6))
    # Gráfico de barras costuma ser melhor para visualizar "inscrições por mês" do que linhas
    plt.bar(monthly_2026['month'], monthly_2026['registrations'], color='green', width=20, alpha=0.7)
    # Linha por cima para destacar a tendência
    plt.plot(monthly_2026['month'], monthly_2026['registrations'], marker='o', linestyle='-', color='darkgreen')
    
    plt.xlabel('Mês')
    plt.ylabel('Novas Inscrições')
    plt.title('Inscrições Mensais de Novos Usuários (2026)')
    
    # Formatação do eixo X
    plt.xticks(monthly_2026['month'], [d.strftime('%b/%Y') for d in monthly_2026['month']], rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)

    # Adicionando os rótulos de valor
    for idx, row in monthly_2026.iterrows():
        plt.text(row['month'], row['registrations'], str(int(row['registrations'])), 
                 fontsize=10, fontweight='bold', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('user_subs_by_month_2026.png')
    plt.show()

    return "User Subscriptions by Month 2026 plotted successfully!"

if __name__ == "__main__":
    print(UserSubscByMonth())
