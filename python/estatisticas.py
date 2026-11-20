import json
import math
import statistics
from collections import Counter
from pyscript import document, window

CHAVE = "ponteLibrasHistorico"
CHAVE_EXEMPLO = "ponteLibrasExemplo"

# palavras de ligação que atrapalham o gráfico de barras
IGNORAR = {"a", "o", "e", "de", "da", "do", "um", "uma", "em", "eu", "me", "para", "com", "que"}

# conversa de EXEMPLO (dados inventados, só para demonstrar o modelo)
EXEMPLO = [
    {"quem": "sinaliza", "texto": "oi eu quero comprar pão e leite"},
    {"quem": "ouve", "texto": "oi eu posso ajudar você a comprar pão"},
    {"quem": "sinaliza", "texto": "eu quero pão e queijo"},
    {"quem": "ouve", "texto": "o pão está aqui e o queijo também"},
    {"quem": "sinaliza", "texto": "quanto custa o pão"},
    {"quem": "ouve", "texto": "o pão custa dois reais"},
    {"quem": "sinaliza", "texto": "eu quero dois pão e leite"},
    {"quem": "ouve", "texto": "o leite custa cinco reais"},
    {"quem": "sinaliza", "texto": "obrigado eu quero pagar"},
    {"quem": "ouve", "texto": "pode pagar aqui obrigado"},
    {"quem": "sinaliza", "texto": "tchau obrigado"},
    {"quem": "ouve", "texto": "tchau volte sempre"},
]


def num(valor, casas=1):
    # número com vírgula, como a gente escreve no Brasil (ex.: 12,5)
    texto = (("%." + str(casas) + "f") % valor).replace(".", ",")
    return texto.replace("-", "−")


def par(valor, casas=2):
    # número negativo vai entre parênteses nas contas (ex.: 80 − (−2,69))
    texto = num(valor, casas)
    if valor < 0:
        return "(" + texto + ")"
    return texto


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
# Por que logarítmica? Nos textos, poucas palavras aparecem
# muito e a maioria aparece pouco (lei de Zipf, 1949): o ganho
# de cobertura diminui a cada palavra nova.
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
    if erro_total == 0:
        r2 = 1
    else:
        r2 = 1 - erro_modelo / erro_total
    return a, b, r2


def f(x, a, b):
    return a + b * math.log10(x)


def formula_texto(a, b, x="x"):
    # escreve a fórmula já com o sinal certo (evita "+ -2,3")
    sinal = " + " if b >= 0 else " − "
    return num(a, 2) + sinal + num(abs(b), 2) + "·log10(" + x + ")"


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



def montar_analise(a, b, r2, n, cobertura):
    f1 = f(1, a, b)
    f10 = f(10, a, b)
    fn = f(n, a, b)
    zero = 10 ** (-a / b)
    x100 = 10 ** ((100 - a) / b)
    salto1 = f(10, a, b) - f(1, a, b)      # de x = 1 até x = 10
    salto2 = f(100, a, b) - f(10, a, b)    # de x = 10 até x = 100

    t = "1) DOMÍNIO E IMAGEM\n"
    t += "Domínio matemático: x > 0, ou seja, o intervalo (0, +∞), porque log10(x) só existe para x positivo.\n"
    t += "Imagem matemática: todos os números reais.\n"
    t += "Domínio do problema: x inteiro, de 1 a " + str(n) + " palavras diferentes.\n"
    t += "Imagem do problema: de f(1) = " + num(f1) + " % até f(" + str(n) + ") = " + num(fn) + " % (cobertura da conversa).\n"
    if f1 < 0:
        t += "Atenção: f(1) deu negativo. Cobertura negativa não existe; é um erro do ajuste perto de x = 1 (na conversa real, a 1ª palavra já cobre " + num(cobertura[0]) + " %).\n"
    if fn > 100:
        t += "Atenção: f(" + str(n) + ") passou de 100 %. Cobertura acima de 100 % não existe, então o modelo só vale até cerca de " + num(x100, 1) + " palavras.\n"

    t += "\n2) CRESCIMENTO\n"
    if b > 0:
        t += "Função CRESCENTE, porque b = " + num(b, 2) + " > 0: quanto mais palavras a pessoa aprende, maior a parte da conversa que ela entende.\n"
    elif b < 0:
        t += "Função DECRESCENTE, porque b = " + num(b, 2) + " < 0. Para cobertura isso é estranho e indica dados pouco confiáveis.\n"
    else:
        t += "Função constante (b = 0): aprender mais palavras não muda a cobertura.\n"

    t += "\n3) COMPORTAMENTO\n"
    t += "Assíntota vertical x = 0: quando x chega perto de 0, f(x) tende a −∞. Isso não atrapalha o problema, porque o domínio do problema começa em x = 1 (não existe meia palavra).\n"
    if a >= 0:
        t += "a = f(1) = " + num(a, 2) + " %: pelo modelo, só a palavra mais usada já cobre " + num(f1) + " % da conversa (na conversa real ela cobre " + num(cobertura[0]) + " %).\n"
    else:
        t += "a = f(1) = " + num(a, 2) + " %: o modelo dá um valor negativo para 1 palavra, o que não existe na prática. Na conversa real a palavra mais usada cobre " + num(cobertura[0]) + " %. Isso mostra que o modelo erra um pouco perto de x = 1.\n"
    t += "b = " + num(b, 2) + " pontos percentuais: cada vez que o número de palavras é multiplicado por 10, a cobertura sobe " + num(b) + " pontos percentuais.\n"
    if zero < 1:
        t += "Zero da função: x0 = 10^(−a/b) = " + num(zero, 3) + " palavra. Esse valor é menor que 1, então cai FORA do domínio do problema (não existe menos de 1 palavra).\n"
    elif zero <= n:
        t += "Zero da função: x0 = 10^(−a/b) = " + num(zero, 2) + " palavras. Cai DENTRO do domínio do problema: com menos palavras que isso o modelo daria cobertura negativa.\n"
    else:
        t += "Zero da função: x0 = 10^(−a/b) = " + num(zero, 2) + " palavras. Esse valor é maior que " + str(n) + ", então cai FORA do domínio do problema.\n"

    t += "\nO crescimento fica cada vez mais lento:\n"
    t += "• de x = 1 a x = 10 (9 palavras a mais): f sobe " + num(salto1) + " pontos percentuais, ou " + num(salto1 / 9, 2) + " p.p. por palavra acrescentada.\n"
    t += "• de x = 10 a x = 100 (90 palavras a mais): f sobe " + num(salto2) + " pontos percentuais, ou " + num(salto2 / 90, 2) + " p.p. por palavra acrescentada.\n"
    t += "Os dois saltos são iguais (valem b), mas o segundo precisa de 10 vezes mais palavras: o ganho por palavra cai para 1/10.\n"
    if n < 100:
        t += "Atenção: x = 100 está fora do domínio do problema (esta conversa tem só " + str(n) + " palavras diferentes). Esse valor é uma extrapolação do modelo"
        if f(100, a, b) > 100:
            t += " e passa de 100 %, o que não existe"
        t += ".\n"

    t += "\n4) INTERPRETAÇÃO\n"
    t += "Cada vez que o número de palavras aprendidas é multiplicado por 10, a cobertura da conversa sobe " + num(b) + " pontos percentuais. As primeiras palavras rendem muito; as seguintes rendem cada vez menos.\n"
    t += "Ajuste: R² = " + num(r2, 3) + " (quanto mais perto de 1, melhor a curva acompanha os dados).\n"
    if n < 10:
        t += "Cuidado: só há " + str(n) + " palavras diferentes. Com tão poucos dados o ajuste é pouco confiável; converse mais para melhorar o modelo.\n"
    return t


def montar_contas(a, b, n):
    zero = 10 ** (-a / b)
    meta = 80
    expoente = (meta - a) / b
    t = "Modelo ajustado: f(x) = " + formula_texto(a, b) + "\n\n"
    t += "Zero da função:\n"
    t += "f(x) = 0  →  " + formula_texto(a, b) + " = 0\n"
    t += "log10(x) = −a/b = −" + par(a) + " / " + par(b) + " = " + num(-a / b, 3) + "\n"
    t += "x = 10^" + num(-a / b, 3) + " = " + num(zero, 3) + "\n\n"
    t += "Valores de f:\n"
    t += "f(1) = a + b·log10(1) = " + par(a) + " + " + par(b) + "·0 = " + num(f(1, a, b), 2) + " %\n"
    t += "f(10) = a + b·log10(10) = " + par(a) + " + " + par(b) + "·1 = " + num(f(10, a, b), 2) + " %\n"
    t += "f(" + str(n) + ") = a + b·log10(" + str(n) + ") = " + par(a) + " + " + par(b) + "·" + num(math.log10(n), 3) + " = " + num(f(n, a, b), 2) + " %\n"
    t += "f(100) = a + b·log10(100) = " + par(a) + " + " + par(b) + "·2 = " + num(f(100, a, b), 2) + " %"
    if n < 100:
        t += "  (extrapolação: fora do domínio do problema)"
    t += "\n\n"
    t += "Para uma meta de " + str(meta) + " % da conversa (isolando x):\n"
    t += str(meta) + " = a + b·log10(x)  →  log10(x) = (" + str(meta) + " − a)/b = (" + str(meta) + " − " + par(a) + ") / " + par(b) + " = " + num(expoente, 3) + "\n"
    t += "x = 10^" + num(expoente, 3) + " = " + num(10 ** expoente, 2) + " palavras\n\n"
    t += "Compare estes números com os que você fez à mão no relatório."
    return t


def limpar_modelo():
    document.querySelector("#modelo").innerText = ""
    document.querySelector("#analise").innerText = "Ainda não há modelo."
    document.querySelector("#contas").innerText = ""
    document.querySelector("#cartoesModelo").innerHTML = ""
    document.querySelector("#formula").innerText = ""


def atualizar_modelo(palavras):
    global modelo
    caixa = document.querySelector("#graficoModelo")
    texto = document.querySelector("#modelo")

    # precisa de pelo menos 3 palavras diferentes pra ajustar a curva
    if len(set(palavras)) < 3:
        modelo = None
        caixa.innerHTML = '<p class="vazio">Precisa de pelo menos 3 palavras diferentes.</p>'
        limpar_modelo()
        return

    cobertura = calcular_cobertura(palavras)
    a, b, r2 = calcular_a_b(cobertura)
    modelo = (a, b, r2, cobertura)
    n = len(cobertura)

    caixa.innerHTML = desenhar_modelo(cobertura, a, b)

    # cartões grandes com frases fáceis (só para x dentro do domínio do problema)
    cartoes = document.querySelector("#cartoesModelo")
    cartoes.innerHTML = ""
    itens = []
    for x in (5, 10):
        if x < n:
            itens.append((str(round(max(0, min(100, f(x, a, b))))) + "%", str(x) + " palavras cobrem isso da conversa"))
    itens.append((str(round(max(0, min(100, f(n, a, b))))) + "%", "todas as " + str(n) + " palavras juntas (segundo o modelo)"))
    for numero, frase in itens:
        c = document.createElement("div")
        c.style.cssText = "background:#e3ecfb;border-radius:12px;padding:14px;text-align:center;"
        c.innerHTML = '<strong style="display:block;font-size:34px;color:#1c5fd6;">' + numero + '</strong><span style="font-size:15px;color:#1a2b4c;">' + frase + '</span>'
        cartoes.appendChild(c)

    document.querySelector("#formula").innerText = "Fórmula: f(x) = " + formula_texto(a, b) + "   (R² = " + num(r2, 3) + ")"

    t = "f(x) = " + formula_texto(a, b) + "\n"
    t += "R² do ajuste: " + num(r2, 3) + "\n"
    t += "Pontos usados no ajuste: " + str(n) + " (uma palavra diferente por ponto)\n"
    t += "Método: mínimos quadrados, com u = log10(x) e y = % da conversa coberta"
    texto.innerText = t

    document.querySelector("#analise").innerText = montar_analise(a, b, r2, n, cobertura)
    document.querySelector("#contas").innerText = montar_contas(a, b, n)


def simular(evento=None):
    saida = document.querySelector("#simulacao")
    if modelo is None:
        saida.innerText = "Ainda não há modelo."
        return
    a, b, r2, cobertura = modelo
    n = len(cobertura)
    try:
        meta = float(document.querySelector("#metaPct").value)
    except ValueError:
        saida.innerText = "Digite um número entre 1 e 99."
        return
    if meta < 1 or meta > 99:
        saida.innerText = "Digite um número entre 1 e 99."
        return
    if b <= 0:
        saida.innerText = "O ajuste deu uma curva que não cresce, então a simulação não faz sentido com esses dados."
        return

    # isolando x na fórmula: x = 10^((meta - a) / b)
    x_exato = 10 ** ((meta - a) / b)
    x_modelo = max(1, math.ceil(x_exato))

    # nos dados reais: primeira posição que chega na meta
    x_real = None
    for i in range(len(cobertura)):
        if cobertura[i] >= meta:
            x_real = i + 1
            break

    t = "Para entender " + str(round(meta)) + "% da conversa, a fórmula diz que você precisa saber cerca de " + str(x_modelo) + " palavras.\n"
    t += "Conta: x = 10^((" + str(round(meta)) + " − " + par(a) + ") / " + par(b) + ") = " + num(x_exato, 2) + ", arredondado para cima: " + str(x_modelo) + ".\n"
    if x_modelo > n:
        t += "Atenção: a fórmula pede mais palavras do que existem nesta conversa (" + str(n) + "). Isso está fora do domínio do problema e é só extrapolação do modelo.\n"
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


def mostrar_aviso_exemplo():
    aviso = document.querySelector("#avisoExemplo")
    if window.localStorage.getItem(CHAVE_EXEMPLO) == "1":
        aviso.innerText = "Você está vendo uma conversa de EXEMPLO (dados inventados só para demonstrar o modelo). Clique em Zerar dados antes de usar a conversa de verdade."
    else:
        aviso.innerText = ""


def mostrar_vazio():
    msg = '<p class="vazio">Converse na tela de tradução primeiro (abra o site sempre pelo mesmo endereço do servidor) ou clique em Carregar conversa de exemplo.</p>'
    document.querySelector("#numeros").innerText = "Ainda não há mensagens."
    document.querySelector("#grafico").innerHTML = msg
    document.querySelector("#graficoModelo").innerHTML = msg
    document.querySelector("#simulacao").innerText = ""
    limpar_modelo()
    mostrar_aviso_exemplo()


def atualizar(evento=None):
    historico = carregar_historico()
    if len(historico) == 0:
        mostrar_vazio()
        return

    importantes = []   # palavras que entram no gráfico de barras
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
    texto += "Média por mensagem: " + num(media, 2) + "\n"
    texto += "Mediana: " + num(mediana, 1) + "\n"
    texto += "Desvio padrão: " + num(desvio, 2) + "\n"
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
    mostrar_aviso_exemplo()


def carregar_exemplo(evento=None):
    historico = carregar_historico()
    if len(historico) > 0:
        if not window.confirm("Isso vai substituir a conversa salva por uma conversa de exemplo. Continuar?"):
            return
    window.localStorage.setItem(CHAVE, json.dumps(EXEMPLO))
    window.localStorage.setItem(CHAVE_EXEMPLO, "1")
    atualizar()


def zerar(evento=None):
    window.localStorage.removeItem(CHAVE)
    window.localStorage.removeItem(CHAVE_EXEMPLO)
    mostrar_vazio()


atualizar()
document.querySelector("#statusPython").innerText = "Python pronto"