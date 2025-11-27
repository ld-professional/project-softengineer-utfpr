// --- LÓGICA DO TEMA (DARK/LIGHT MODE) ---
const themeSwitch = document.getElementById('theme-switch');
let lightmode = localStorage.getItem('lightmode');

if (lightmode === 'active') document.body.classList.add('lightmode');

if (themeSwitch) {
    themeSwitch.addEventListener('click', () => {
        lightmode = localStorage.getItem('lightmode');
        if (lightmode !== 'active') {
            document.body.classList.add('lightmode');
            localStorage.setItem('lightmode', 'active');
        } else {
            document.body.classList.remove('lightmode');
            localStorage.setItem('lightmode', null);
        }
    });
}

// --- VARIÁVEL GLOBAL OBRIGATÓRIA ---
let idSelecionado = null;

// --- BOTÃO CONFIRMAR ---
const btnConfirmar = document.querySelector('.confirm-button');
if (btnConfirmar) {
    btnConfirmar.addEventListener('click', (e) => {
        e.preventDefault();

        if (idSelecionado) {
            // AJUSTE CRÍTICO DE URL:
            // Baseado no seu dashboard (/clientes/dashboard/), o caminho provável é este:
            window.location.href = `/clientes/agendamentos/escolher_barbeiro/?id_servico=${idSelecionado}`;
        } else {
            alert("Por favor, selecione um serviço primeiro!");
        }
    });
}

// --- A FUNÇÃO QUE O SEU HTML CHAMA ---
// Essa função TEM que existir para o onclick="selecionarServico(this)" funcionar
function selecionarServico(elementoClicado) {
    
    // 1. Limpa a cor de todos os outros
    const todosBlocos = document.querySelectorAll('.link-bloco');
    todosBlocos.forEach(bloco => bloco.classList.remove('selecionado'));

    // 2. Pinta o que você clicou
    elementoClicado.classList.add('selecionado');

    // 3. Salva o ID na memória
    idSelecionado = elementoClicado.getAttribute('data-id');
    console.log("Serviço Selecionado ID:", idSelecionado);

    // 4. Ativa o botão confirmar
    if (btnConfirmar) btnConfirmar.classList.add('ativo');
}

// --- CARROSSEL ---
const scrollContainer = document.getElementById('scroll-container');
const btnEsq = document.getElementById('btn-esq');
const btnDir = document.getElementById('btn-dir');

if (btnEsq && btnDir && scrollContainer) {
    btnEsq.addEventListener('click', () => {
        scrollContainer.scrollTo({ left: scrollContainer.scrollLeft - 200, behavior: 'smooth' });
    });
    btnDir.addEventListener('click', () => {
        scrollContainer.scrollTo({ left: scrollContainer.scrollLeft + 200, behavior: 'smooth' });
    });
}

// --- BOTÕES VOLTAR/INICIO ---
const btnVoltar = document.getElementById('voltar-dash-btn');
if (btnVoltar) btnVoltar.addEventListener('click', () => window.location.href = '/clientes/dashboard/');

const btnInicio = document.getElementById('inicio-dash-tbm-btn');
if (btnInicio) btnInicio.addEventListener('click', () => window.location.href = '/clientes/dashboard/');