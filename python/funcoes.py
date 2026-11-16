# ======================================================
# PONTE LIBRAS - mesmas funções para rodar no terminal
# Como rodar:  python funcoes.py
# ======================================================


def funcao_primeiro_grau(a, b, x):
    return a * x + b


def raiz_primeiro_grau(a, b):
    if a == 0:
        return None
    return -b / a


def calcular_delta(a, b, c):
    return b ** 2 - 4 * a * c


def bhaskara(a, b, c):
    delta = calcular_delta(a, b, c)

    if delta < 0:
        return delta, None, None

    x1 = (-b + delta ** 0.5) / (2 * a)
    x2 = (-b - delta ** 0.5) / (2 * a)
    return delta, x1, x2


def menu():
    opcao = ""

    while opcao != "0":
        print("\n===== CALCULADORA PONTE LIBRAS =====")
        print("1 - Função do 1º grau")
        print("2 - Função do 2º grau")
        print("0 - Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            a = float(input("a: "))
            b = float(input("b: "))
            x = float(input("x: "))
            print("f(x) =", funcao_primeiro_grau(a, b, x))

            raiz = raiz_primeiro_grau(a, b)
            if raiz is None:
                print("Sem raiz (a = 0)")
            else:
                print("Raiz: x =", raiz)

        elif opcao == "2":
            a = float(input("a: "))
            b = float(input("b: "))
            c = float(input("c: "))

            if a == 0:
                print("a não pode ser 0 na função do 2º grau")
                continue

            delta, x1, x2 = bhaskara(a, b, c)
            print("Delta =", delta)

            if delta < 0:
                print("Não tem raízes reais")
            elif delta == 0:
                print("Uma raiz: x =", x1)
            else:
                print("x1 =", x1)
                print("x2 =", x2)

        elif opcao == "0":
            print("Tchau!")

        else:
            print("Opção inválida")


menu()
