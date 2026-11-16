const API_SERVIDOR = 'http://127.0.0.1:5000';
const FRAMES_PARA_CONFIRMAR = 12;
const INTERVALO_POLL_MS = 200;

let cameraLigada = false;
let pollTimer = null;
let legenda = '';
let ultimoSinal = '';
let contagem = 0;
let sinalConfirmadoNaSessao = false;

async function alternarCamera() {
    if (cameraLigada) {
        await desligarCamera();
    } else {
        await ligarCamera();
    }
}

async function ligarCamera() {
    const botao = document.getElementById('botaoCamera');
    botao.innerText = 'Carregando...';

    try {
        const resp = await fetch(`${API_SERVIDOR}/start`, { method: 'POST' });
        if (!resp.ok) {
            throw new Error('Falha ao iniciar câmera no servidor');
        }

        const area = document.getElementById('areaCamera');
        area.innerHTML = '';

        const img = document.createElement('img');
        img.id = 'feedVideoLibras';
        img.alt = 'Câmera com detecção de Libras';
        img.src = `${API_SERVIDOR}/video_feed?t=${Date.now()}`;
        area.appendChild(img);
    } catch (erro) {
        alert('Não consegui conectar ao servidor Python em http://127.0.0.1:5000. Confira se o servidor_libras.py está rodando.');
        botao.innerText = '📷 Ligar câmera';
        return;
    }

    cameraLigada = true;
    botao.innerText = '⏹ Desligar câmera';
    botao.classList.add('gravando');
    document.getElementById('statusCamera').innerText = '● AO VIVO';

    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(consultarPredicao, INTERVALO_POLL_MS);
}

async function desligarCamera() {
    cameraLigada = false;

    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }

    try {
        await fetch(`${API_SERVIDOR}/stop`, { method: 'POST' });
    } catch (_) {}

    document.getElementById('areaCamera').innerHTML = '<p class="camera-aviso">A câmera aparece aqui.</p>';

    const botao = document.getElementById('botaoCamera');
    botao.innerText = '📷 Ligar câmera';
    botao.classList.remove('gravando');
    document.getElementById('statusCamera').innerText = '● DESLIGADA';
    document.getElementById('palpite').innerText = 'Palpite atual: -';

    ultimoSinal = '';
    contagem = 0;
    sinalConfirmadoNaSessao = false;
}

async function consultarPredicao() {
    if (!cameraLigada) return;

    try {
        const resp = await fetch(`${API_SERVIDOR}/prediction`);
        if (!resp.ok) return;
        const dados = await resp.json();
        const label = (dados.label || '').trim();

        const palpiteEl = document.getElementById('palpite');

        if (!label || label === 'Nenhum sinal' || label === 'Incerto') {
            palpiteEl.innerText = 'Palpite atual: -';
            ultimoSinal = '';
            contagem = 0;
            sinalConfirmadoNaSessao = false;
            return;
        }

        palpiteEl.innerText = 'Palpite atual: ' + label;

        if (label === ultimoSinal) {
            contagem++;
        } else {
            ultimoSinal = label;
            contagem = 1;
            sinalConfirmadoNaSessao = false;
        }

        if (contagem === FRAMES_PARA_CONFIRMAR && !sinalConfirmadoNaSessao) {
            adicionarNaLegenda(label);
            sinalConfirmadoNaSessao = true;
        }
    } catch (_) {}
}

function adicionarNaLegenda(sinal) {
    if (sinal.length === 1) {
        legenda += sinal;
    } else {
        legenda += ' ' + sinal + ' ';
    }
    mostrarLegenda();
}

function mostrarLegenda() {
    const campo = document.getElementById('legenda');
    campo.innerText = legenda.trim() === '' ? 'A legenda aparece aqui.' : legenda;
}

function espacoLegenda() {
    if (legenda !== '' && legenda[legenda.length - 1] !== ' ') {
        legenda += ' ';
        mostrarLegenda();
    }
}

function apagarLegenda() {
    legenda = legenda.slice(0, -1);
    mostrarLegenda();
}

function falarLegenda() {
    const texto = legenda.replace(/\s+/g, ' ').trim();
    if (!texto) {
        alert('A legenda está vazia.');
        return;
    }
    mensagemDaPessoaQueSinaliza(texto);
    legenda = '';
    mostrarLegenda();
}

async function capturarAmostraLibras() {
    const campo = document.getElementById('sinalTreino');
    const sinal = campo ? campo.value.trim().toUpperCase() : '';
    if (!sinal) {
        alert('Digite a letra ou sinal antes de capturar.');
        return;
    }
    try {
        const resp = await fetch(`${API_SERVIDOR}/train/sample`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label: sinal })
        });
        const dados = await resp.json();
        const info = document.getElementById('infoTreinoLibras');
        if (info && dados.summary) info.innerText = dados.summary;
    } catch (_) {
        alert('Não foi possível capturar amostra no servidor.');
    }
}

async function treinarLibras() {
    try {
        const resp = await fetch(`${API_SERVIDOR}/train/fit`, { method: 'POST' });
        const dados = await resp.json();
        const info = document.getElementById('infoTreinoLibras');
        if (info && dados.message) info.innerText = dados.message;
    } catch (_) {
        alert('Não foi possível treinar o modelo no servidor.');
    }
}

async function limparAmostrasLibras() {
    try {
        const resp = await fetch(`${API_SERVIDOR}/train/clear`, { method: 'POST' });
        const dados = await resp.json();
        const info = document.getElementById('infoTreinoLibras');
        if (info && dados.message) info.innerText = dados.message;
    } catch (_) {}
}