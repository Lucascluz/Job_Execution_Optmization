import csv
import random

def gerar_servers_csv(nome_arquivo='servers.csv', num_servidores=10):
    # Definir os cabeçalhos do CSV
    headers = ['id', 'num_nucleos', 'frequencia', 'capacidade_memoria', 'capacidade_largura_banda']

    # Gerar dados fictícios para os servidores
    servidores = [
        {
            'id': i + 1,
            'num_nucleos': random.choice([4, 8, 16, 32, 64]),  # Número aleatório de núcleos
            'frequencia': round(random.uniform(2.0, 4.0), 2),  # Frequência de CPU entre 2.0 e 4.0 GHz
            'capacidade_memoria': random.choice([4, 8, 16, 32, 64, 128]),  # Memória RAM em GB
            'capacidade_largura_banda': random.choice([100, 150, 200, 250, 300, 500, 1000])  # Largura de banda em Mbps
        } for i in range(num_servidores)
    ]

    # Escrever o arquivo CSV
    with open(nome_arquivo, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(servidores)

    print(f"{nome_arquivo} gerado com sucesso!")

# Chamar a função para gerar o arquivo
gerar_servers_csv()
