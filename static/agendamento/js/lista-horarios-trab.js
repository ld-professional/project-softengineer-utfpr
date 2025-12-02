/* =========================================================================
   1. LÓGICA DO TEMA (DARK/LIGHT MODE) - ADICIONADO AGORA
   ========================================================================= */
const themeSwitch = document.getElementById('theme-switch');
let lightmode = localStorage.getItem('lightmode');

// Verifica se já estava no modo claro antes
if (lightmode === 'active') {
    document.body.classList.add('lightmode');
}

if (themeSwitch) {
    themeSwitch.addEventListener('click', () => {
        lightmode = localStorage.getItem('lightmode');
        if (lightmode !== 'active') {
            // Ativa modo claro
            document.body.classList.add('lightmode');
            localStorage.setItem('lightmode', 'active');
        } else {
            // Volta para modo escuro
            document.body.classList.remove('lightmode');
            localStorage.setItem('lightmode', null);
        }
    });
}

/* =========================================================================
   2. FUNÇÃO PARA PEGAR O TOKEN CSRF (SEGURANÇA DJANGO)
   ========================================================================= */
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

/* =========================================================================
   3. LÓGICA DE PREENCHIMENTO DO FORMULÁRIO (AO CLICAR NO CARD)
   ========================================================================= */
let idParaExcluir = null;

function preencherFormulario(elemento) {
    // Pega dados do HTML (data-attributes)
    const id = elemento.getAttribute('data-id');
    const nome = elemento.getAttribute('data-nome');
    const preco = elemento.getAttribute('data-preco');
    const duracao = elemento.getAttribute('data-duracao');

    // Preenche os inputs do lado esquerdo
    document.getElementById('id_servico').value = id;
    document.getElementById('nome_servico').value = nome;
    document.getElementById('preco_servico').value = preco.replace(',', '.');
    document.getElementById('slot_duracao_servico').value = duracao;

    // Configura botões para modo "Edição"
    idParaExcluir = id; 
    document.querySelector('.confirm-button').classList.add('ativo'); // Acende o botão excluir
    
    document.getElementById('btn-salvar').innerText = "Atualizar Serviço";
    document.getElementById('btn-limpar').style.display = "block"; // Mostra botão cancelar

    // Efeito visual no card selecionado
    document.querySelectorAll('.link-bloco').forEach(b => b.classList.remove('editando'));
    elemento.classList.add('editando');
    
    // Se for celular, rola para o topo para ver o formulário
    if (window.innerWidth < 900) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/* =========================================================================
   4. BOTÃO CANCELAR EDIÇÃO (LIMPAR FORMULÁRIO)
   ========================================================================= */
const btnLimpar = document.getElementById('btn-limpar');
if (btnLimpar) {
    btnLimpar.addEventListener('click', function() {
        // Limpa tudo
        document.getElementById('form-servico').reset();
        document.getElementById('id_servico').value = "";
        
        // Reseta textos e botões
        document.getElementById('btn-salvar').innerText = "Salvar Serviço";
        this.style.display = "none";
        
        // Desativa botão de excluir
        idParaExcluir = null;
        document.querySelector('.confirm-button').classList.remove('ativo');
        
        // Remove seleção visual dos cards
        document.querySelectorAll('.link-bloco').forEach(b => b.classList.remove('editando'));
    });
}

/* =========================================================================
   5. LÓGICA DE EXCLUSÃO (BOTÃO VERMELHO)
   ========================================================================= */
const btnExcluir = document.querySelector('.confirm-button');

if (btnExcluir) {
    btnExcluir.addEventListener('click', (e) => {
        e.preventDefault();

        if (idParaExcluir) {
            Swal.fire({
                title: 'Tem certeza?',
                text: "Você deseja realmente excluir este serviço?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, excluir',
                cancelButtonText: 'Voltar',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    const csrftoken = getCookie('csrftoken');

                    // Envia requisição para excluir
                    fetch('/barbeiro/servicos/excluir-servico/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            'id_agendamentos': idParaExcluir // Mantendo a chave que seu backend espera
                        })
                    })
                    .then(response => {
                        if (response.ok) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Excluído!',
                                text: 'Serviço excluído com sucesso!',
                                confirmButtonText: 'OK'
                            }).then(() => {
                                window.location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Erro',
                                text: 'Erro ao excluir. Tente novamente.'
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro de conexão',
                            text: 'Verifique sua internet.'
                        });
                    });
                }
            });
        } else {
            Swal.fire({
                icon: 'info',
                title: 'Atenção',
                text: 'Selecione um serviço na lista ao lado para excluir.'
            });
        }
    });
}

/* =========================================================================
   6. CARROSSEL (SETAS DE NAVEGAÇÃO)
   ========================================================================= */
const scrollContainer = document.getElementById('scroll-container');
const btnEsq = document.getElementById('btn-esq');
const btnDir = document.getElementById('btn-dir');

if (btnEsq && btnDir && scrollContainer) {
    btnEsq.addEventListener('click', () => {
        scrollContainer.scrollBy({ left: -300, behavior: 'smooth' });
    });
    btnDir.addEventListener('click', () => {
        scrollContainer.scrollBy({ left: 300, behavior: 'smooth' });
    });
}

/* =========================================================================
   7. LÓGICA DOS DIAS DA SEMANA (CHIPS SELECIONÁVEIS)
   ========================================================================= */
document.addEventListener("DOMContentLoaded", () => {

    const chips = document.querySelectorAll(".dias-semana-chips button");

    chips.forEach(chip => {
        chip.addEventListener("click", () => {

            // Alterna visualmente
            chip.classList.toggle("selected");

            // Input hidden correspondente
            const input = document.querySelector(`input[name="dias_semana"][value="${chip.dataset.value}"]`);

            if (!input) return;

            // Marca/desmarca o valor
            if (chip.classList.contains("selected")) {
                input.checked = true;
            } else {
                input.checked = false;
            }
        });
    });

});

/* =========================================================================
   8. LÓGICA PARA CHECKBOX NA LISTA (NOVO FORMATO)
   ========================================================================= */
document.addEventListener("DOMContentLoaded", () => {

    const checkboxes = document.querySelectorAll(".checkbox-servico");

    checkboxes.forEach(cb => {
        cb.addEventListener("change", () => {

            // Desmarca todos os outros
            checkboxes.forEach(c => {
                if (c !== cb) c.checked = false;
            });

            // Se marcou, preenche o formulário
            if (cb.checked) {
                preencherFormulario(cb);
            } else {
                // se desmarcar, limpa o form
                document.getElementById('btn-limpar').click();
            }

        });
    });

});
