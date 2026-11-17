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

# MODELO MATEMÁTICO (função logarítmica)

#   f(x) = a + b * log10(x)

#   x    = número de palavras diferentes (as x mais usadas)   [palavras]

#   f(x) = % de todas as palavras ditas que essas x cobrem    [%]

# Os pontos vêm da conversa real e a e b são ajustados por

# mínimos quadrados (regressão de y contra log10(x)).

# Referência do tipo de curva: lei de Zipf (frequência de palavras).

# ======================================================

MODELO = None   # guarda (a, b, r2, pontos_y) do último ajuste


def cobertura_acumulada(palavras):

    contagem = sorted(Counter(palavras).values(), reverse=True)

    total = sum(contagem)

    acumulado = 0

    ys = []

    for qtd in contagem:

        acumulado += qtd

        ys.append(acumulado / total * 100)

    return ys   # ys[i] é a cobertura com i+1 palavras


def ajustar_log(ys):

    n = len(ys)

    us = [math.log10(i + 1) for i in range(n)]

    soma_u = sum(us)

    soma_y = sum(ys)

    soma_uy = sum(u * y for u, y in zip(us, ys))

    soma_uu = sum(u * u for u in us)

    denominador = n * soma_uu - soma_u ** 2

    if denominador == 0:

        return None

    b = (n * soma_uy - soma_u * soma_y) / denominador

    a = (soma_y - b * soma_u) / n

    media_y = soma_y / n

    ss_tot = sum((y - media_y) ** 2 for y in ys)

    ss_res = sum((y - (a + b * u)) ** 2 for u, y in zip(us, ys))

    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1

    return a, b, r2


def f(x, a, b):

    return a + b * math.log10(x)


def grafico_svg(ys, a, b):

    n = len(ys)

    L, A = 560, 320

    ml, mr, mt, mb = 60, 20, 40, 55

    w = L - ml - mr

    h = A - mt - mb

    ymin, ymax = 0, 100

    def px(x):

        return ml + (x - 1) / max(n - 1, 1) * w

    def py(y):

        y = max(ymin, min(ymax, y))

        return mt + h - (y - ymin) / (ymax - ymin) * h

    svg = '<svg viewBox="0 0 %d %d" style="width:100%%;max-width:560px;background:#fff;border-radius:10px">' % (L, A)

    svg += '<text x="%d" y="24" text-anchor="middle" font-size="15" font-weight="bold">Cobertura da conversa pelas palavras mais usadas</text>' % (L // 2)

    # grade e eixo y

    for v in range(0, 101, 20):

        yy = py(v)

        svg += '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#ddd"/>' % (ml, yy, ml + w, yy)

        svg += '<text x="%d" y="%.1f" text-anchor="end" font-size="11">%d</text>' % (ml - 6, yy + 4, v)

    # eixo x

    passo = max(1, n // 8)

    for x in range(1, n + 1, passo):

        svg += '<text x="%.1f" y="%d" text-anchor="middle" font-size="11">%d</text>' % (px(x), mt + h + 16, x)

    svg += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>' % (ml, mt + h, ml + w, mt + h)

    svg += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>' % (ml, mt, ml, mt + h)

    svg += '<text x="%d" y="%d" text-anchor="middle" font-size="12">Palavras diferentes mais usadas (x)</text>' % (ml + w // 2, A - 28)

    svg += '<text transform="translate(16,%d) rotate(-90)" text-anchor="middle" font-size="12">Cobertura da conversa (%%)</text>' % (mt + h // 2)

    # curva ajustada

    pontos = []

    passos = 120

    for k in range(passos + 1):

        x = 1 + (n - 1) * k / passos

        pontos.append("%.1f,%.1f" % (px(x), py(f(x, a, b))))

    svg += '<polyline points="%s" fill="none" stroke="#e53935" stroke-width="2.5"/>' % " ".join(pontos)

    # pontos reais

    for i, y in enumerate(ys):

        svg += '<circle cx="%.1f" cy="%.1f" r="3.5" fill="#1e88e5"/>' % (px(i + 1), py(y))

    # legenda

    svg += '<circle cx="%d" cy="%d" r="4" fill="#1e88e5"/><text x="%d" y="%d" font-size="11">dados reais</text>' % (ml + 12, mt + 12, ml + 22, mt + 16)

    svg += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#e53935" stroke-width="2.5"/><text x="%d" y="%d" font-size="11">f(x) = %.1f %s %.1f·log10(x)</text>' % (

        ml + 8, mt + 30, ml + 18, mt + 30, ml + 24, mt + 34, a, "+" if b >= 0 else "−", abs(b))

    svg += '</svg>'

    return svg


def atualizar_modelo(palavras):

    global MODELO

    caixa = document.querySelector("#graficoModelo")

    texto = document.querySelector("#modelo")

    if len(set(palavras)) < 3:

        MODELO = None

        caixa.innerHTML = '<p class="vazio">Precisa de pelo menos 3 palavras diferentes para ajustar o modelo.</p>'

        texto.innerText = ""

        return

    ys = cobertura_acumulada(palavras)

    resultado = ajustar_log(ys)

    if resultado is None:

        MODELO = None

        return

    a, b, r2 = resultado

    MODELO = (a, b, r2, ys)

    n = len(ys)

    caixa.innerHTML = grafico_svg(ys, a, b)

    t = "f(x) = " + str(round(a, 2)) + (" + " if b >= 0 else " - ") + str(round(abs(b), 2)) + " · log10(x)\n"

    t += "R² do ajuste: " + str(round(r2, 3)) + "\n"

    t += "f(1) = " + str(round(a, 1)) + "% (a palavra mais usada sozinha)\n"

    t += "Multiplicar x por 10 muda a cobertura em " + str(round(b, 1)) + " pontos percentuais\n"

    if b != 0:

        zero = 10 ** (-a / b)

        t += "Zero da função: x = " + str(round(zero, 2)) + " palavras"

        t += " (dentro do domínio do problema)" if 1 <= zero <= n else " (fora do domínio do problema, 1 a " + str(n) + ")"

    texto.innerText = t


def simular(evento=None):

    saida = document.querySelector("#simulacao")

    if MODELO is None:

        saida.innerText = "Ainda não há modelo ajustado."

        return

    a, b, r2, ys = MODELO

    try:

        meta = float(document.querySelector("#metaPct").value)

    except ValueError:

        saida.innerText = "Digite um número entre 1 e 99."

        return

    if meta <= 0 or meta >= 100 or b <= 0:

        saida.innerText = "Digite um número entre 1 e 99."

        return

    x_modelo = math.ceil(10 ** ((meta - a) / b))

    x_modelo = max(1, x_modelo)

    real = None

    for i, y in enumerate(ys):

        if y >= meta:

            real = i + 1

            break

    t = "Para cobrir " + str(round(meta)) + "% da conversa, o modelo indica " + str(x_modelo) + " palavras.\n"

    if real is not None:

        t += "Nos dados reais, bastaram " + str(real) + " palavras."

    else:

        t += "Os dados reais ainda não chegam a essa cobertura."

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
 