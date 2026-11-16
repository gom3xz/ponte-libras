# Ponte Libras 🤟

Site para ajudar pessoas que não conseguem se comunicar verbalmente a conversar com quem ouve.

## O que o site faz

- **Tradução ao vivo (index.html)**
  - A pessoa que não fala toca em frases prontas ou soletra letra por letra, e o site **fala em voz alta**.
  - A pessoa ouvinte fala no microfone (ou digita) e o texto aparece na tela.
  - O avatar **VLibras** (do governo federal) traduz o texto da página para Libras. É só clicar no botão azul no canto da tela e depois no texto.
  - A conversa fica registrada embaixo, com contadores de mensagens e palavras.
- **Alfabeto (alfabeto.html)**: digita uma palavra e o site mostra letra por letra.
- **Calculadora Python (calculadora.html)**: funções de 1º e 2º grau (Bhaskara) feitas em Python rodando no navegador com PyScript.

## Tecnologias

| Parte | Arquivo |
|---|---|
| HTML | index.html, alfabeto.html, calculadora.html |
| CSS | css/style.css |
| JavaScript | js/script.js, js/alfabeto.js |
| Python | python/calculadora.py (no site), python/funcoes.py (no terminal) |

## Como abrir

1. Abra a pasta no VS Code.
2. Use a extensão **Live Server** (botão direito no index.html → Open with Live Server).
   - Precisa de internet para o VLibras e o Python (PyScript) carregarem.
   - O microfone funciona melhor no **Google Chrome**.
3. Para o Python no terminal: `python python/funcoes.py`

## Imagens do alfabeto

Coloque as fotos das mãos em `img/alfabeto/` com o nome da letra em minúsculo: `a.png`, `b.png`, ...
Se a imagem não existir, o site mostra só a letra.

## Publicar no GitHub Pages

```
git init
git add .
git commit -m "primeira versão do Ponte Libras"
git remote add origin LINK_DO_REPOSITORIO
git push -u origin main
```
Depois: Settings → Pages → escolher a branch main.
