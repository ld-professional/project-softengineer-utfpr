// --- 1. FUNÇÃO PARA PEGAR O TOKEN CSRF (OBRIGATÓRIA PARA POST) ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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

// --- VARIÁVEL GLOBAL ---
let idSelecionado = null;

// --- A FUNÇÃO QUE O HTML CHAMA AO CLICAR NO CARD ---
function selecionarServico(elementoClicado) {
    
    // 1. Limpa a seleção visual dos outros
    const todosBlocos = document.querySelectorAll('.link-bloco');
    todosBlocos.forEach(bloco => bloco.classList.remove('selecionado'));

    // 2. Marca o atual
    elementoClicado.classList.add('selecionado');

    // 3. Pega o ID que está no atributo data-id (Não precisa de hidden input)
    idSelecionado = elementoClicado.getAttribute('data-id');
    console.log("Agendamento Selecionado ID:", idSelecionado);

    // 4. Ativa visualmente o botão de cancelar
    const btnConfirmar = document.querySelector('.confirm-button');
    if (btnConfirmar) btnConfirmar.classList.add('ativo');
}

// --- BOTÃO CONFIRMAR (LÓGICA DE CANCELAMENTO VIA API) ---
const btnConfirmar = document.querySelector('.confirm-button');

if (btnConfirmar) {
    btnConfirmar.addEventListener('click', (e) => {
        e.preventDefault();

        if (idSelecionado) {
            // 1. SUBSTITUI O 'confirm()' NATIVO PELO SWEETALERT
            Swal.fire({
                title: 'Tem certeza?',
                text: "Você deseja realmente cancelar este agendamento?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, cancelar',
                cancelButtonText: 'Voltar',
                reverseButtons: true // Inverte a ordem dos botões para ficar mais intuitivo
            }).then((result) => {
                // Se o usuário clicou em "Sim"
                if (result.isConfirmed) {
                    
                    // Pega o token CSRF
                    const csrftoken = getCookie('csrftoken');

                    // Mostra um loading enquanto processa (opcional, mas fica chique)
                    Swal.fire({
                        title: 'Processando...',
                        html: 'Aguarde um momento.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    // Chama a sua URL configurada no urls.py
                    fetch('/barbeiro/servicos/excluir-servico/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            'id_agendamentos': idSelecionado 
                        })
                    })
                    .then(response => {
                        if (response.ok) {
                            // 2. SUBSTITUI O 'alert()' DE SUCESSO
                            Swal.fire({
                                icon: 'success',
                                title: 'Excluido!',
                                text: 'Serviço cancelado com sucesso!',
                                confirmButtonText: 'OK'
                            }).then(() => {
                                window.location.reload(); // Recarrega só depois do OK
                            });
                        } else {
                            // SUBSTITUI O 'alert()' DE ERRO
                            Swal.fire({
                                icon: 'error',
                                title: 'Erro',
                                text: 'Erro ao excluir. Tente novamente.'
                            });
                            console.error("Status do erro:", response.status);
                        }
                    })
                    .catch(error => {
                        console.error('Erro de rede:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro de conexão',
                            text: 'Verifique sua internet.'
                        });
                    });
                }
            });

        } else {
            // 3. SUBSTITUI O 'alert()' DE SELEÇÃO
            Swal.fire({
                icon: 'info',
                title: 'Atenção',
                text: 'Por favor, selecione um agendamento para cancelar!'
            });
        }
    });
}

// --- CARROSSEL ---
const scrollContainer = document.getElementById('scroll-container');
const btnEsq = document.getElementById('btn-esq');
const btnDir = document.getElementById('btn-dir');

if (btnEsq && btnDir && scrollContainer) {
    btnEsq.addEventListener('click', () => {
        scrollContainer.scrollTo({ left: scrollContainer.scrollLeft - 220, behavior: 'smooth' });
    });
    btnDir.addEventListener('click', () => {
        scrollContainer.scrollTo({ left: scrollContainer.scrollLeft + 220, behavior: 'smooth' });
    });
}

// --- BOTÕES VOLTAR/INICIO ---
const btnVoltar = document.getElementById('voltar-dash-btn');
if (btnVoltar) btnVoltar.addEventListener('click', () => window.location.href = '/barbeiro/dashboard/');

const btnInicio = document.getElementById('inicio-dash-tbm-btn');
if (btnInicio) btnInicio.addEventListener('click', () => window.location.href = '/barbeiro/dashboard/');