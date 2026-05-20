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
    """
    Filtro Passa-Alta Alto Reforço (High-Boost).
    Implementado estritamente de acordo com a formulação teórica clássica:
    Saída = (A - 1) * Original + Passa-Alta
    """
    # Obtém as bordas através do passa-alta básico
    bordas = passa_alta_basico(matriz)
    altura = len(matriz)
    largura = len(matriz[0])
    
    # Cria a matriz de saída zerada
    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Aplica a fórmula teórica pixel a pixel
    for y in range(altura):
        for x in range(largura):
            # Fórmula exata da literatura: (A - 1) * Original + Passa-Alta
            valor = ((A - 1.0) * matriz[y][x]) + bordas[y][x]
            
            # Limita (clipping) para garantir que caiba em 8 bits (0 a 255)
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

def passa_baixa_gaussiano(matriz, tamanho_mascara=3):
    if tamanho_mascara == 3:
        kernel_raw = [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ]
        divisor = 16
    else:  # 5x5
        kernel_raw = [
            [1,  4,  6,  4, 1],
            [4, 16, 24, 16, 4],
            [6, 24, 36, 24, 6],
            [4, 16, 24, 16, 4],
            [1,  4,  6,  4, 1]
        ]
        divisor = 256

    n = tamanho_mascara
    kernel = [[kernel_raw[ky][kx] / divisor for kx in range(n)] for ky in range(n)]

    resultado = convolucao(matriz, kernel)

    for y in range(len(resultado)):
        for x in range(len(resultado[0])):
            resultado[y][x] = max(0, min(255, int(resultado[y][x])))

    return resultado

def passa_baixa_min(matriz, tamanho_mascara=3):
    altura = len(matriz)
    largura = len(matriz[0])
    offset = tamanho_mascara // 2
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            vizinhanca = []
            for ky in range(tamanho_mascara):
                for kx in range(tamanho_mascara):
                    vizinhanca.append(matriz[y - offset + ky][x - offset + kx])
            saida[y][x] = min(vizinhanca)

    return saida

def passa_baixa_max(matriz, tamanho_mascara=3):
    altura = len(matriz)
    largura = len(matriz[0])
    offset = tamanho_mascara // 2
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            vizinhanca = []
            for ky in range(tamanho_mascara):
                for kx in range(tamanho_mascara):
                    vizinhanca.append(matriz[y - offset + ky][x - offset + kx])
            saida[y][x] = max(vizinhanca)

    return saida

def passa_alta_roberts(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(altura - 1):
        for x in range(largura - 1):
            gx = matriz[y][x] - matriz[y + 1][x + 1]
            gy = matriz[y][x + 1] - matriz[y + 1][x]
            saida[y][x] = max(0, min(255, int(abs(gx) + abs(gy))))

    return saida

def passa_alta_prewitt(matriz):
    kernel_x = [
        [-1, 0, 1],
        [-1, 0, 1],
        [-1, 0, 1]
    ]
    kernel_y = [
        [-1, -1, -1],
        [ 0,  0,  0],
        [ 1,  1,  1]
    ]

    altura = len(matriz)
    largura = len(matriz[0])
    offset = 1
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            gx = 0
            gy = 0
            for ky in range(3):
                for kx in range(3):
                    pixel = matriz[y - offset + ky][x - offset + kx]
                    gx += pixel * kernel_x[ky][kx]
                    gy += pixel * kernel_y[ky][kx]
            saida[y][x] = max(0, min(255, int(abs(gx) + abs(gy))))

    return saida

def passa_alta_sobel(matriz):
    kernel_x = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]
    kernel_y = [
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ]

    altura = len(matriz)
    largura = len(matriz[0])
    offset = 1
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(offset, altura - offset):
        for x in range(offset, largura - offset):
            gx = 0
            gy = 0
            for ky in range(3):
                for kx in range(3):
                    pixel = matriz[y - offset + ky][x - offset + kx]
                    gx += pixel * kernel_x[ky][kx]
                    gy += pixel * kernel_y[ky][kx]
            saida[y][x] = max(0, min(255, int(abs(gx) + abs(gy))))

    return saida

def somaIMG(matriz1, matriz2):
    """Soma duas imagens e normaliza o resultado para o intervalo 0-255."""
    altura = len(matriz1)
    largura = len(matriz1[0])
    
    # Cria a matriz auxiliar para guardar as somas
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    
    # Inicializa os valores de referência
    MaiorValor = 1000
    MenorValor = -1
    
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

import math

def T_log(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    MaiorValor = 0
    for y in range(altura):
        for x in range(largura):
            if matriz[y][x] > MaiorValor:
                MaiorValor = matriz[y][x]

    if MaiorValor == 0:
        return saida

    c = 255.0 / math.log(1 + MaiorValor)

    for y in range(altura):
        for x in range(largura):
            s = c * math.log(1 + matriz[y][x])
            saida[y][x] = int(s)

    return saida

def subIMG(matriz1, matriz2):
    altura = len(matriz1)
    largura = len(matriz1[0])
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    MaiorValor = -1000
    MenorValor = 1000

    for y in range(altura):
        for x in range(largura):
            sub = matriz1[y][x] - matriz2[y][x]
            matrizaux[y][x] = sub
            if sub > MaiorValor:
                MaiorValor = sub
            if sub < MenorValor:
                MenorValor = sub

    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    if MaiorValor == MenorValor:
        return matrizaux

    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            saida[y][x] = int((255.0 / (MaiorValor - MenorValor)) * (f - MenorValor))

    return saida

def multIMG(matriz1, matriz2):
    altura = len(matriz1)
    largura = len(matriz1[0])
    matrizaux = [[0 for _ in range(largura)] for _ in range(altura)]
    MaiorValor = -1
    MenorValor = 100000

    for y in range(altura):
        for x in range(largura):
            mul = matriz1[y][x] * matriz2[y][x]
            matrizaux[y][x] = mul
            if mul > MaiorValor:
                MaiorValor = mul
            if mul < MenorValor:
                MenorValor = mul

    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    if MaiorValor == MenorValor:
        return matrizaux

    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            saida[y][x] = int((255.0 / (MaiorValor - MenorValor)) * (f - MenorValor))

    return saida

def divIMG(matriz1, matriz2):
    altura = len(matriz1)
    largura = len(matriz1[0])
    matrizaux = [[0.0 for _ in range(largura)] for _ in range(altura)]
    MaiorValor = -1.0
    MenorValor = 1000.0

    for y in range(altura):
        for x in range(largura):
            if matriz2[y][x] == 0:
                div = 255.0
            else:
                div = matriz1[y][x] / matriz2[y][x]
            matrizaux[y][x] = div
            if div > MaiorValor:
                MaiorValor = div
            if div < MenorValor:
                MenorValor = div

    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    if MaiorValor == MenorValor:
        return [[int(v) for v in linha] for linha in matrizaux]

    for y in range(altura):
        for x in range(largura):
            f = matrizaux[y][x]
            saida[y][x] = int((255.0 / (MaiorValor - MenorValor)) * (f - MenorValor))

    return saida

def negativo(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    for y in range(altura):
        for x in range(largura):
            saida[y][x] = 255 - matriz[y][x]

    return saida

def equalizar_histograma(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    total_pixels = altura * largura

    hist = calcular_histograma(matriz)

    probabilidade_acumulada = 0.0
    mapa_de_cores = [0] * 256

    for k in range(256):
        probabilidade_acumulada += hist[k] / total_pixels
        mapa_de_cores[k] = int(probabilidade_acumulada * 255)

    saida = [[0 for _ in range(largura)] for _ in range(altura)]
    for y in range(altura):
        for x in range(largura):
            saida[y][x] = mapa_de_cores[matriz[y][x]]

    return saida

def crescimento_regioes(matriz, semente_y, semente_x, limiar=20):
    altura = len(matriz)
    largura = len(matriz[0])

    semente_y = max(0, min(altura - 1, semente_y))
    semente_x = max(0, min(largura - 1, semente_x))

    visitado = [[False for _ in range(largura)] for _ in range(altura)]
    saida = [[0 for _ in range(largura)] for _ in range(altura)]

    valor_semente = int(matriz[semente_y][semente_x])

    fila = [(semente_y, semente_x)]
    visitado[semente_y][semente_x] = True

    while fila:
        y, x = fila.pop(0)
        saida[y][x] = 255

        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < altura and 0 <= nx < largura and not visitado[ny][nx]:
                if abs(int(matriz[ny][nx]) - valor_semente) <= limiar:
                    visitado[ny][nx] = True
                    fila.append((ny, nx))

    return saida

def gerar_imagem_histograma(matriz):
    hist = calcular_histograma(matriz)

    largura_hist = 256
    altura_hist = 200

    max_freq = max(hist)
    if max_freq == 0:
        return [[255 for _ in range(largura_hist)] for _ in range(altura_hist)]

    saida = [[255 for _ in range(largura_hist)] for _ in range(altura_hist)]

    for x in range(256):
        altura_barra = int((hist[x] / max_freq) * (altura_hist - 1))
        for y in range(altura_barra):
            saida[altura_hist - 1 - y][x] = 0

    return saida