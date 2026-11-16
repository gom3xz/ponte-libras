# ======================================================
# PONTE LIBRAS - Estatísticas da conversa (Python no navegador, PyScript)
# Lê a conversa salva pelo js/script.js e calcula números e gráfico.
# ======================================================

import json
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


def atualizar(evento=None):
    historico = carregar_historico()

    if len(historico) == 0:
        mostrar_vazio()
        return

    importantes = []   # palavras que entram no gráfico
    tamanhos = []      # quantas palavras tem cada mensagem
    do_sinalizador = 0

    for mensagem in historico:
        palavras = separar_palavras(mensagem["texto"])
        tamanhos.append(len(palavras))
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


def zerar(evento=None):
    window.localStorage.removeItem(CHAVE)
    mostrar_vazio()


atualizar()
document.querySelector("#statusPython").innerText = "Python pronto ✔"
