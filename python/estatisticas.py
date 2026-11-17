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

   svg = '<svg viewBox="0 0 ' + str(largura) + ' ' + str(altura) + '" width="100%" style="max-width:900px;display:block;margin:0 auto;font-family:sans-serif;">'

   # título

   svg += '<text x="' + str(largura / 2) + '" y="28" text-anchor="middle" font-size="20" font-weight="bold" fill="#1a2b4c">Cobertura da conversa pelas palavras mais usadas</text>'

   # linhas horizontais e números do eixo y (0% a 100%)

   for y in range(0, 101, 20):

       py = pos_y(y)

       svg += '<line x1="' + str(esq) + '" y1="' + str(py) + '" x2="' + str(esq + area_w) + '" y2="' + str(py) + '" stroke="#d5dbe8" stroke-width="1"/>'

       svg += '<text x="' + str(esq - 10) + '" y="' + str(py + 5) + '" text-anchor="end" font-size="14" fill="#333">' + str(y) + '%</text>'

   # números do eixo x

   passo = max(1, round(n / 10))

   for x in range(1, n + 1):

       if x == 1 or x == n or x % passo == 0:

           px = pos_x(x)

           svg += '<line x1="' + str(px) + '" y1="' + str(topo + area_h) + '" x2="' + str(px) + '" y2="' + str(topo + area_h + 6) + '" stroke="#333"/>'

           svg += '<text x="' + str(px) + '" y="' + str(topo + area_h + 22) + '" text-anchor="middle" font-size="14" fill="#333">' + str(x) + '</text>'

   # eixos

   svg += '<line x1="' + str(esq) + '" y1="' + str(topo) + '" x2="' + str(esq) + '" y2="' + str(topo + area_h) + '" stroke="#333" stroke-width="2"/>'

   svg += '<line x1="' + str(esq) + '" y1="' + str(topo + area_h) + '" x2="' + str(esq + area_w) + '" y2="' + str(topo + area_h) + '" stroke="#333" stroke-width="2"/>'

   # nomes dos eixos

   svg += '<text x="' + str(esq + area_w / 2) + '" y="' + str(altura - 14) + '" text-anchor="middle" font-size="15" fill="#1a2b4c">x = quantidade de palavras diferentes (das mais usadas para as menos usadas)</text>'

   svg += '<text transform="translate(20 ' + str(topo + area_h / 2) + ') rotate(-90)" text-anchor="middle" font-size="15" fill="#1a2b4c">f(x) = % da conversa coberta</text>'

   # curva do modelo (linha vermelha)

   pontos = ''

   passos = 120

   for i in range(passos + 1):

       x = 1 + (n - 1) * i / passos

       pontos += str(round(pos_x(x), 1)) + ',' + str(round(pos_y(f(x, a, b)), 1)) + ' '

   svg += '<polyline points="' + pontos + '" fill="none" stroke="#e03131" stroke-width="3"/>'

   # dados reais (bolinhas azuis)

   for i in range(n):

       svg += '<circle cx="' + str(round(pos_x(i + 1), 1)) + '" cy="' + str(round(pos_y(cobertura[i]), 1)) + '" r="5" fill="#1c5fd6"/>'

   # legenda

   svg += '<circle cx="' + str(esq + 20) + '" cy="' + str(topo + 18) + '" r="5" fill="#1c5fd6"/>'

   svg += '<text x="' + str(esq + 32) + '" y="' + str(topo + 23) + '" font-size="14" fill="#333">dados reais da conversa</text>'

   svg += '<line x1="' + str(esq + 15) + '" y1="' + str(topo + 42) + '" x2="' + str(esq + 25) + '" y2="' + str(topo + 42) + '" stroke="#e03131" stroke-width="3"/>'

   svg += '<text x="' + str(esq + 32) + '" y="' + str(topo + 47) + '" font-size="14" fill="#333">modelo f(x) = a + b·log10(x)</text>'

   svg += '</svg>'

   return svg

def atualizar_modelo(palavras):

   global modelo

   caixa = document.querySelector("#graficoModelo")

   texto = document.querySelector("#modelo")

   # precisa de pelo menos 3 palavras diferentes pra ajustar a curva

   if len(set(palavras)) < 3:

       modelo = None

       caixa.innerHTML = '<p class="vazio">Precisa de pelo menos 3 palavras diferentes.</p>'

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

       c.innerHTML = '<strong style="display:block;font-size:34px;color:#1c5fd6;">' + numero + '</strong><span style="font-size:15px;color:#1a2b4c;">' + frase + '</span>'

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

   document.querySelector("#grafico").innerHTML = '<p class="vazio">Converse na tela de tradução primeiro.</p>'

   document.querySelector("#graficoModelo").innerHTML = '<p class="vazio">Converse na tela de tradução primeiro.</p>'

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

       document.querySelector("#grafico").innerHTML = '<p class="vazio">Sem palavras para mostrar.</p>'

   document.querySelector("#numeros").innerText = texto

   atualizar_modelo(todas)

def zerar(evento=None):

   window.localStorage.removeItem(CHAVE)

   mostrar_vazio()

atualizar()

document.querySelector("#statusPython").innerText = "Python pronto ✔"
 
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

   svg = '<svg viewBox="0 0 ' + str(largura) + ' ' + str(altura) + '" width="100%" style="max-width:900px;display:block;margin:0 auto;font-family:sans-serif;">'

   # título

   svg += '<text x="' + str(largura / 2) + '" y="28" text-anchor="middle" font-size="20" font-weight="bold" fill="#1a2b4c">Cobertura da conversa pelas palavras mais usadas</text>'

   # linhas horizontais e números do eixo y (0% a 100%)

   for y in range(0, 101, 20):

       py = pos_y(y)

       svg += '<line x1="' + str(esq) + '" y1="' + str(py) + '" x2="' + str(esq + area_w) + '" y2="' + str(py) + '" stroke="#d5dbe8" stroke-width="1"/>'

       svg += '<text x="' + str(esq - 10) + '" y="' + str(py + 5) + '" text-anchor="end" font-size="14" fill="#333">' + str(y) + '%</text>'

   # números do eixo x

   passo = max(1, round(n / 10))

   for x in range(1, n + 1):

       if x == 1 or x == n or x % passo == 0:

           px = pos_x(x)

           svg += '<line x1="' + str(px) + '" y1="' + str(topo + area_h) + '" x2="' + str(px) + '" y2="' + str(topo + area_h + 6) + '" stroke="#333"/>'

           svg += '<text x="' + str(px) + '" y="' + str(topo + area_h + 22) + '" text-anchor="middle" font-size="14" fill="#333">' + str(x) + '</text>'

   # eixos

   svg += '<line x1="' + str(esq) + '" y1="' + str(topo) + '" x2="' + str(esq) + '" y2="' + str(topo + area_h) + '" stroke="#333" stroke-width="2"/>'

   svg += '<line x1="' + str(esq) + '" y1="' + str(topo + area_h) + '" x2="' + str(esq + area_w) + '" y2="' + str(topo + area_h) + '" stroke="#333" stroke-width="2"/>'

   # nomes dos eixos

   svg += '<text x="' + str(esq + area_w / 2) + '" y="' + str(altura - 14) + '" text-anchor="middle" font-size="15" fill="#1a2b4c">x = quantidade de palavras diferentes (das mais usadas para as menos usadas)</text>'

   svg += '<text transform="translate(20 ' + str(topo + area_h / 2) + ') rotate(-90)" text-anchor="middle" font-size="15" fill="#1a2b4c">f(x) = % da conversa coberta</text>'

   # curva do modelo (linha vermelha)

   pontos = ''

   passos = 120

   for i in range(passos + 1):

       x = 1 + (n - 1) * i / passos

       pontos += str(round(pos_x(x), 1)) + ',' + str(round(pos_y(f(x, a, b)), 1)) + ' '

   svg += '<polyline points="' + pontos + '" fill="none" stroke="#e03131" stroke-width="3"/>'

   # dados reais (bolinhas azuis)

   for i in range(n):

       svg += '<circle cx="' + str(round(pos_x(i + 1), 1)) + '" cy="' + str(round(pos_y(cobertura[i]), 1)) + '" r="5" fill="#1c5fd6"/>'

   # legenda

   svg += '<circle cx="' + str(esq + 20) + '" cy="' + str(topo + 18) + '" r="5" fill="#1c5fd6"/>'

   svg += '<text x="' + str(esq + 32) + '" y="' + str(topo + 23) + '" font-size="14" fill="#333">dados reais da conversa</text>'

   svg += '<line x1="' + str(esq + 15) + '" y1="' + str(topo + 42) + '" x2="' + str(esq + 25) + '" y2="' + str(topo + 42) + '" stroke="#e03131" stroke-width="3"/>'

   svg += '<text x="' + str(esq + 32) + '" y="' + str(topo + 47) + '" font-size="14" fill="#333">modelo f(x) = a + b·log10(x)</text>'

   svg += '</svg>'

   return svg

def atualizar_modelo(palavras):

   global modelo

   caixa = document.querySelector("#graficoModelo")

   texto = document.querySelector("#modelo")

   # precisa de pelo menos 3 palavras diferentes pra ajustar a curva

   if len(set(palavras)) < 3:

       modelo = None

       caixa.innerHTML = '<p class="vazio">Precisa de pelo menos 3 palavras diferentes.</p>'

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

       c.innerHTML = '<strong style="display:block;font-size:34px;color:#1c5fd6;">' + numero + '</strong><span style="font-size:15px;color:#1a2b4c;">' + frase + '</span>'

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

   document.querySelector("#grafico").innerHTML = '<p class="vazio">Converse na tela de tradução primeiro.</p>'

   document.querySelector("#graficoModelo").innerHTML = '<p class="vazio">Converse na tela de tradução primeiro.</p>'

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

       document.querySelector("#grafico").innerHTML = '<p class="vazio">Sem palavras para mostrar.</p>'

   document.querySelector("#numeros").innerText = texto

   atualizar_modelo(todas)

def zerar(evento=None):

   window.localStorage.removeItem(CHAVE)

   mostrar_vazio()

atualizar()

document.querySelector("#statusPython").innerText = "Python pronto ✔"
 