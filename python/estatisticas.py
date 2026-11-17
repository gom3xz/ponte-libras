# ======================================================
# PONTE LIBRAS - Estatísticas da conversa (Python no navegador, PyScript)
# Lê a conversa salva pelo js/script.js e calcula números e gráfico.
# ======================================================
import json
import math
import statistics
from collections import Counter
from pyscript import document, window
CHAVE = "ponteLibrasHistorico"
# palavras de ligação que atrapalham o gráfico
IGNORAR = {"a", "o", "e", "de", "da", "do", "um", "uma", "em", "eu", "me", "para", "com", "que"}

def carregar_historico():
   bruto = window.localStorage.getItem(CHAVE)
   if not bruto:
       return []
   return json.loads(bruto)

def separar_palavras(texto):
   texto = texto.lower()
   for sinal in ".,!?;:":
       texto = texto.replace(sinal, "")
   return texto.split()

# ======================================================
# MODELO MATEMÁTICO: função logarítmica
# f(x) = a + b * log10(x)
#   x    = quantidade de palavras diferentes (as mais usadas)
#   f(x) = % da conversa que essas palavras cobrem
# a e b são calculados pelos dados da conversa (ajuste)
# ======================================================
modelo = None  # guarda a, b, r2 e os pontos depois que calcula

def calcular_cobertura(palavras):
   # conta quantas vezes cada palavra apareceu, da maior para a menor
   contagem = sorted(Counter(palavras).values(), reverse=True)
   total = sum(contagem)
   cobertura = []
   soma = 0
   for qtd in contagem:
       soma = soma + qtd
       cobertura.append(soma / total * 100)
   return cobertura  # posição 0 = só a 1ª palavra, posição 1 = as 2 primeiras...

def calcular_a_b(cobertura):
   # ajuste por mínimos quadrados: y = a + b*u, com u = log10(x)
   n = len(cobertura)
   u = []
   for i in range(n):
       u.append(math.log10(i + 1))
   soma_u = sum(u)
   soma_y = sum(cobertura)
   soma_uy = 0
   soma_uu = 0
   for i in range(n):
       soma_uy = soma_uy + u[i] * cobertura[i]
       soma_uu = soma_uu + u[i] * u[i]
   b = (n * soma_uy - soma_u * soma_y) / (n * soma_uu - soma_u ** 2)
   a = (soma_y - b * soma_u) / n
   # R²: mostra o quanto a curva acompanha os pontos (0 a 1)
   media = soma_y / n
   erro_total = 0
   erro_modelo = 0
   for i in range(n):
       erro_total = erro_total + (cobertura[i] - media) ** 2
       erro_modelo = erro_modelo + (cobertura[i] - (a + b * u[i])) ** 2
   r2 = 1 - erro_modelo / erro_total
   return a, b, r2

def f(x, a, b):
   return a + b * math.log10(x)

def desenhar_modelo(cobertura, a, b):
   n = len(cobertura)
   largura = 800
   altura = 480
   esq = 70      # margem esquerda
   topo = 50
   area_w = 700  # largura da área do gráfico
   area_h = 340  # altura da área do gráfico
   def pos_x(x):
       return esq + (x - 1) / (n - 1) * area_w
   def pos_y(y):
       if y < 0:
           y = 0
       if y > 100:
           y = 100
       return topo + area_h - y / 100 * area_h
   svg = ''
   return svg

def atualizar_modelo(palavras):
   global modelo
   caixa = document.querySelector("#graficoModelo")
   texto = document.querySelector("#modelo")
   # precisa de pelo menos 3 palavras diferentes pra ajustar a curva
   if len(set(palavras)) < 3:
       modelo = None
       caixa.innerHTML = ' Precisa de pelo menos 3 palavras diferentes.'
       texto.innerText = ""
       document.querySelector("#cartoesModelo").innerHTML = ""
       document.querySelector("#formula").innerText = ""
       return
   cobertura = calcular_cobertura(palavras)
   a, b, r2 = calcular_a_b(cobertura)
   modelo = (a, b, r2, cobertura)
   n = len(cobertura)
   caixa.innerHTML = desenhar_modelo(cobertura, a, b)
   zero = 10 ** (-a / b)
   # cartões grandes com frases fáceis
   cartoes = document.querySelector("#cartoesModelo")
   cartoes.innerHTML = ""
   itens = [
       (str(round(max(0, min(100, f(5, a, b))))) + "%", "5 palavras já cobrem isso da conversa"),
       (str(round(max(0, min(100, f(10, a, b))))) + "%", "10 palavras cobrem isso da conversa"),
       (str(round(max(0, min(100, f(n, a, b))))) + "%", "todas as " + str(n) + " palavras juntas (segundo o modelo)"),
   ]
   for numero, frase in itens:
       c = document.createElement("div")
       c.style.cssText = "background:#e3ecfb;border-radius:12px;padding:14px;text-align:center;"
       c.innerHTML = '' + numero + '' + frase + ''
       cartoes.appendChild(c)
   sinal = " + " if b >= 0 else " - "
   document.querySelector("#formula").innerText = "Fórmula: f(x) = " + str(round(a, 2)) + sinal + str(round(abs(b), 2)) + " · log10(x)   (R² = " + str(round(r2, 3)) + ")"
   t = "f(x) = " + str(round(a, 2)) + " + " + str(round(b, 2)) + " · log10(x)\n"
   t += "R² do ajuste: " + str(round(r2, 3)) + "\n"
   t += "a = f(1) = " + str(round(a, 2)) + " %\n"
   t += "b = " + str(round(b, 2)) + " pontos percentuais a cada x multiplicado por 10\n"
   t += "Zero da função: x = " + str(round(zero, 2)) + " palavras\n"
   t += "Domínio do problema: de 1 a " + str(n) + " palavras\n"
   t += "f(1) = " + str(round(f(1, a, b), 1)) + " %\n"
   t += "f(10) = " + str(round(f(10, a, b), 1)) + " %\n"
   t += "f(" + str(n) + ") = " + str(round(f(n, a, b), 1)) + " %\n"
   t += "f(10) - f(1) = " + str(round(f(10, a, b) - f(1, a, b), 1)) + " pontos percentuais\n"
   t += "f(100) - f(10) = " + str(round(f(100, a, b) - f(10, a, b), 1)) + " pontos percentuais"
   texto.innerText = t

def simular(evento=None):
   saida = document.querySelector("#simulacao")
   if modelo is None:
       saida.innerText = "Ainda não há modelo."
       return
   a, b, r2, cobertura = modelo
   try:
       meta = float(document.querySelector("#metaPct").value)
   except ValueError:
       saida.innerText = "Digite um número entre 1 e 99."
       return
   if meta < 1 or meta > 99:
       saida.innerText = "Digite um número entre 1 e 99."
       return
   # isolando x na fórmula: x = 10^((meta - a) / b)
   x_modelo = math.ceil(10 ** ((meta - a) / b))
   # nos dados reais: primeira posição que chega na meta
   x_real = None
   for i in range(len(cobertura)):
       if cobertura[i] >= meta:
           x_real = i + 1
           break
   t = "Para entender " + str(round(meta)) + "% da conversa, a fórmula diz que você precisa saber cerca de " + str(x_modelo) + " palavras.\n"
   if x_real is None:
       t += "Nos dados reais ainda não chegou nessa porcentagem."
   else:
       t += "Na conversa de verdade, bastaram " + str(x_real) + " palavras."
   t += "\n\nComo ler: a fórmula é uma estimativa. Quanto mais perto os dois números, melhor o modelo."
   saida.innerText = t

def desenhar_grafico(contagem, total):
   caixa = document.querySelector("#grafico")
   caixa.innerHTML = ""
   maior = contagem[0][1]
   for palavra, qtd in contagem:
       largura = qtd / maior * 100
       porcento = qtd / total * 100
       linha = document.createElement("div")
       linha.className = "barra-linha"
       nome = document.createElement("span")
       nome.innerText = palavra
       fundo = document.createElement("div")
       fundo.className = "barra-fundo"
       barra = document.createElement("div")
       barra.className = "barra"
       barra.style.width = str(round(largura)) + "%"
       valor = document.createElement("small")
       valor.innerText = str(qtd) + "x (" + str(round(porcento)) + "%)"
       fundo.appendChild(barra)
       linha.appendChild(nome)
       linha.appendChild(fundo)
       linha.appendChild(valor)
       caixa.appendChild(linha)

def mostrar_vazio():
   document.querySelector("#numeros").innerText = "Ainda não há mensagens."
   document.querySelector("#grafico").innerHTML = ' Converse na tela de tradução primeiro.'
   document.querySelector("#graficoModelo").innerHTML = ' Converse na tela de tradução primeiro.'
   document.querySelector("#modelo").innerText = ""
   document.querySelector("#simulacao").innerText = ""
   document.querySelector("#cartoesModelo").innerHTML = ""
   document.querySelector("#formula").innerText = ""

def atualizar(evento=None):
   historico = carregar_historico()
   if len(historico) == 0:
       mostrar_vazio()
       return
   importantes = []   # palavras que entram no gráfico
   todas = []         # todas as palavras (usadas no modelo)
   tamanhos = []      # quantas palavras tem cada mensagem
   do_sinalizador = 0
   for mensagem in historico:
       palavras = separar_palavras(mensagem["texto"])
       tamanhos.append(len(palavras))
       todas = todas + palavras
       importantes = importantes + [p for p in palavras if p not in IGNORAR]
       if mensagem["quem"] == "sinaliza":
           do_sinalizador += 1
   total_mensagens = len(historico)
   total_palavras = sum(tamanhos)
   media = statistics.mean(tamanhos)
   mediana = statistics.median(tamanhos)
   desvio = statistics.pstdev(tamanhos)
   pct_sinaliza = do_sinalizador / total_mensagens * 100
   texto = "Mensagens: " + str(total_mensagens) + "\n"
   texto += "Palavras no total: " + str(total_palavras) + "\n"
   texto += "Média por mensagem: " + str(round(media, 2)) + "\n"
   texto += "Mediana: " + str(mediana) + "\n"
   texto += "Desvio padrão: " + str(round(desvio, 2)) + "\n"
   texto += "Da pessoa que sinaliza: " + str(round(pct_sinaliza)) + "%\n"
   texto += "Da pessoa ouvinte: " + str(round(100 - pct_sinaliza)) + "%"
   if len(importantes) > 0:
       mais_usadas = Counter(importantes).most_common(8)
       texto += "\nPalavra mais usada: " + mais_usadas[0][0]
       desenhar_grafico(mais_usadas, len(importantes))
   else:
       document.querySelector("#grafico").innerHTML = ' Sem palavras para mostrar.'
   document.querySelector("#numeros").innerText = texto
   atualizar_modelo(todas)

def zerar(evento=None):
   window.localStorage.removeItem(CHAVE)
   mostrar_vazio()

atualizar()
document.querySelector("#statusPython").innerText = "Python pronto ✔"