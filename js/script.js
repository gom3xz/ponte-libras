const frases = [
    { texto: 'Olá, tudo bem?' },
    { texto: 'Sim' },
    { texto: 'Não' },
    { texto: 'Obrigado' },
    { texto: 'Estou com dor' },
    { texto: 'Quero água' },
    { texto: 'Estou com fome' },
    { texto: 'Preciso ir ao banheiro' },
    { texto: 'Preciso de ajuda' },
    { texto: 'Pode repetir, por favor?' }
];

const alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

let palavra = '';
let totalMensagens = 0;
let totalSinaliza = 0;
let totalOuvinte = 0;
let totalPalavras = 0;
let ouvindo = false;
let reconhecimento = null;

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let historico = [];
try {
    historico = JSON.parse(localStorage.getItem('ponteLibrasHistorico') || '[]');
} catch (erro) {
    historico = [];
}

function salvarHistorico() {
    try {
        localStorage.setItem('ponteLibrasHistorico', JSON.stringify(historico));
    } catch (erro) {
        console.log('Não foi possível salvar o histórico.');
    }
}

function criarFrases() {
    const caixa = document.getElementById('frases');

    for (let i = 0; i < frases.length; i++) {
        const botao = document.createElement('button');
        botao.className = 'frase';
        botao.innerText = frases[i].texto;

        botao.onclick = function () {
            mensagemDaPessoaQueSinaliza(frases[i].texto);
        };

        caixa.appendChild(botao);
    }
}

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

function adicionarLetra(letra) {
    palavra = palavra + letra;
    mostrarPalavra();
}

function adicionarEspaco() {
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

function ouvir() {
    if (!SpeechRecognition) {
        alert('Seu navegador não suporta reconhecimento de voz. Use o Google Chrome ou Edge.');
        return;
    }

    if (ouvindo && reconhecimento) {
        reconhecimento.stop();
        return;
    }

    reconhecimento = new SpeechRecognition();
    reconhecimento.lang = 'pt-BR';
    reconhecimento.interimResults = true;
    reconhecimento.continuous = false;

    const saida = document.getElementById('ultimoTextoOuvinte');

    reconhecimento.onstart = function () {
        ouvindo = true;
        mudarMicrofone(true);
        if (saida) {
            saida.innerText = 'Ouvindo...';
        }
    };

    reconhecimento.onresult = function (evento) {
        let transcricao = '';
        let finalizou = false;

        for (let i = evento.resultIndex; i < evento.results.length; i++) {
            transcricao += evento.results[i][0].transcript;
            if (evento.results[i].isFinal) {
                finalizou = true;
            }
        }

        const textoLimpo = transcricao.trim();
        if (saida && textoLimpo) {
            saida.innerText = textoLimpo;
        }

        if (finalizou && textoLimpo) {
            mensagemDoOuvinte(textoLimpo);
        }
    };

    reconhecimento.onerror = function (evento) {
        if (saida) {
            saida.innerText = evento.error === 'not-allowed'
                ? 'Permissão do microfone negada no navegador.'
                : 'Não consegui ouvir. Verifique se o microfone está liberado.';
        }
    };

    reconhecimento.onend = function () {
        ouvindo = false;
        mudarMicrofone(false);
    };

    reconhecimento.start();
}

function mudarMicrofone(ligado) {
    const botao = document.getElementById('botaoMicrofone');
    const onda = document.getElementById('onda');

    if (ligado) {
        botao.innerText = 'Parar de ouvir';
        botao.classList.add('gravando');
        onda.classList.add('mexendo');
    } else {
        botao.innerText = 'Iniciar reconhecimento de voz';
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

function mensagemDaPessoaQueSinaliza(texto) {
    adicionarMensagem('sinaliza', texto);
    falar(texto);
}

function mensagemDoOuvinte(texto) {
    adicionarMensagem('ouvinte', texto);
    document.getElementById('ultimoTextoOuvinte').innerText = texto;
}

function adicionarMensagem(quem, texto) {
    const lista = document.getElementById('mensagens');

    if (totalMensagens === 0) {
        lista.innerHTML = '';
    }

    let nome = '';
    let classe = '';

    switch (quem) {
        case 'sinaliza':
            nome = 'Pessoa que sinaliza';
            classe = 'msg-sinaliza';
            totalSinaliza++;
            break;
        case 'ouvinte':
            nome = 'Pessoa ouvinte';
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
        '<button class="ouvir-de-novo" aria-label="Ouvir a mensagem de novo">Ouvir</button>';

    mensagem.querySelector('p').innerText = texto;
    mensagem.querySelector('button').onclick = function () {
        falar(texto);
    };

    lista.appendChild(mensagem);
    lista.scrollTop = lista.scrollHeight;

    historico.push({ quem: quem, texto: texto });
    salvarHistorico();

    totalMensagens++;
    totalPalavras = totalPalavras + contarPalavras(texto);
    atualizarNumeros();
}

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
        historico = [];
        salvarHistorico();
        document.getElementById('mensagens').innerHTML = '<p class="vazio">A conversa vai aparecer aqui.</p>';
        atualizarNumeros();
    }
}

criarFrases();
criarLetras();

document.getElementById('textoOuvinte').addEventListener('keydown', function (evento) {
    if (evento.key === 'Enter') {
        enviarTextoOuvinte();
    }
});

console.log('Ponte Libras carregado!');