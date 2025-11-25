const themeSwitch = document.getElementById('theme-switch');

// pega o estado atual do modo (se esstá claro ou escuro)
let lightmode = localStorage.getItem('lightmode');

// darkmode
const enableLightMode = () => {
    document.body.classList.add('lightmode');
    localStorage.setItem('lightmode', 'active');
};
const disableLightMode = () => {
    document.body.classList.remove('lightmode');
    localStorage.setItem('lightmode', null);
};

if (lightmode === 'active') {
    enableLightMode();
}

themeSwitch.addEventListener('click', () => {
    lightmode = localStorage.getItem('lightmode');
    if (lightmode !== 'active') {
        enableLightMode();
    } else {
        disableLightMode();
    }
});

const blocos = document.querySelectorAll('.link-bloco');
let blocoSelecionado = null;

blocos.forEach(bloco => {
    bloco.addEventListener('click', () => {

        // Remove seleção anterior
        blocos.forEach(b => b.classList.remove('selecionado'));

        // Adiciona seleção ao clicado
        bloco.classList.add('selecionado');

        // Pega o título do serviço (conteúdo do <h2>)
        blocoSelecionado = bloco.querySelector('h2').textContent;
    });
});


const btnVoltar = document.getElementById('voltar-dash-btn');

if (btnVoltar) {
    btnVoltar.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/dashboard/'; 
    });
}

const btnInicio = document.getElementById('inicio-dash-tbm-btn');

if (btnInicio) {
    btnInicio.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/dashboard/'; 
    });
}







// ==========================================
// 1. LÓGICA DE SELEÇÃO DE SERVIÇO (O 'this')
// ==========================================

// Variável que guarda o ID na memória
let idSelecionado = null;

// Função chamada pelo onclick="selecionarServico(this)" no HTML
function selecionarServico(elementoClicado) {
    
    // Remove a classe 'selecionado' de todos (limpa seleção anterior)
    const todosBlocos = document.querySelectorAll('.link-bloco');
    todosBlocos.forEach(bloco => {
        bloco.classList.remove('selecionado');
    });

    // Adiciona a classe 'selecionado' na div que foi clicada (o 'this')
    elementoClicado.classList.add('selecionado');

    // Pega o ID guardado no atributo data-id
    idSelecionado = elementoClicado.getAttribute('data-id');
    
    console.log("Serviço selecionado ID:", idSelecionado);
}


// ==========================================
// 2. LÓGICA DO CARROSSEL (SUA VERSÃO)
// ==========================================
const scrollContainer = document.getElementById('scroll-container');
const btnEsq = document.getElementById('btn-esq');
const btnDir = document.getElementById('btn-dir');

// Valor que vai rolar a cada clique
const scrollAmount = 200; 

if (btnEsq && btnDir && scrollContainer) {
    
    btnEsq.addEventListener('click', () => {
        scrollContainer.scrollTo({
            left: scrollContainer.scrollLeft - scrollAmount,
            behavior: 'smooth'
        });
    });

    btnDir.addEventListener('click', () => {
        scrollContainer.scrollTo({
            left: scrollContainer.scrollLeft + scrollAmount,
            behavior: 'smooth'
        });
    });
}


// ==========================================
// 3. BOTÃO CONFIRMAR E REDIRECIONAR
// ==========================================
const btnConfirmar = document.querySelector('.confirm-button');

if (btnConfirmar) {
    btnConfirmar.addEventListener('click', (e) => {
        e.preventDefault(); 

        if (idSelecionado) {
            // Se o usuário escolheu algo, manda para a próxima tela com o ID
            // ATENÇÃO: Verifique se essa URL bate com o seu urls.py
            window.location.href = `/agendamento/horarios/?id_servico=${idSelecionado}`;
        } else {
            alert("Por favor, selecione um serviço primeiro!");
        }
    });
}