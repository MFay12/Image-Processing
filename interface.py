import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import processamento

try:
    entrada = Image.open('sua_imagem.jpg')
    matriz_original = processamento.imagem_para_matriz_cinza(entrada)
except FileNotFoundError:
    print("Erro: Coloque 'sua_imagem.jpg' na mesma pasta.")
    exit()

def matriz_para_pil(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    img = Image.new('L', (largura, altura))
    pixels_flat = [int(pixel) for linha in matriz for pixel in linha]
    img.putdata(pixels_flat)
    return img

def atualizar_interface(*args):
    """Gerencia a interface: Esconde, mostra e renomeia a barra dependendo do filtro."""
    filtro = combo_filtros.get()
    
    if filtro in ['Passa-Baixa Média', 'Passa-Baixa Mediana']:
        # Mostra a barra e ajusta para máscaras ímpares
        label_barra.config(text="Tamanho da Máscara:")
        barra_param.config(from_=3, to_=15, resolution=2) # resolution=2 pula de 2 em 2 (ímpares)
        label_barra.grid(row=0, column=1, padx=(15, 0))
        barra_param.grid(row=0, column=2, padx=(0, 15))
        
    elif filtro == 'Passa-Alta High-Boost':

        label_barra.config(text="Reforço:")
        barra_param.config(from_=10, to_=30, resolution=1) 
        label_barra.grid(row=0, column=1, padx=(15, 0))
        barra_param.grid(row=0, column=2, padx=(0, 15))
        
    else:
        # Esconde a barra para todos os outros filtros (Original, Otsu, Passa-Alta, Soma)
        label_barra.grid_remove()
        barra_param.grid_remove()
        
    aplicar_filtro()

def aplicar_filtro(*args):
    filtro = combo_filtros.get()
    parametro = int(barra_param.get())
    
    if filtro == 'Original':
        resultado = matriz_original
    elif filtro == 'Limiarização (Otsu)':
        limiar = processamento.calcular_otsu(matriz_original)
        resultado = processamento.threshold(matriz_original, limiar)
    elif filtro == 'Passa-Alta Básico':
        resultado = processamento.passa_alta_basico(matriz_original)
    elif filtro == 'Passa-Alta High-Boost':
        resultado = processamento.passa_alta_Alto_reforco(matriz_original, A=(parametro / 10.0))
    elif filtro == 'Passa-Baixa Média':
        resultado = processamento.passa_baixa_media(matriz_original, parametro)
    elif filtro == 'Passa-Baixa Mediana':
        resultado = processamento.passa_baixa_mediana(matriz_original, parametro)
    elif filtro == 'Soma (Original + Passa-Alta)':
        img_passa_alta = processamento.passa_alta_basico(matriz_original)
        resultado = processamento.somaIMG(matriz_original, img_passa_alta)
    elif filtro == 'Subtração (Original + Passa-Alta)':
        img_passa_alta = processamento.passa_alta_basico(matriz_original)
        resultado = processamento.subIMG(matriz_original,img_passa_alta)
    elif filtro == 'Multiplicação (Original + Passa-Alta)':
        img_passa_alta = processamento.passa_alta_basico(matriz_original)
        resultado = processamento.multIMG(matriz_original,img_passa_alta)
    elif filtro == 'Divisão (Original + Passa-Alta)':
        img_passa_alta = processamento.passa_alta_basico(matriz_original)
        resultado = processamento.divIMG(matriz_original,img_passa_alta)
    elif filtro == 'Negativo':
        resultado = processamento.negativo(matriz_original)
    elif filtro == 'Transformação Logarítimica':
        resultado = processamento.T_log(matriz_original)
    elif filtro == 'Equalizador':
        resultado = processamento.equalizar_histograma(matriz_original)
    elif filtro == 'Crescimento de Regiões':
        label_barra.config(text="Tolerância de Cor:")
        barra_param.config(from_=3, to_=20, resolution=1) # Tolerância de 3 a 20 tons de cinza
        label_barra.grid(row=0, column=1, padx=(15, 0))
        barra_param.grid(row=0, column=2, padx=(0, 15))    
    else:
        resultado = matriz_original

    img_pil = matriz_para_pil(resultado)
    img_tk = ImageTk.PhotoImage(img_pil)
    label_imagem.config(image=img_tk)
    label_imagem.image = img_tk 

def clicar_na_imagem(evento):
    """Captura o X e Y do clique do mouse e roda o Crescimento de Regiões."""
    filtro = combo_filtros.get()
    
    # Só faz alguma coisa se o filtro selecionado for o Crescimento
    if filtro == 'Crescimento de Regiões':
        semente_x = evento.x
        semente_y = evento.y
        tolerancia = int(barra_param.get())
        
        
        resultado = processamento.crescimento_regioes(matriz_original, semente_x, semente_y, tolerancia)
        
        # Desenha a imagem binarizada (preto e branco) na tela
        img_pil = matriz_para_pil(resultado)
        img_tk = ImageTk.PhotoImage(img_pil)
        label_imagem.config(image=img_tk)
        label_imagem.image = img_tk

# ==========================================
# CONSTRUÇÃO DA JANELA VISUAL
# ==========================================

janela = tk.Tk()
janela.title("Processamento de Imagens")
janela.geometry("900x700")

frame_controles = tk.Frame(janela)
frame_controles.pack(pady=15)

filtros = [
    'Original', 
    'Limiarização (Otsu)', 
    'Passa-Alta Básico', 
    'Passa-Alta High-Boost', 
    'Passa-Baixa Média', 
    'Passa-Baixa Mediana', 
    'Soma (Original + Passa-Alta)',
    'Subtração (Original + Passa-Alta)',
    'Multiplicação (Original + Passa-Alta)',
    'Divisão (Original + Passa-Alta)',
    'Negativo',
    'Transformação Logarítimica',
    'Equalizador',
    'Crescimento de Regiões'
]


combo_filtros = ttk.Combobox(frame_controles, values=filtros, state="readonly", width=35)
combo_filtros.set('Original')
combo_filtros.grid(row=0, column=0, padx=15)
combo_filtros.bind("<<ComboboxSelected>>", atualizar_interface) 


label_barra = tk.Label(frame_controles, text="")
barra_param = tk.Scale(frame_controles, from_=3, to_=15, orient="horizontal", length=250, command=aplicar_filtro)


label_barra.grid_remove()
barra_param.grid_remove()


img_tk_inicial = ImageTk.PhotoImage(matriz_para_pil(matriz_original))
label_imagem = tk.Label(janela, image=img_tk_inicial)
label_imagem.pack(expand=True)
label_imagem.bind("<Button-1>", clicar_na_imagem)

janela.mainloop()