def imagem_para_matriz_cinza(img_pil):
    """
    Converte a imagem em matriz e faz o Item 4: RGB para Escala de Cinza MANUALMENTE.
    """
    largura, altura = img_pil.size
    
    # Pedimos ao Pillow APENAS os pixels coloridos brutos (lista de tuplas R,G,B)
    pixels_rgb = list(img_pil.convert('RGB').getdata())
    
    matriz_cinza = []
    
    for y in range(altura):
        linha = []
        for x in range(largura):
            # Encontra a posição exata do pixel na lista plana
            indice = (y * largura) + x
            r, g, b = pixels_rgb[indice]
            
            # Aplica a fórmula matemática de luminosidade:
            # Cinza = 0.299*R + 0.587*G + 0.114*B
            cinza = int((0.299 * r) + (0.587 * g) + (0.114 * b))
            linha.append(cinza)
            
        matriz_cinza.append(linha)
        
    return matriz_cinza

def calcular_histograma(matriz):
    """
    Calcula a frequência de cada tom de cinza (0-255).
    Retorna uma lista de 256 posições onde o índice é a intensidade 
    e o valor é a quantidade de pixels.
    """
    histograma = [0] * 256
    
    for linha in matriz:
        for pixel in linha:
            # Incrementa a contagem para o valor do pixel encontrado
            # Indice Inteiro
            histograma[int(pixel)] += 1
            
    return histograma

def threshold(matriz, limiar):
    """Limiarização simples."""
    altura = len(matriz)
    largura = len(matriz[0])
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    for y in range(altura):
        for x in range(largura):
            saida[y][x] = 255 if matriz[y][x] > limiar else 0  #Melhorar if para legibilidade
    return saida

def calcular_otsu(matriz):
    """Item 2: Algoritmo de Otsu para encontrar o limiar ótimo."""
    altura = len(matriz)
    largura = len(matriz[0])
    total_pixels = largura * altura
    
    # 1. Utiliza a função modular já existente para pegar o histograma
    histograma = calcular_histograma(matriz)
            
    sum_total = sum(i * histograma[i] for i in range(256))
    
    sum_back, w_back, w_fore = 0, 0, 0
    max_variancia = 0.0
    limiar_otimo = 0
    
    for t in range(256):
        w_back += histograma[t]
        if w_back == 0: continue
        
        w_fore = total_pixels - w_back
        if w_fore == 0: break
        
        sum_back += t * histograma[t]
        m_back = sum_back / w_back
        m_fore = (sum_total - sum_back) / w_fore
        
        variancia_entre = w_back * w_fore * (m_back - m_fore) ** 2
        
        if variancia_entre > max_variancia:
            max_variancia = variancia_entre
            limiar_otimo = t
            
    return limiar_otimo

def convolucao(matriz, kernel):
    """Função base para filtros de vizinhança."""
    altura = len(matriz)
    largura = len(matriz[0])
    n = len(kernel)
    offset = n // 2
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            soma = 0
            for ky in range(n):
                for kx in range(n):
                    pixel = matriz[y - offset + ky][x - offset + kx]
                    soma += pixel * kernel[ky][kx]
            saida[y][x] = soma
    return saida

def passa_alta_basico(matriz):
    """Filtro Passa-Alta usando o kernel Laplaciano."""
    kernel = [
        [-1, -1, -1],
        [-1,  8, -1],
        [-1, -1, -1]
    ]
    resultado = convolucao(matriz, kernel)
    
    # Normalizamos para garantir que a cor não passe de 255 nem fique negativa
    for y in range(len(resultado)):
        for x in range(len(resultado[0])):
            resultado[y][x] = max(0, min(255, int(resultado[y][x])))
    return resultado

def passa_alta_Alto_reforco(matriz, A=1.5):
   
    bordas = passa_alta_basico(matriz)
    altura = len(matriz)
    largura = len(matriz[0])
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    for y in range(altura):
        for x in range(largura):
            valor = (A * matriz[y][x]) + bordas[y][x]
            saida[y][x] = max(0, min(255, int(valor)))
    return saida

def passa_baixa_mediana(matriz, tamanho_mascara=3):
   
    altura = len(matriz)
    largura = len(matriz[0])
    offset = tamanho_mascara // 2
    
    # Cria a matriz de saída zerada
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Percorre a imagem ignorando as bordas para evitar erro de índice
    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            vizinhanca = []
            
            # Coleta todos os pixels dentro da janela (máscara)
            for ky in range(tamanho_mascara):
                for kx in range(tamanho_mascara):
                    pixel = matriz[y - offset + ky][x - offset + kx]
                    vizinhanca.append(pixel)
            
            # Ordena os valores da vizinhança
            vizinhanca.sort()
            
            # Pega o valor exato do meio da lista
            indice_meio = len(vizinhanca) // 2
            mediana = vizinhanca[indice_meio]
            
            # Atribui ao pixel central
            saida[y][x] = mediana
            
    return saida

def passa_baixa_media(matriz, tamanho_mascara=3):
   
    altura = len(matriz)
    largura = len(matriz[0])
    offset = tamanho_mascara // 2
    total_pixels_mascara = tamanho_mascara * tamanho_mascara
    
    # Cria a matriz de saída zerada
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Percorre a imagem ignorando as bordas para evitar erro de índice
    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            soma = 0
            
            # Coleta e soma todos os pixels dentro da janela (máscara)
            for ky in range(tamanho_mascara):
                for kx in range(tamanho_mascara):
                    soma += matriz[y - offset + ky][x - offset + kx]
            
            # Calcula a média simples
            media = soma // total_pixels_mascara
            
            # Atribui o valor médio ao pixel central
            saida[y][x] = media
            
    return saida

def somaIMG(matriz1, matriz2):
    """Soma duas imagens e normaliza o resultado para o intervalo 0-255."""
    altura = len(matriz1)
    largura = len(matriz1[0])
    
    # Cria a matriz auxiliar para guardar as somas
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Inicializa os valores de referência
    MaiorValor = -1
    MenorValor = 1000
    
    #Soma pixel a pixel e encontra o maior e menor valor
    for y in range(altura):
        for x in range(largura):
            soma = matriz1[y][x] + matriz2[y][x]
            matrizaux[y][x] = soma
            
            if soma > MaiorValor:
                MaiorValor = soma
            if soma < MenorValor:
                MenorValor = soma
                
    # Cria a matriz final que será salva no disco
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Verifica divisão por 0
    if MaiorValor == MenorValor:
        return matrizaux    
    
    #Normalização pixel a pixel
    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            
            
            #Usando 255.0 para o arredondamento não falhar 
            Pixelaux = (255.0 / (MaiorValor - MenorValor)) * (f - MenorValor)
            
            saida[y][x] = int(Pixelaux)
            
    return saida


def subIMG(matriz1, matriz2):
    """Subtrai duas imagens e normaliza o resultado para o intervalo 0-255."""
    altura = len(matriz1)
    largura = len(matriz1[0])
    
    # Cria a matriz auxiliar para guardar a subtração
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Inicializa os valores de referência
    MaiorValor = -1000
    MenorValor = 1000
    
    #subtrai pixel a pixel e encontra o maior e menor valor
    for y in range(altura):
        for x in range(largura):
            sub = matriz1[y][x] - matriz2[y][x]
            matrizaux[y][x] = sub
            
            if sub > MaiorValor:
                MaiorValor = sub
            if sub < MenorValor:
                MenorValor = sub
                
    # Cria a matriz final que será salva no disco
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Verifica divisão por 0
    if MaiorValor == MenorValor:
        return matrizaux    
    
    #Normalização pixel a pixel
    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            
            
            #Usando 255.0 para o arredondamento não falhar 
            Pixelaux = (255.0 / (MaiorValor - MenorValor)) * (f - MenorValor)
            
            saida[y][x] = int(Pixelaux)
            
    return saida

def multIMG(matriz1, matriz2):
    """Multiplica duas imagens e normaliza o resultado para o intervalo 0-255."""
    altura = len(matriz1)
    largura = len(matriz1[0])
    
    # Cria a matriz auxiliar para guardar a subtração
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Inicializa os valores de referência
    MaiorValor = -1
    MenorValor = 100000
    
    #multiplica pixel a pixel e encontra o maior e menor valor
    for y in range(altura):
        for x in range(largura):
            mul = matriz1[y][x] * matriz2[y][x]
            matrizaux[y][x] = mul
            
            if mul > MaiorValor:
                MaiorValor = mul
            if mul < MenorValor:
                MenorValor = mul
                
    # Cria a matriz final que será salva no disco
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Verifica divisão por 0
    if MaiorValor == MenorValor:
        return matrizaux    
    
    #Normalização pixel a pixel
    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            
            
            #Usando 255.0 para o arredondamento não falhar 
            Pixelaux = (255.0 / (MaiorValor - MenorValor)) * (f - MenorValor)
            
            saida[y][x] = int(Pixelaux)
            
    return saida

def divIMG(matriz1, matriz2):
    """Divide duas imagens e normaliza o resultado para o intervalo 0-255."""
    altura = len(matriz1)
    largura = len(matriz1[0])
    
    # Cria a matriz auxiliar para guardar a divisão
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Inicializa os valores de referência
    MaiorValor = -1
    MenorValor = 1000
    
    #Divide pixel a pixel e encontra o maior e menor valor
    for y in range(altura):
        for x in range(largura):
        #Verifica se é 0, se for é transformado em 255
            if matriz2[y][x] == 0:
                div = 255
            else:
                div = matriz1[y][x] / matriz2[y][x]
            matrizaux[y][x] = div
            
            if div > MaiorValor:
                MaiorValor = div
            if div < MenorValor:
                MenorValor = div
                
    # Cria a matriz final que será salva no disco
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Verifica divisão por 0 na fórmula
    if MaiorValor == MenorValor:
        return matrizaux    
    
    #Normalização pixel a pixel
    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            
            
            #Usando 255.0 para o arredondamento não falhar 
            Pixelaux = (255.0 / (MaiorValor - MenorValor)) * (f - MenorValor)
            
            saida[y][x] = int(Pixelaux)
            
    return saida

def negativo(matriz):
    "Faz o negativo da imagem usando a fórmula 255 - px"
    altura = len(matriz)
    largura = len(matriz[0])
    
    # Cria a matriz auxiliar para guardar a subtração
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(altura):
        for x in range(largura):
            f = matriz[y][x]
            matrizaux[y][x] =  255 - f
        
    return matrizaux

import math #Para o uso da função de log em py
def T_log(matriz):
    """Aplica a transformação logarítmica s = c * log(1 + r)"""
    altura = len(matriz)
    largura = len(matriz[0])
    
    # Cria a matriz de saída zerada
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    #Encontrar o maior valor da imagem para calcular a constante 'c'
    MaiorValor = -1
    for y in range(altura):
        for x in range(largura):
            if matriz[y][x] > MaiorValor:
                MaiorValor = matriz[y][x]
                
    print(MaiorValor)            
    # Se a imagem for totalmente preta (MaiorValor == 0), retorna ela mesma
    if MaiorValor == 0:
        return saida
        
    # Calcula a constante 'c' para garantir que o brilho máximo não passe de 255
    # Fórmula de c: 255 / log(1 + MaiorValor)
    c = 255.0 / math.log(1 + MaiorValor)
    
    #Aplica a fórmula do Gonzalez pixel a pixel
    for y in range(altura):
        for x in range(largura):
            r = matriz[y][x]
            
            # s = c * log(1 + r)
            s = c * math.log(1 + r)
            
            saida[y][x] = int(s)
            
    return saida


def equalizar_histograma(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    total_pixels = altura * largura # Isso é o 'n' da fórmula
    
    
    #Histograma da função calcular_histograma
    hist = calcular_histograma(matriz) 
    
    #Calcula as probabilidades e a soma acumulada 
    probabilidade_acumulada = 0.0
    mapa_de_cores = [0] * 256
    
    for k in range(256):
        probabilidade_atual = hist[k] / total_pixels # Isso é o (n_j / n)
        
        probabilidade_acumulada += probabilidade_atual #Acumulando a Probabilidade
        
        #Multiplica por 255 e arredonda para achar a nova cor
        nova_cor = int(probabilidade_acumulada * 255)
        mapa_de_cores[k] = nova_cor
        
    #Cria a matriz de saída varrendo a imagem original e trocando as cores
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    for y in range(altura):
        for x in range(largura):
            cor_antiga = matriz[y][x]
            saida[y][x] = mapa_de_cores[cor_antiga]
            
    return saida
