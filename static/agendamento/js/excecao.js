/* =========================================================================
   1. LÓGICA DO TEMA (DARK/LIGHT MODE)
   ========================================================================= */
const themeSwitch = document.getElementById('theme-switch');
let lightmode = localStorage.getItem('lightmode');

if (lightmode === 'active') {
    document.body.classList.add('lightmode');
}

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

/* VARIÁVEL GLOBAL para rastrear o ID de um bloco de horário para exclusão */
let idParaExcluir = null;

/* =========================================================================
   3. FUNÇÃO PARA LIMPAR FORMULÁRIO E RESETAR O ESTADO
   ========================================================================= */
function limparFormulario() {
    document.getElementById('form-servico').reset();
    
    document.querySelectorAll(".dias-semana-chips button")
        .forEach(chip => chip.classList.remove('selected'));

    idParaExcluir = null;

    const btnExcluir = document.getElementById('btn-excluir');
    if (btnExcluir) btnExcluir.style.display = "none";

    const btnSalvar = document.getElementById('btn-salvar');
    if (btnSalvar) btnSalvar.style.display = "block";

    document.querySelectorAll('.item-lista')
        .forEach(b => b.classList.remove('editando'));
}

/* =========================================================================
   4. FUNÇÃO PARA MARCAR ID PARA EXCLUSÃO (AO CLICAR NO CARD)
   ========================================================================= */
function marcarIdParaExclusao(elementoCheckbox) {
    const id = elementoCheckbox.getAttribute('data-id');
    idParaExcluir = id; 

    const btnExcluir = document.getElementById('btn-excluir');
    const btnSalvar = document.getElementById('btn-salvar');

    if (btnExcluir) btnExcluir.style.display = "block"; 
    if (btnSalvar) btnSalvar.style.display = "none";
    
    document.querySelectorAll('.item-lista')
        .forEach(b => b.classList.remove('editando'));
    
    elementoCheckbox.closest('.item-lista').classList.add('editando');

    document.querySelectorAll(".dias-semana-chips button")
        .forEach(chip => chip.classList.remove('selected'));

    document.getElementById('form-servico').reset();
}

/* =========================================================================
   5. LÓGICA DOS CHIPS DE DIAS DA SEMANA (MODO CRIAÇÃO)
   ========================================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const chips = document.querySelectorAll(".dias-semana-chips button");

    chips.forEach(chip => {
        chip.addEventListener("click", () => {

            // só limpa se estiver realmente no modo exclusão
            const btnExcluir = document.getElementById('btn-excluir');
            if (btnExcluir && btnExcluir.style.display === "block") {
                limparFormulario();
            }

            // sempre mostrar o botão salvar quando clicado
            document.getElementById('btn-salvar').style.display = "block";

            // Agora permite seleção múltipla de fato
            chip.classList.toggle("selected");
        });
    });

    const checkboxesHorarios = document.querySelectorAll(".checkbox-horario");

    checkboxesHorarios.forEach(cb => {
        cb.addEventListener("change", () => {

            checkboxesHorarios.forEach(c => {
                if (c !== cb) c.checked = false;
            });

            if (cb.checked) {
                marcarIdParaExclusao(cb);
            } else {
                limparFormulario();
            }

        });
    });

    const btnExcluirInicial = document.getElementById('btn-excluir');
    if (btnExcluirInicial) btnExcluirInicial.style.display = "none";
});

/* =========================================================================
   6. LÓGICA DE SUBMISSÃO DO FORMULÁRIO (SALVAR HORÁRIOS EM MASSA - API)
   ========================================================================= */
const formHorarios = document.getElementById('form-servico');

if (formHorarios) {
    formHorarios.addEventListener('submit', async (e) => {
        e.preventDefault();

        const btnSalvar = document.getElementById('btn-salvar');
        if (btnSalvar.style.display === "none") return; 

        const chipsSelecionados = document.querySelectorAll(".dias-semana-chips button.selected");
        const listaDias = Array.from(chipsSelecionados).map(chip => chip.getAttribute('data-value'));

        const horarioInicio = document.getElementById('horario_inicio').value;
        const horarioFim = document.getElementById('horario_fim').value;
        const csrftoken = getCookie('csrftoken');

        if (listaDias.length === 0) {
            Swal.fire('Atenção', 'Selecione pelo menos um dia da semana.', 'warning');
            return;
        }

        const payload = {
            dias_semana: listaDias,
            horario_inicio: horarioInicio,
            horario_fim: horarioFim,
        };
        
        btnSalvar.disabled = true;

        try {
            const response = await fetch('/barbeiro/agendamentos/editar-agenda/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok && response.headers.get("content-type") && 
                !response.headers.get("content-type").includes("application/json")) {
                
                throw new Error("Resposta inesperada do servidor (Erro 500). Tente novamente.");
            }

            const data = await response.json();

            if (response.ok && data.sucesso) {
                Swal.fire('Sucesso!', data.mensagem, 'success').then(() => {
                    window.location.reload(); 
                });
            } else {
                Swal.fire('Erro!', data.mensagem, 'error');
            }

        } catch (error) {
            console.error('Erro na submissão:', error);
            let msg = error.message.includes("Resposta inesperada")
                        ? error.message
                        : "Falha na comunicação com o servidor. Verifique a rede.";
            Swal.fire('Erro de Comunicação', msg, 'error');
        } finally {
            btnSalvar.disabled = false;
        }
    });
}

/* =========================================================================
   7. LÓGICA DE EXCLUSÃO (BOTÃO DEDICADO)
   ========================================================================= */
const btnExcluir = document.getElementById('btn-excluir');

if (btnExcluir) {
    btnExcluir.addEventListener('click', (e) => {
        e.preventDefault();

        if (idParaExcluir) {
            Swal.fire({
                title: 'Tem certeza?',
                text: "Você deseja realmente excluir este bloco de horário?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, excluir',
                cancelButtonText: 'Voltar',
                reverseButtons: true
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const csrftoken = getCookie('csrftoken');

                    try {
                        const response = await fetch('/barbeiro/agendamentos/excluir-horario/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken
                            },
                            body: JSON.stringify({ 'id_horario': idParaExcluir })
                        });

                        if (!response.ok && response.headers.get("content-type") && 
                            !response.headers.get("content-type").includes("application/json")) {
                            
                            throw new Error("Resposta inesperada do servidor (Erro 500). Tente novamente.");
                        }

                        const data = await response.json();

                        if (response.ok && data.sucesso) {
                            Swal.fire('Excluído!', data.mensagem || 'Horário excluído com sucesso!', 'success')
                                .then(() => window.location.reload());
                        } else {
                            Swal.fire('Erro', data.mensagem || 'Erro ao excluir.', 'error');
                        }
                    } catch (error) {
                         console.error('Erro de Comunicação:', error);
                         let msg = error.message.includes("Resposta inesperada")
                                     ? error.message
                                     : "Falha de rede ou JSON. Verifique a conexão.";
                         Swal.fire('Erro de Exclusão', msg, 'error');
                    }
                }
            });
        } else {
            Swal.fire('Atenção', 'Selecione um bloco de horário na lista ao lado para excluir.', 'info');
        }
    });
}

/* =========================================================================
   8. BOTÃO CANCELAR EDIÇÃO (REUTILIZA FUNÇÃO DE LIMPEZA)
   ========================================================================= */
const btnLimpar = document.getElementById('btn-limpar');
if (btnLimpar) {
    btnLimpar.addEventListener('click', limparFormulario);
    btnLimpar.style.display = "none";
}
