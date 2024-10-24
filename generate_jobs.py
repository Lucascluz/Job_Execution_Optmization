import csv
import random

def gerar_jobs_csv(nome_arquivo='jobs.csv', num_jobs=100):
    # Definir os cabeçalhos do CSV 
    headers = ['id', 'tamanho', 'memoria', 'largura_banda', 'suporta_multicore', 'prioridade']

    # Gerar dados fictícios para os jobs
    jobs = [
        {
            'id': i + 1,
            'tamanho': random.uniform(1.0, 1000.0),         # tempo de execuçào em um servidor de 2.0 GHz sem multicore
            'memoria': random.uniform(1.0, 4000.0),         # Memória requerida pelo job (em MB)
            'largura_banda': random.uniform(1.0, 150.0),    # Largura de banda exigida (em Mbps)
            'suporta_multicore': random.choice([0, 1]),     # Se suporta (1) ou não (0) multi-core
            'prioridade' : random.randrange(1,10)           # Define a prioridade do job
        } for i in range(num_jobs)
    ]

    # Escrever o arquivo CSV
    with open(nome_arquivo, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(jobs)

    print(f"{nome_arquivo} gerado com sucesso!")

# Chamar a função para gerar o arquivo
gerar_jobs_csv()
