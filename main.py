from PIL import Image
import processamento
import math

def salvar_matriz(matriz, nome_arquivo):
    """O Pillow apenas pega a matriz processada e escreve um arquivo no disco."""
    altura = len(matriz)
    largura = len(matriz[0])
    
    # Cria um "canvas" em branco para tons de cinza ('L')
    img = Image.new('L', (largura, altura))
    
    # Achata a nossa matriz de volta para uma lista simples e salva
    pixels_flat = [int(pixel) for linha in matriz for pixel in linha]
    img.putdata(pixels_flat)
    img.save(nome_arquivo)
    print(f"--> Salvo: {nome_arquivo}")

def executar():
    # 1. Carregar a imagem.
    try:
        entrada = Image.open('sua_imagem.jpg')
    except FileNotFoundError:
        print("Erro: Coloque um arquivo chamado 'sua_imagem.jpg' na mesma pasta.")
        return

    # Conversão RGB -> Cinza Manual
    print("\nConvertendo RGB para Escala de Cinza...")
    matriz_original = processamento.imagem_para_matriz_cinza(entrada)
    salvar_matriz(matriz_original, 'resultado_cinza.png')

    # Otsu + Threshold
    print("\nCalculando Limiar de Otsu...")
    limiar_otimo = processamento.calcular_otsu(matriz_original)
    print(f"Limiar encontrado pelo Otsu: {limiar_otimo}")
    img_otsu = processamento.threshold(matriz_original, limiar_otimo)
    salvar_matriz(img_otsu, 'resultado_otsu_threshold.png')

    # Passa-Alta
    print("\nAplicando Passa-Alta...")
    img_passa_alta = processamento.passa_alta_basico(matriz_original)
    salvar_matriz(img_passa_alta, 'resultado_passa_alta.png')

    # Alto Reforço
    print("\nAplicando Alto reforço...")
    img_Alto_reforco = processamento.passa_alta_Alto_reforco(matriz_original, A=1.5)
    salvar_matriz(img_Alto_reforco, 'resultado_Alto_reforco.png')

    # Mediana
    print("\nAplicando Mediana...")
    img_Mediana = processamento.passa_baixa_mediana(matriz_original,tamanho_mascara=3)
    salvar_matriz(img_Mediana, 'resultado_Mediana.png')

    # Média
    print("\nAplicando Media...")
    img_Media = processamento.passa_baixa_media(matriz_original,tamanho_mascara=3)
    salvar_matriz(img_Media, 'resultado_Media.png')
    
    
    print("\nConcluído com sucesso!")

if __name__ == "__main__":
    executar()