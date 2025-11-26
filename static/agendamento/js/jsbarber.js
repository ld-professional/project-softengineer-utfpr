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

// --- BOTÕES DE NAVEGAÇÃO ---
const btnVoltar = document.getElementById('voltar-dash-btn');
if (btnVoltar) {
    btnVoltar.addEventListener('click', function() {
        // Usa o histórico para voltar mantendo dados ou vai para a seleção de serviço
        window.location.href = '/clientes/agendamentos/escolher_servico/';  
    });
}

const btnInicio = document.getElementById('inicio-dash-tbm-btn');
if (btnInicio) {
    btnInicio.addEventListener('click', function() {
        window.location.href = '/clientes/dashboard/'; 
    });
}

// ==========================================
// LÓGICA DO CARROSSEL DINÂMICO
// ==========================================

const slides = document.querySelectorAll(".slide");
const nomeBarbeiroDisplay = document.getElementById("nomeBarbeiro");
let index = 0;

// Função que atualiza a imagem e lê os dados do HTML
function atualizarSlide(novoIndex) {
    // 1. Esconde o slide atual
    slides[index].classList.remove("ativo");
    
    // 2. Calcula o novo índice (lógica circular)
    index = novoIndex;
    if (index >= slides.length) index = 0;
    if (index < 0) index = slides.length - 1;

    // 3. Mostra o novo slide
    const slideAtual = slides[index];
    slideAtual.classList.add("ativo");

    // 4. MÁGICA AQUI: Lê o nome que o Django escreveu no atributo data-nome
    const nomeReal = slideAtual.getAttribute('data-nome');
    
    // Atualiza o texto na tela
    if (nomeBarbeiroDisplay) {
        nomeBarbeiroDisplay.textContent = nomeReal;
    }
}

// Eventos das Setas
const nextBtn = document.getElementById("next");
const prevBtn = document.getElementById("prev");

if (nextBtn && prevBtn && slides.length > 0) {
    nextBtn.addEventListener("click", () => {
        atualizarSlide(index + 1);
    });

    prevBtn.addEventListener("click", () => {
        atualizarSlide(index - 1);
    });
}

// Gera estrelas baseado na nota
function gerarEstrelas(nota) {
    return "★★★★★".slice(0, nota) + "☆☆☆☆☆".slice(nota);
}

// notas por barbeiro
const notaBarbeiros = {
    "vini_jr": 5,
    "rezende": 1,
    "ze_felipe": 1
};

// Função que atualiza a imagem e lê os dados do HTML
function atualizarSlide(novoIndex) {
    slides[index].classList.remove("ativo");
    
    index = novoIndex;
    if (index >= slides.length) index = 0;
    if (index < 0) index = slides.length - 1;

    const slideAtual = slides[index];
    slideAtual.classList.add("ativo");

    const nomeReal = slideAtual.getAttribute('data-nome');

    if (nomeBarbeiroDisplay) {
        nomeBarbeiroDisplay.textContent = nomeReal;
    }

    const ratingDisplay = document.getElementById("ratingBarbeiro");
    const nota = notaBarbeiros[nomeReal] ?? 0;
    ratingDisplay.textContent = gerarEstrelas(nota);
}


// ==========================================
// LÓGICA DO BOTÃO CONFIRMAR
// ==========================================
const btnConfirmar = document.getElementById('confirmButton');
const inputServico = document.getElementById('id-servico-selecionado');

if (btnConfirmar) {
    btnConfirmar.addEventListener('click', (e) => {
        e.preventDefault();

        // 1. Pega o slide que está visível agora
        const slideAtivo = document.querySelector('.slide.ativo');
        
        if (!slideAtivo) {
            alert("Nenhum barbeiro disponível!");
            return;
        }

        // 2. Pega os IDs (Barbeiro da imagem ativa + Serviço do input hidden)
        const idBarbeiro = slideAtivo.getAttribute('data-id');
        const idServico = inputServico ? inputServico.value : null;

        if (idBarbeiro && idServico) {
            // 3. Redireciona para escolher o dia
            // ATENÇÃO: Certifique-se que 'escolher_dia' está descomentado no urls.py
            window.location.href = `/clientes/agendamentos/escolher_dia/?id_servico=${idServico}&id_barbeiro=${idBarbeiro}`;
        } else {
            console.error("Dados faltando:", idServico, idBarbeiro);
            alert("Erro ao selecionar. Tente recarregar a página.");
        }
    });
}