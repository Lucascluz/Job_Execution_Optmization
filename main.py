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
    Isso simula a execução de todos os jobs no servidor mais lento (ou mais rápido, dependendo da formulação).
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
                tempo_execucao = calcular_tempo_execucao(job, servidor, servidor['num_nucleos'])
                
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

# Função de fitness
def fitness(população, jobs, servidores):
    """
    Calcula o fitness de um indivíduo baseado no tempo total de execução e ociosidade.
    O fitness varia de 0 (pior caso) a 1 (melhor caso).
    """
    fitness_populacao = []
    
    # Calcula o tempo ideal baseado no servidor mais rápido para cada job
    servidor_mais_rapido = max(servidores, key=lambda s: s['frequencia'] * s['num_nucleos'])
    total_tempo_ideal = sum([calcular_tempo_execucao(job, servidor_mais_rapido, servidor_mais_rapido['num_nucleos']) for job in jobs])
    tempo_ideal = total_tempo_ideal / len(servidores)  # Tempo ideal com distribuição perfeita

    for individuo in população:
        # Obter os tempos simulados de execução para o indivíduo
        tempo_maximo_possivel, tempo_total, _, _ = simula_exec(individuo, jobs, servidores)
        
        # Penaliza soluções que ultrapassam o tempo máximo
        if tempo_total > tempo_maximo_possivel:
            fitness_value = 0  # Pior caso, tempo acima do possível
        else:
            # Ajusta o fitness considerando o tempo total e a ociosidade
            fitness_value = (tempo_maximo_possivel - tempo_total) / (tempo_maximo_possivel - tempo_ideal)
            fitness_value = min(max(fitness_value, 0), 1)  # Garante que o fitness esteja entre 0 e 1

        fitness_populacao.append(fitness_value)
    
    return fitness_populacao

    
# Inicialização de um indivíduo aleatório
def inicializa_individuo_aleatorio(jobs, servidores):
    """
    Inicializa um indivíduo aleatoriamente.
    Um indivíduo é uma lista de tuplas (servidor_id, job_id).
    """
    individuo = []
    for job in jobs:
        servidor_id = random.choice(servidores)['id']
        individuo.append((servidor_id, job['id']))
    return individuo

# Inicialização da população
def inicializa_populacao(tamanho_populacao, jobs, servidores):
    """
    Inicializa uma população de indivíduos aleatoriamente.
    Cada indivíduo é uma lista de tuplas (servidor_id, job_id).
    """
    populacao = [inicializa_individuo_aleatorio(jobs, servidores) for _ in range(tamanho_populacao)]
    return populacao

# Seleção por torneio
def selecao_torneio(populacao, fitness, tamanho_torneio):
    """
    Seleciona um indivíduo da população utilizando o método do torneio.
    """
    tamanho_torneio = min(tamanho_torneio, len(populacao))
    
    torneio = random.sample(list(zip(populacao, fitness)), tamanho_torneio)
    vencedor = max(torneio, key=lambda x: x[1])[0]  # Seleciona o indivíduo com maior fitness
    return vencedor

# Crossover (Recombinação)
def crossover(pai1, pai2):
    """
    Realiza o crossover entre dois indivíduos.
    Gera dois novos indivíduos (filhos).
    """
    ponto_corte = random.randint(1, len(pai1) - 1)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2

# Mutação
def mutacao(individuo, taxa_mutacao, servidores):
    """
    Aplica mutação em um indivíduo com uma probabilidade definida.
    A mutação consiste em trocar o servidor de um job aleatoriamente.
    """
    for i in range(len(individuo)):
        if random.random() < taxa_mutacao:
            novo_servidor_id = random.choice(servidores)['id']
            individuo[i] = (novo_servidor_id, individuo[i][1])  # Troca o servidor para esse job
    return individuo

# Substituição (geração da nova população)
def gerar_nova_populacao(populacao, fitness_populacao, jobs, servidores, tamanho_torneio, taxa_mutacao):
    """
    Gera uma nova população utilizando seleção, crossover e mutação.
    """
    nova_populacao = []
    while len(nova_populacao) < len(populacao):
        # Seleção dos pais
        pai1 = selecao_torneio(populacao, fitness_populacao, tamanho_torneio)
        pai2 = selecao_torneio(populacao, fitness_populacao, tamanho_torneio)
        
        # Crossover
        filho1, filho2 = crossover(pai1, pai2)
        
        # Mutação
        filho1 = mutacao(filho1, TAXA_MUTACAO, servidores)
        filho2 = mutacao(filho2, TAXA_MUTACAO, servidores)
        
        # Adiciona os filhos à nova população
        nova_populacao.append(filho1)
        nova_populacao.append(filho2)
    
    # Certificar que o tamanho da população não excede o limite
    return nova_populacao[:len(populacao)]

# Critério de Parada - Treinamento do Algoritmo Genético
def algoritmo_genetico(jobs, servidores):
    """
    Executa o algoritmo genético para otimização do escalonamento de jobs.
    """
    # Inicializa a população
    populacao = inicializa_populacao(TAMANHO_POPULACAO, jobs, servidores)
    
    for geracao in range(NUM_GERACOES):
        # Avaliar a população
        fitness_populacao = fitness(populacao, jobs, servidores)
        
        if not fitness_populacao:
            print("Erro: A população de fitness está vazia.")
            break
        
        # Encontrar o melhor indivíduo da geração atual
        melhor_individuo = populacao[fitness_populacao.index(max(fitness_populacao))]
        tempo_maximo_possivel, tempo_total, tempo_espera_medio, ociosidade_servidores = simula_exec(melhor_individuo, jobs, servidores)
        
        print(f"Geração {geracao}: Fitness = {max(fitness_populacao)}, Tempo Maximo = {tempo_maximo_possivel}, Tempo Total = {tempo_total} ms, Tempo Médio de Espera = {tempo_espera_medio} ms, Ociosidade = {ociosidade_servidores}")
        
        # Gerar a nova população
        populacao = gerar_nova_populacao(populacao, fitness_populacao, jobs, servidores, TAMANHO_TORNEIO, TAXA_MUTACAO)

    return melhor_individuo

# Execução do algoritmo genético
melhor_individuo_final = algoritmo_genetico(jobs, servidores)
_, tempo_total_final, tempo_espera_medio_final, ociosidade_servidores_final = simula_exec(melhor_individuo_final, jobs, servidores)

print(f"Melhor solução encontrada: {melhor_individuo_final}")
print(f"Tempo total de execução: {tempo_total_final} ms")
print(f"Tempo médio de espera: {tempo_espera_medio_final} ms")
print(f"Tempos de ociosidade dos servidores: {ociosidade_servidores_final}")