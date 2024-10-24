import csv
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Definição de variáveis globais para controle de parâmetros
TAMANHO_POPULACAO = 30      # Tamanho da população
NUM_GERACOES = 100          # Número de gerações
TAXA_MUTACAO = 0.1          # Probabilidade de mutação
TAMANHO_TORNEIO = 3         # Tamanho do torneio de seleção

# Carregar servidores dos arquivos CSV
def carregar_servidores(arquivo_servidores):
    servidores = []
    with open(arquivo_servidores, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row = {key.strip(): value.strip() for key, value in row.items()}
            if 'id' in row and 'num_nucleos' in row and 'frequencia' in row and 'capacidade_memoria' in row and 'capacidade_largura_banda' in row:
                servidores.append({
                    'id': int(row['id']),
                    'num_nucleos': int(row['num_nucleos']),
                    'frequencia': float(row['frequencia']),
                    'capacidade_memoria': float(row['capacidade_memoria']),
                    'capacidade_largura_banda': float(row['capacidade_largura_banda'])
                })
            else:
                print(f"Missing keys in row: {row} (servers.csv)")
    return servidores

# Carregar jobs dos arquivos CSV
def carregar_jobs(arquivo_jobs):
    jobs = []
    with open(arquivo_jobs, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:  # Corrected the unmatched parenthesis here
            row = {key.strip(): value.strip() for key, value in row.items()}
            if 'id' in row and 'tamanho' in row and 'memoria' in row and 'largura_banda' in row and 'suporta_multicore' in row:
                jobs.append({
                    'id': int(row['id']),
                    'tamanho': float(row['tamanho']),
                    'memoria': float(row['memoria']),
                    'largura_banda': float(row['largura_banda']),
                    'suporta_multicore': int(row['suporta_multicore'])
                })
            else:
                print(f"Missing keys in row: {row} (jobs.csv)")
    return jobs

#  Funções auxiliares para simulação de execução
def calcular_tempo_execucao(job, servidor, num_nucleos):
    """
    Calcula o tempo de execução de um job em um servidor específico.
    O tempo de execução depende do tamanho do job e da capacidade do servidor.
    """
    if job['suporta_multicore'] == 0:
        tempo_execucao = job['tamanho'] / servidor['frequencia']
    else:
        capacidade_computacional = servidor['frequencia'] * num_nucleos
        tempo_execucao = job['tamanho'] / capacidade_computacional
    return tempo_execucao

jobs = carregar_jobs('jobs.csv')
servidores = carregar_servidores('servers.csv')

# Funções auxiliares para simulação de execução
def calcular_tempo_maximo_possivel(jobs, servidores):
    """
    Calcula o tempo máximo possível de execução dos jobs em um único servidor.
    Isso simula a execução de todos os jobs no servidor mais lento de forma sequencial e sem multicore.
    """
    servidor_mais_lento = min(servidores, key=lambda s: s['frequencia'])
    tempo_maximo = sum([calcular_tempo_execucao(job, servidor_mais_lento, 1) for job in jobs])
    return tempo_maximo

# Simulação de execução de um indivíduo
def simula_exec(individuo, jobs, servidores):
    """
    Simula a execução de um indivíduo (solução) para o problema de escalonamento de jobs.
    Retorna o tempo total de execução, o tempo médio de espera dos jobs,
    os tempos de ociosidade de cada servidor, e o speed-up em relação ao tempo máximo possível.
    """
    # Inicializando estrutura para acompanhar o tempo de execução e ociosidade de cada servidor
    servidores_jobs = {servidor['id']: [] for servidor in servidores}
    ociosidade_servidores = {servidor['id']: 0 for servidor in servidores}
    
    # Inicializa as listas para armazenar tempos de espera e execução de cada job
    tempo_jobs = {job['id']: 0 for job in jobs}
    tempo_espera_jobs = {job['id']: 0 for job in jobs}

    # Atribui os jobs aos servidores de acordo com o indivíduo
    for servidor_id, job_id in individuo:
        servidores_jobs[servidor_id].append(job_id)

    # Inicializa variáveis de controle de tempo
    tempo_total = 0
    jobs_restantes = len(jobs)
    
    while jobs_restantes > 0:
        for servidor_id, jobs_atribuidos in servidores_jobs.items():
            if jobs_atribuidos:  # Verifica se o servidor tem jobs para executar
                servidor = next(s for s in servidores if s['id'] == servidor_id)
                job_id = jobs_atribuidos[0]  # Job que está sendo executado
                job = next(j for j in jobs if j['id'] == job_id)
                
                # Calcular o tempo de execução para o job no servidor
                tempo_execucao = calcular_tempo_execucao(job, servidor)
                
                # Se o tempo de execução ainda não foi completado, processar o job
                if tempo_jobs[job_id] < tempo_execucao:
                    tempo_jobs[job_id] += 1
                    tempo_total += 1  # Avançar o tempo total de execução do sistema

                    # Atualizar o tempo de espera dos outros jobs na fila desse servidor
                    for j in jobs_atribuidos[1:]:
                        tempo_espera_jobs[j] += 1
                else:
                    # Job foi concluído, remover da fila
                    jobs_atribuidos.pop(0)
                    jobs_restantes -= 1  # Um job a menos para ser executado
            else:
                # O servidor está ocioso, então incrementa o tempo de ociosidade
                ociosidade_servidores[servidor_id] += 1

    # Calcular o tempo total de execução e o tempo médio de espera dos jobs
    tempo_espera_medio = sum(tempo_espera_jobs.values()) / len(jobs)

    # Calcular o tempo máximo possível de execução (sequencial)
    tempo_maximo_possivel = calcular_tempo_maximo_possivel(jobs, servidores)

    return tempo_maximo_possivel, tempo_total, tempo_espera_medio, ociosidade_servidores    