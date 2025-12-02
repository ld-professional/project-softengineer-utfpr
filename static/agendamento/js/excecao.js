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

/* VARIÁVEL GLOBAL para rastrear o ID de um bloco para exclusão */
let idParaExcluir = null;

/* =========================================================================
   3. FUNÇÃO PARA LIMPAR FORMULÁRIO E RESETAR O ESTADO
   ========================================================================= */
function limparFormulario() {
    const form = document.getElementById('form-servico');
    if(form) form.reset();
    
    // Reseta visibilidade do campo data fim
    const containerDiaFim = document.getElementById('container_dia_fim');
    if (containerDiaFim) containerDiaFim.style.display = 'none';

    // Reseta visualmente o botão de prolongar
    const btnProlongar = document.getElementById('btn-prolongar');
    if (btnProlongar) btnProlongar.classList.remove('checked');

    idParaExcluir = null;

    const btnExcluir = document.getElementById('btn-excluir');
    if (btnExcluir) btnExcluir.style.display = "none";

    const btnSalvar = document.getElementById('btn-salvar');
    if (btnSalvar) {
        btnSalvar.style.display = "block";
        btnSalvar.innerText = "Salvar Exceção";
        btnSalvar.disabled = false;
    }

    document.querySelectorAll('.item-lista')
        .forEach(b => b.classList.remove('editando'));
}

/* =========================================================================
   4. FUNÇÃO PARA MARCAR ID PARA EXCLUSÃO (AO CLICAR NO CHECKBOX)
   ========================================================================= */
function marcarIdParaExclusao(elementoCheckbox) {
    const id = elementoCheckbox.getAttribute('data-id');
    idParaExcluir = id; 

    const btnExcluir = document.getElementById('btn-excluir');
    const btnSalvar = document.getElementById('btn-salvar');

    if (btnExcluir) btnExcluir.style.display = "block"; 
    if (btnSalvar) btnSalvar.style.display = "none";
    
    // Remove estilo de edição de todos e adiciona só no atual
    document.querySelectorAll('.item-lista').forEach(b => b.classList.remove('editando'));
    elementoCheckbox.closest('.item-lista').classList.add('editando');

    // Reseta o form para garantir que não se está editando dados antigos
    document.getElementById('form-servico').reset();
    
    // Garante que o campo extra esteja fechado e o botão desmarcado
    const containerDiaFim = document.getElementById('container_dia_fim');
    if (containerDiaFim) containerDiaFim.style.display = 'none';
    
    const btnProlongar = document.getElementById('btn-prolongar');
    if (btnProlongar) btnProlongar.classList.remove('checked');
}

/* =========================================================================
   5. LISTENERS GERAIS (CARREGAMENTO DA PÁGINA)
   ========================================================================= */
document.addEventListener("DOMContentLoaded", () => {
    
    // Configura os checkboxes da lista lateral
    const checkboxesHorarios = document.querySelectorAll(".checkbox-horario");

    checkboxesHorarios.forEach(cb => {
        cb.addEventListener("change", () => {
            // Garante seleção única
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

    // Garante estado inicial dos botões
    const btnExcluirInicial = document.getElementById('btn-excluir');
    if (btnExcluirInicial) btnExcluirInicial.style.display = "none";


    /* --- LÓGICA DO BOTÃO PROLONGAR (NOVO ESTILO CHIP) --- */
    const btnProlongar = document.getElementById('btn-prolongar');
    const containerDiaFim = document.getElementById('container_dia_fim');
    const inputDiaFim = document.getElementById('dia_fim_excecao');

    if (btnProlongar && containerDiaFim) {
        btnProlongar.addEventListener('click', () => {
            // Alterna a classe visual
            btnProlongar.classList.toggle('checked');
            
            // Verifica se está marcado
            const isChecked = btnProlongar.classList.contains('checked');

            if (isChecked) {
                containerDiaFim.style.display = 'block';
                inputDiaFim.required = true; 
            } else {
                containerDiaFim.style.display = 'none';
                inputDiaFim.value = ''; 
                inputDiaFim.required = false;
            }
        });
    }
});

/* =========================================================================
   6. LÓGICA DE SUBMISSÃO (SALVAR EXCEÇÃO)
   ========================================================================= */
const formServico = document.getElementById('form-servico');

if (formServico) {
    formServico.addEventListener('submit', async (e) => {
        e.preventDefault();

        const btnSalvar = document.getElementById('btn-salvar');
        if (btnSalvar.style.display === "none") return; 

        // Captura os valores dos inputs
        const diaInicio = document.getElementById('dia_excecao').value;
        let diaFim = document.getElementById('dia_fim_excecao').value;
        const horarioInicio = document.getElementById('horario_inicio').value;
        const horarioFim = document.getElementById('horario_fim').value;
        const motivo = document.getElementById('motivo_excecao').value;
        
        // Verifica o estado do botão PROLONGAR pela classe .checked
        const btnProlongar = document.getElementById('btn-prolongar');
        const isProlongado = btnProlongar && btnProlongar.classList.contains('checked');
        
        const csrftoken = getCookie('csrftoken');

        // Se NÃO estiver prolongado, diaFim deve ser igual a diaInicio
        if (!isProlongado || !diaFim) {
            diaFim = diaInicio;
        }

        // Validação simples no front
        if (!diaInicio || !diaFim || !horarioInicio || !horarioFim || !motivo) {
            Swal.fire('Atenção', 'Preencha todos os campos.', 'warning');
            return;
        }

        const payload = {
            dia_excecao: diaInicio,
            dia_fim: diaFim,
            horario_inicio: horarioInicio,
            horario_fim: horarioFim,
            motivo: motivo
        };
        
        btnSalvar.disabled = true;
        btnSalvar.innerText = "Salvando...";

        try {
            const response = await fetch('/barbeiro/agendamentos/salvar-excecao/', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok && data.sucesso) {
                Swal.fire('Sucesso!', data.mensagem, 'success').then(() => {
                    window.location.reload(); 
                });
            } else {
                Swal.fire('Erro!', data.mensagem, 'error');
            }

        } catch (error) {
            console.error('Erro:', error);
            Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
        } finally {
            btnSalvar.disabled = false;
            btnSalvar.innerText = "Salvar Exceção";
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
                text: "Você deseja remover esta exceção?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const csrftoken = getCookie('csrftoken');

                    try {
                        const response = await fetch('/barbeiro/agendamentos/excluir-excecao/', { 
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken
                            },
                            body: JSON.stringify({ 'id_excecao': idParaExcluir })
                        });

                        if (!response.ok && response.headers.get("content-type") && 
                            !response.headers.get("content-type").includes("application/json")) {
                            throw new Error("Erro no servidor.");
                        }

                        const data = await response.json();

                        if (response.ok && data.sucesso) {
                            Swal.fire('Excluído!', data.mensagem, 'success')
                                .then(() => window.location.reload());
                        } else {
                            Swal.fire('Erro', data.mensagem || 'Erro ao excluir.', 'error');
                        }
                    } catch (error) {
                         console.error('Erro de Comunicação:', error);
                         Swal.fire('Erro de Exclusão', 'Falha ao tentar excluir.', 'error');
                    }
                }
            });
        } else {
            Swal.fire('Atenção', 'Selecione um item na lista ao lado para excluir.', 'info');
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