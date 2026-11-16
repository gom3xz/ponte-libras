// ======================================================
// PONTE LIBRAS - script da tela de tradução ao vivo
// ======================================================

// ---------- VARIÁVEIS ----------

// frases que a pessoa que não fala pode usar com 1 toque
const frases = [
    { emoji: '👋', texto: 'Olá, tudo bem?' },
    { emoji: '✅', texto: 'Sim' },
    { emoji: '❌', texto: 'Não' },
    { emoji: '🙏', texto: 'Obrigado' },
    { emoji: '🤕', texto: 'Estou com dor' },
    { emoji: '💧', texto: 'Quero água' },
    { emoji: '🍽️', texto: 'Estou com fome' },
    { emoji: '🚻', texto: 'Preciso ir ao banheiro' },
    { emoji: '🆘', texto: 'Preciso de ajuda' },
    { emoji: '🔁', texto: 'Pode repetir, por favor?' }
];

const alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

let palavra = '';          // palavra que está sendo soletrada
let totalMensagens = 0;
let totalSinaliza = 0;
let totalOuvinte = 0;
let totalPalavras = 0;
let ouvindo = false;


// ---------- MONTAR A TELA ----------

// cria os botões de frases rápidas usando for
function criarFrases() {
    const caixa = document.getElementById('frases');

    for (let i = 0; i < frases.length; i++) {
        const botao = document.createElement('button');
        botao.className = 'frase';
        botao.innerHTML = '<span>' + frases[i].emoji + '</span>' + frases[i].texto;

        botao.onclick = function () {
            mensagemDaPessoaQueSinaliza(frases[i].texto);
        };

        caixa.appendChild(botao);
    }
}

// cria os botões de A até Z
function criarLetras() {
    const caixa = document.getElementById('letras');

    for (let i = 0; i < alfabeto.length; i++) {
        const letra = alfabeto[i];
        const botao = document.createElement('button');
        botao.className = 'letra';
        botao.innerText = letra;
        botao.setAttribute('aria-label', 'Letra ' + letra);

        botao.onclick = function () {
            adicionarLetra(letra);
        };

        caixa.appendChild(botao);
    }
}


// ---------- SOLETRAR ----------

function adicionarLetra(letra) {
    palavra = palavra + letra;
    mostrarPalavra();
}

function adicionarEspaco() {
    // não deixa começar com espaço nem colocar dois seguidos
    if (palavra !== '' && palavra[palavra.length - 1] !== ' ') {
        palavra = palavra + ' ';
        mostrarPalavra();
    }
}

function apagarLetra() {
    palavra = palavra.slice(0, -1);
    mostrarPalavra();
}

function mostrarPalavra() {
    const campo = document.getElementById('palavra');

    if (palavra === '') {
        campo.innerText = 'Toque nas letras...';
    } else {
        campo.innerText = palavra;
    }
}

function enviarPalavra() {
    if (palavra.trim() === '') {
        alert('Soletre alguma palavra antes de falar.');
        return;
    }

    mensagemDaPessoaQueSinaliza(palavra.trim());
    palavra = '';
    mostrarPalavra();
}


// ---------- VOZ ----------

// o navegador lê o texto em voz alta (português do Brasil)
function falar(texto) {
    if (!('speechSynthesis' in window)) {
        console.log('Este navegador não fala em voz alta.');
        return;
    }

    window.speechSynthesis.cancel();
    const fala = new SpeechSynthesisUtterance(texto);
    fala.lang = 'pt-BR';
    fala.rate = 0.9;
    window.speechSynthesis.speak(fala);
}

// o navegador escuta o microfone e transforma a fala em texto
function ouvir() {
    const Reconhecimento = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Reconhecimento) {
        alert('Seu navegador não reconhece voz. Use o Google Chrome ou digite o texto.');
        return;
    }

    if (ouvindo) {
        return;
    }

    const microfone = new Reconhecimento();
    microfone.lang = 'pt-BR';

    microfone.onstart = function () {
        ouvindo = true;
        mudarMicrofone(true);
    };

    microfone.onresult = function (evento) {
        const texto = evento.results[0][0].transcript;
        mensagemDoOuvinte(texto);
    };

    microfone.onerror = function () {
        alert('Não consegui ouvir. Verifique se o microfone está liberado.');
    };

    microfone.onend = function () {
        ouvindo = false;
        mudarMicrofone(false);
    };

    microfone.start();
}

function mudarMicrofone(ligado) {
    const botao = document.getElementById('botaoMicrofone');
    const onda = document.getElementById('onda');

    if (ligado) {
        botao.innerText = '🔴 Ouvindo...';
        botao.classList.add('gravando');
        onda.classList.add('mexendo');
    } else {
        botao.innerText = '🎤 Começar a ouvir';
        botao.classList.remove('gravando');
        onda.classList.remove('mexendo');
    }
}

function enviarTextoOuvinte() {
    const campo = document.getElementById('textoOuvinte');
    const texto = campo.value.trim();

    if (texto === '') {
        alert('Digite alguma coisa antes de enviar.');
        return;
    }

    mensagemDoOuvinte(texto);
    campo.value = '';
}


// ---------- CONVERSA ----------

function mensagemDaPessoaQueSinaliza(texto) {
    adicionarMensagem('sinaliza', texto);
    falar(texto);   // a frase vira voz para o ouvinte escutar
}

function mensagemDoOuvinte(texto) {
    adicionarMensagem('ouvinte', texto);
    document.getElementById('ultimoTextoOuvinte').innerText = texto;
}

function adicionarMensagem(quem, texto) {
    const lista = document.getElementById('mensagens');

    // tira o aviso "A conversa vai aparecer aqui"
    if (totalMensagens === 0) {
        lista.innerHTML = '';
    }

    let nome = '';
    let classe = '';

    switch (quem) {
        case 'sinaliza':
            nome = '🤟 Pessoa que sinaliza';
            classe = 'msg-sinaliza';
            totalSinaliza++;
            break;
        case 'ouvinte':
            nome = '🗣️ Pessoa ouvinte';
            classe = 'msg-ouvinte';
            totalOuvinte++;
            break;
        default:
            nome = 'Desconhecido';
    }

    const mensagem = document.createElement('div');
    mensagem.className = 'mensagem ' + classe;
    mensagem.innerHTML =
        '<div class="msg-topo"><b>' + nome + '</b> <small>' + horaAgora() + '</small></div>' +
        '<p></p>' +
        '<button class="ouvir-de-novo" aria-label="Ouvir de novo">🔊</button>';

    // innerText no texto para ninguém conseguir colocar HTML na conversa
    mensagem.querySelector('p').innerText = texto;
    mensagem.querySelector('button').onclick = function () {
        falar(texto);
    };

    lista.appendChild(mensagem);
    lista.scrollTop = lista.scrollHeight;

    totalMensagens++;
    totalPalavras = totalPalavras + contarPalavras(texto);
    atualizarNumeros();
}

// conta as palavras de um texto usando while
function contarPalavras(texto) {
    const partes = texto.trim().split(' ');
    let contador = 0;
    let i = 0;

    while (i < partes.length) {
        if (partes[i] !== '') {
            contador++;
        }
        i++;
    }

    return contador;
}

function horaAgora() {
    const agora = new Date();
    let hora = agora.getHours();
    let minuto = agora.getMinutes();

    if (hora < 10) hora = '0' + hora;
    if (minuto < 10) minuto = '0' + minuto;

    return hora + ':' + minuto;
}

function atualizarNumeros() {
    document.getElementById('totalMensagens').innerText = totalMensagens;
    document.getElementById('totalSinaliza').innerText = totalSinaliza;
    document.getElementById('totalOuvinte').innerText = totalOuvinte;
    document.getElementById('totalPalavras').innerText = totalPalavras;
}

function limparConversa() {
    if (totalMensagens === 0) {
        return;
    }

    if (confirm('Quer mesmo apagar a conversa?')) {
        totalMensagens = 0;
        totalSinaliza = 0;
        totalOuvinte = 0;
        totalPalavras = 0;
        document.getElementById('mensagens').innerHTML = '<p class="vazio">A conversa vai aparecer aqui.</p>';
        atualizarNumeros();
    }
}


// ---------- INÍCIO ----------

criarFrases();
criarLetras();

// enviar com a tecla Enter no campo de texto
document.getElementById('textoOuvinte').addEventListener('keydown', function (evento) {
    if (evento.key === 'Enter') {
        enviarTextoOuvinte();
    }
});

console.log('Ponte Libras carregado!');
