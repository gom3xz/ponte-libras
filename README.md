# Ponte Libras

Site para ajudar pessoas que não conseguem se comunicar verbalmente a conversar com quem ouve.

## O que o site faz

- **Tradução ao vivo (index.html)**
  - Quem não fala toca em frases prontas ou soletra, e o site **fala em voz alta**.
  - Quem ouve fala no microfone (ou digita) e o texto aparece; o avatar **VLibras** traduz para Libras.
  - **Câmera → Legenda:** a pessoa faz o sinal parado na câmera, o modelo (Teachable Machine) identifica e monta a legenda. Dá para mandar a legenda para a conversa e falar em voz alta.
- **Alfabeto (alfabeto.html)**: clique em uma letra e veja a letra grande com o sinal em Libras. Também dá para digitar uma palavra e ver letra por letra.
- **Estatísticas (estatisticas.html)**: Python (PyScript) lê a conversa e calcula média, mediana, desvio padrão, porcentagens e desenha o gráfico das palavras mais usadas.

## Tecnologias

| Parte | Arquivo |
|---|---|
| HTML | index.html, alfabeto.html, estatisticas.html |
| CSS | css/style.css |
| JavaScript | js/script.js, js/alfabeto.js, js/camera.js |
| Python | python/estatisticas.py (roda no navegador com PyScript) |
| IA da câmera | Teachable Machine (TensorFlow.js) |

## Configurar a câmera (obrigatório)

1. Treine um modelo de imagem em teachablemachine.withgoogle.com (uma classe por sinal + uma classe `Nada`, 100+ fotos cada, de várias pessoas).
2. Exporte → TensorFlow.js → Upload → copie o link.
3. Cole o link em `URL_MODELO` no topo de `js/camera.js`.

Limite: reconhece **sinais parados** (letras sem movimento e algumas palavras). Sinais com movimento, como J e Z, não funcionam nesta versão.

## Imagens do alfabeto

Coloque as imagens dos sinais em `img/alfabeto/` com o nome da letra em minúsculo: `a.png`, `b.png`, ... `z.png`.
Sem a imagem, o site mostra só a letra. Cite a fonte das imagens aqui se não forem fotos do grupo.

## Como abrir

1. Abra a pasta no VS Code e use **Live Server** no index.html (câmera e microfone só funcionam em localhost ou https).
2. Precisa de internet para VLibras, PyScript e Teachable Machine. Use o Google Chrome.

## Equipe

| Pessoa | Área |
|---|---|
| Caio | HTML e CSS |
| Felipe | JavaScript (alfabeto, histórico da conversa) |
| Gomes | JavaScript (câmera e legenda) |
| Lucas | Python (estatísticas) |
| Mahdi | Matemática (cálculos e testes de acerto) |

## Publicar no GitHub Pages

```
git init
git add .
git commit -m "Ponte Libras"
git remote add origin LINK_DO_REPOSITORIO
git push -u origin main
```
Depois: Settings → Pages → escolher a branch main.
