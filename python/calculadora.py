# ======================================================
# PONTE LIBRAS - Calculadora em Python (roda no site com PyScript)
# Funções de 1º grau e 2º grau
# ======================================================

from pyscript import document


# ---------- FUNÇÕES DE MATEMÁTICA ----------

def funcao_primeiro_grau(a, b, x):
    # f(x) = a*x + b
    return a * x + b


def raiz_primeiro_grau(a, b):
    # a*x + b = 0  ->  x = -b / a
    if a == 0:
        return None
    return -b / a


def calcular_delta(a, b, c):
    # delta = b² - 4*a*c
    return b ** 2 - 4 * a * c


def bhaskara(a, b, c):
    delta = calcular_delta(a, b, c)

    if delta < 0:
        return delta, None, None

    x1 = (-b + delta ** 0.5) / (2 * a)
    x2 = (-b - delta ** 0.5) / (2 * a)
    return delta, x1, x2


def formatar(numero):
    # mostra 3 em vez de 3.0, e no máximo 2 casas
    if numero == int(numero):
        return str(int(numero))
    return str(round(numero, 2))


def pegar_numero(id_do_campo):
    texto = document.querySelector("#" + id_do_campo).value
    if texto == "":
        return None
    return float(texto)


# ---------- LIGANDO COM OS BOTÕES DO SITE ----------

def calcular_primeiro_grau(evento):
    a = pegar_numero("a1")
    b = pegar_numero("b1")
    x = pegar_numero("x1")
    saida = document.querySelector("#resultado1")

    if a is None or b is None or x is None:
        saida.innerText = "Preencha a, b e x."
        return

    resultado = funcao_primeiro_grau(a, b, x)
    raiz = raiz_primeiro_grau(a, b)

    texto = "f(" + formatar(x) + ") = " + formatar(a) + "·" + formatar(x) + " + " + formatar(b)
    texto = texto + " = " + formatar(resultado) + "\n"

    if a > 0:
        texto = texto + "A função é crescente (a > 0)\n"
    elif a < 0:
        texto = texto + "A função é decrescente (a < 0)\n"
    else:
        texto = texto + "Com a = 0 não é função do 1º grau\n"

    if raiz is not None:
        texto = texto + "Raiz (onde f(x) = 0): x = " + formatar(raiz) + "\n"

    # tabelinha de valores com for
    texto = texto + "\nTabela:\n"
    for valor in range(-2, 3):
        texto = texto + "x = " + str(valor) + "  ->  f(x) = " + formatar(funcao_primeiro_grau(a, b, valor)) + "\n"

    saida.innerText = texto


def calcular_segundo_grau(evento):
    a = pegar_numero("a2")
    b = pegar_numero("b2")
    c = pegar_numero("c2")
    saida = document.querySelector("#resultado2")

    if a is None or b is None or c is None:
        saida.innerText = "Preencha a, b e c."
        return

    if a == 0:
        saida.innerText = "Se a = 0 não é função do 2º grau. Use a de 1º grau."
        return

    delta, x1, x2 = bhaskara(a, b, c)

    texto = "Δ = b² - 4·a·c = " + formatar(delta) + "\n"

    if delta < 0:
        texto = texto + "Δ < 0: não tem raízes reais\n"
    elif delta == 0:
        texto = texto + "Δ = 0: uma raiz só\n"
        texto = texto + "x = " + formatar(x1) + "\n"
    else:
        texto = texto + "Δ > 0: duas raízes diferentes\n"
        texto = texto + "x1 = " + formatar(x1) + "\n"
        texto = texto + "x2 = " + formatar(x2) + "\n"

    # vértice da parábola
    xv = -b / (2 * a)
    yv = -delta / (4 * a)
    texto = texto + "Vértice: (" + formatar(xv) + ", " + formatar(yv) + ")\n"

    if a > 0:
        texto = texto + "Concavidade para cima (a > 0)"
    else:
        texto = texto + "Concavidade para baixo (a < 0)"

    saida.innerText = texto


# avisa na tela que o Python já carregou
document.querySelector("#statusPython").innerText = "Python pronto ✔"
