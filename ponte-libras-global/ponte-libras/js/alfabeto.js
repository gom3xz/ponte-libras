// ======================================================
// PONTE LIBRAS - página do alfabeto
// As imagens das mãos ficam em img/alfabeto/a.png, b.png ...
// Se a imagem não existir, aparece só a letra.
// ======================================================

const letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

function criarGrade() {
    const grade = document.getElementById('grade');

    for (let i = 0; i < letras.length; i++) {
        const letra = letras[i];
        const cartao = document.createElement('button');
        cartao.className = 'cartao-letra';
        cartao.id = 'letra-' + letra;
        cartao.setAttribute('aria-label', 'Letra ' + letra);

        const imagem = document.createElement('img');
        imagem.src = 'img/alfabeto/' + letra.toLowerCase() + '.png';
        imagem.alt = 'Mão fazendo a letra ' + letra + ' em Libras';
        // se não achar a imagem, esconde
        imagem.onerror = function () {
            imagem.style.display = 'none';
        };

        const titulo = document.createElement('strong');
        titulo.innerText = letra;

        cartao.appendChild(imagem);
        cartao.appendChild(titulo);
        cartao.onclick = function () {
            destacar(letra);
        };

        grade.appendChild(cartao);
    }
}

// tira os acentos para achar a letra certa (Á vira A, Ç vira C)
function semAcento(texto) {
    return texto.normalize('NFD').replace(/[̀-ͯ]/g, '');
}

function destacar(letra) {
    // apaga o destaque de todas
    for (let i = 0; i < letras.length; i++) {
        document.getElementById('letra-' + letras[i]).classList.remove('destaque');
    }

    const cartao = document.getElementById('letra-' + letra);
    if (!cartao) {
        return;
    }
    cartao.classList.add('destaque');

    // painel grande: letra + sinal em Libras
    const imagem = document.getElementById('painelImg');
    imagem.style.display = 'block';
    imagem.onerror = function () { imagem.style.display = 'none'; };
    imagem.src = 'img/alfabeto/' + letra.toLowerCase() + '.png';
    imagem.alt = 'Mão fazendo a letra ' + letra + ' em Libras';

    document.getElementById('painelLetra').innerText = letra;
    document.getElementById('painelTexto').innerText = 'Letra ' + letra + ' em Libras';
    document.getElementById('letraAtual').innerText = 'Letra: ' + letra;
}

function soletrar() {
    let palavra = document.getElementById('palavraSoletrar').value;
    palavra = semAcento(palavra).toUpperCase().trim();

    if (palavra === '') {
        alert('Digite uma palavra.');
        return;
    }

    // mostra uma letra a cada 1,2 segundo
    for (let i = 0; i < palavra.length; i++) {
        setTimeout(function () {
            const letra = palavra[i];

            if (letras.includes(letra)) {
                destacar(letra);
            } else {
                document.getElementById('letraAtual').innerText = '(espaço)';
            }
        }, i * 1200);
    }
}

criarGrade();
