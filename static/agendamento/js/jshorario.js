/* =========================================================================
   ENTENDENDO O FLUXO DESTA TELA (DOCUMENTAÇÃO DIDÁTICA)
   =========================================================================
   1. O DJANGO (Backend) enviou o HTML com dois campos invisíveis (<input hidden>)
      contendo o ID do Serviço e o ID do Barbeiro escolhidos anteriormente.
   
   2. O JAVASCRIPT (Este arquivo) inicia e desenha o calendário visual na tela.
   
   3. QUANDO O USUÁRIO CLICA EM UM DIA (Ex: Dia 25):
      a. O JS formata essa data para o padrão internacional "2025-11-25".
      b. O JS pega os IDs dos campos invisíveis.
      c. O JS envia tudo isso para o Django usando 'fetch' (GET).
         URL: /api/buscar-horarios/?data=...&id_barbeiro=...&id_servico=...
   
   4. O DJANGO RESPONDE:
      - Devolve uma lista JSON com os horários livres: ['08:00', '08:30', '14:00']
   
   5. O JAVASCRIPT ATUALIZA A TELA:
      - Apaga a lista antiga e desenha botões novos com esses horários.
      
   6. AO CONFIRMAR:
      - O JS envia um POST com todos os dados para salvar no banco.
========================================================================= */

// --- 1. SELEÇÃO DOS ELEMENTOS DO HTML ---
const botaoTema = document.getElementById('theme-switch');
const textoMesAno = document.getElementById('monthYear'); // Título "Novembro 2025"
const containerDias = document.getElementById('dates');   // Onde ficam as bolinhas dos dias
const btnMesAnterior = document.getElementById('prevButton');
const btnProximoMes = document.getElementById('nextButton');
const divListaHorarios = document.getElementById("listaHorarios"); // Onde entram os botões de hora

// Captura os INPUTS INVISÍVEIS que o Django preencheu no HTML
const campoOcultoIdServico = document.getElementById('id_servico_hidden');
const campoOcultoIdBarbeiro = document.getElementById('id_barbeiro_hidden');

// --- 2. VARIÁVEIS DE CONTROLE (MEMÓRIA DO JS) ---
let dataAtualDoCalendario = new Date(); // Controla qual mês estamos vendo agora
let horarioFinalEscolhido = null;       // Guarda "14:30" quando o usuário clica
let dataFormatadaParaApi = null;        // Guarda "2025-11-25" para enviar pro Django

// =========================================================================
// 3. FUNÇÃO PRINCIPAL: DESENHAR O CALENDÁRIO
// =========================================================================
const renderizarCalendario = () => {
    const anoAtual = dataAtualDoCalendario.getFullYear();
    const mesAtual = dataAtualDoCalendario.getMonth();

    // Cálculos matemáticos para saber onde começar e terminar o mês
    const primeiroDiaDoMes = new Date(anoAtual, mesAtual, 1);
    const ultimoDiaDoMes = new Date(anoAtual, mesAtual + 1, 0);
    const totalDiasNoMes = ultimoDiaDoMes.getDate();
    const diaDaSemanaQueComeca = primeiroDiaDoMes.getDay(); // 0=Dom, 1=Seg...

    // Atualiza o título (Ex: "Novembro 2025")
    const nomeMesAno = dataAtualDoCalendario.toLocaleString('pt-BR', { month: 'long', year: 'numeric' });
    textoMesAno.textContent = nomeMesAno.charAt(0).toUpperCase() + nomeMesAno.slice(1);

    let htmlDosDias = '';

    // Ajuste visual: Se o calendário começa na Segunda mas o dia 1 é Domingo
    // (Se seu CSS .days começa com Segunda, use esta lógica)
    const diasVaziosAntes = diaDaSemanaQueComeca === 0 ? 6 : diaDaSemanaQueComeca - 1;

    // a) Desenha dias cinzas do mês passado (inativos)
    for (let i = diasVaziosAntes; i > 0; i--) {
        const dataPassada = new Date(anoAtual, mesAtual, 1 - i);
        htmlDosDias += `<div class="date inactive">${dataPassada.getDate()}</div>`;
    }

    // b) Desenha os dias do mês atual (Bolinhas clicáveis)
    for (let dia = 1; dia <= totalDiasNoMes; dia++) {
        const dataVerificada = new Date(anoAtual, mesAtual, dia);
        
        // Verifica se é hoje para pintar de cor diferente (opcional)
        const ehHoje = dataVerificada.toDateString() === new Date().toDateString() ? 'active' : '';
        
        // Adiciona o dia no HTML com um atributo especial 'data-dia-numero'
        htmlDosDias += `<div class="date ${ehHoje}" data-dia-numero="${dia}">${dia}</div>`;
    }

    containerDias.innerHTML = htmlDosDias;

    // --- AGORA ADICIONAMOS O CLIQUE NOS DIAS ---
    adicionarEventoCliqueNosDias(anoAtual, mesAtual);
}

// Função separada para organizar o código do clique
function adicionarEventoCliqueNosDias(ano, mes) {
    // Pega todas as bolinhas que não são cinzas (inactive)
    const bolinhasDosDias = document.querySelectorAll(".date:not(.inactive)");

    bolinhasDosDias.forEach(bolinha => {
        bolinha.addEventListener("click", () => {
            
            // 1. Visual: Remove o amarelo de todos e coloca no clicado
            bolinhasDosDias.forEach(d => d.classList.remove("selected"));
            bolinha.classList.add("selected");

            // 2. Recupera o número do dia clicado (ex: 25)
            const diaNumero = parseInt(bolinha.dataset.diaNumero);
            
            // 3. FORMATAÇÃO MANUAL E SEGURA DA DATA (YYYY-MM-DD)
            // Isso garante que o Django entenda, independente do navegador
            const anoStr = ano;
            // Adiciona zero à esquerda se for menor que 10 (ex: mês 9 vira "09")
            const mesStr = String(mes + 1).padStart(2, '0'); 
            const diaStr = String(diaNumero).padStart(2, '0');
            
            dataFormatadaParaApi = `${anoStr}-${mesStr}-${diaStr}`; // Ex: "2025-11-24"

            console.log("O usuário escolheu a data:", dataFormatadaParaApi);

            // 4. Chama a função que conversa com o Backend
            buscarHorariosDisponiveisNoBackend(dataFormatadaParaApi);
        });
    });
}

// =========================================================================
// 4. COMUNICAÇÃO COM O BACKEND (A API GET)
// =========================================================================
async function buscarHorariosDisponiveisNoBackend(dataString) {
    divListaHorarios.innerHTML = '<p class="mensagem">Consultando agenda...</p>';

    // Pega os valores dos inputs ocultos no HTML
    // O .value lê o que o Django escreveu lá: value="3"
    const idServico = campoOcultoIdServico ? campoOcultoIdServico.value : null;
    const idBarbeiro = campoOcultoIdBarbeiro ? campoOcultoIdBarbeiro.value : null;

    // Validação de segurança
    if (!idServico || !idBarbeiro) {
        divListaHorarios.innerHTML = '<p style="color:red">Erro: IDs do serviço ou barbeiro não encontrados.</p>';
        return;
    }

    // --- AQUI ESTÁ O JEITO SIMPLES DE MONTAR A URL ---
    // O URLSearchParams cria automaticamente: "?data=...&id_barbeiro=...&id_servico=..."
    const parametrosUrl = new URLSearchParams({
        data: dataString,
        id_barbeiro: idBarbeiro,
        id_servico: idServico
    });

    try {
        // Faz o pedido para o Django (GET)
        // Atenção para o caminho da URL, deve bater com seu urls.py
        const resposta = await fetch(`/clientes/agendamentos/api/buscar-horarios/?${parametrosUrl}`);
        const dadosJson = await resposta.json();

        divListaHorarios.innerHTML = ""; // Limpa a mensagem de "carregando"

        if (resposta.ok) {
            // Se o Django disse OK (200)
            if (dadosJson.horarios && dadosJson.horarios.length > 0) {
                criarBotoesDeHorarioNaTela(dadosJson.horarios);
            } else {
                divListaHorarios.innerHTML = `<p class="mensagem">${dadosJson.mensagem || 'Agenda cheia ou barbeiro não trabalha.'}</p>`;
            }
        } else {
            // Se o Django deu erro (400 ou 500)
            divListaHorarios.innerHTML = `<p class="mensagem" style="color:red">${dadosJson.erro || 'Erro no servidor.'}</p>`;
        }

    } catch (erro) {
        console.error(erro);
        divListaHorarios.innerHTML = '<p class="mensagem" style="color:red">Erro de conexão.</p>';
    }
}

// =========================================================================
// 5. FUNÇÃO QUE CRIA OS BOTÕES VISUAIS DOS HORÁRIOS
// =========================================================================
function criarBotoesDeHorarioNaTela(listaDeHorarios) {
    // Recebe a lista ['08:00', '08:30'] e cria divs para cada um
    listaDeHorarios.forEach(horarioTexto => {
        const botaoHorario = document.createElement("div");
        botaoHorario.classList.add("horario"); // Classe do CSS
        botaoHorario.textContent = horarioTexto;

        // Adiciona evento de clique no horário
        botaoHorario.addEventListener("click", () => {
            // Remove seleção anterior
            document.querySelectorAll(".horario").forEach(h => h.classList.remove("selected"));
            
            // Marca este como selecionado
            botaoHorario.classList.add("selected");
            
            horarioFinalEscolhido = horarioTexto; // Salva na memória
            console.log("Horário final:", horarioFinalEscolhido);
        });

        divListaHorarios.appendChild(botaoHorario);
    });
}

// =========================================================================
// 6. BOTÕES DE NAVEGAÇÃO DO CALENDÁRIO
// =========================================================================
btnMesAnterior.addEventListener('click', () => {
    dataAtualDoCalendario.setMonth(dataAtualDoCalendario.getMonth() - 1);
    renderizarCalendario();
});

btnProximoMes.addEventListener('click', () => {
    dataAtualDoCalendario.setMonth(dataAtualDoCalendario.getMonth() + 1);
    renderizarCalendario();
});

// Inicia o calendário ao carregar a página
renderizarCalendario();


// =========================================================================
// 7. TEMA DARK/LIGHT E NAVEGAÇÃO DE PÁGINAS
// =========================================================================
let modoEscuroAtivo = localStorage.getItem('lightmode');

if (modoEscuroAtivo === 'active') {
    document.body.classList.add('lightmode');
}

botaoTema.addEventListener('click', () => {
    modoEscuroAtivo = localStorage.getItem('lightmode');
    if (modoEscuroAtivo !== 'active') {
        document.body.classList.add('lightmode');
        localStorage.setItem('lightmode', 'active');
    } else {
        document.body.classList.remove('lightmode');
        localStorage.setItem('lightmode', null);
    }
});

// Botão Voltar Inteligente
const btnVoltar = document.getElementById('voltar-dash-btn');

if (btnVoltar) {
    btnVoltar.addEventListener('click', function(e) {
        e.preventDefault(); 
        
        // Lê a URL atual para saber qual ID de Serviço devolver para a tela anterior
        const params = new URLSearchParams(window.location.search);
        const idServicoAtual = params.get('id_servico');

        if (idServicoAtual) {
            // Volta para Barbeiros sem perder o ID do Serviço
            window.location.href = `/clientes/agendamentos/escolher_barbeiro/?id_servico=${idServicoAtual}`;
        } else {
            // Se der erro, tenta o histórico normal
            window.history.back();
        }
    });
}

const btnInicio = document.getElementById('inicio-dash-tbm-btn');
if (btnInicio) {
    btnInicio.addEventListener('click', function() {
        window.location.href = '/clientes/dashboard/'; 
    });
}

// =========================================================================
// 8. BOTÃO CONFIRMAR AGENDAMENTO (POST FINAL)
// =========================================================================
const btnConfirmarFinal = document.querySelector('.confirm-button');

if(btnConfirmarFinal) {
    btnConfirmarFinal.addEventListener('click', async () => {
        
        // 1. Validação Básica no Frontend
        if(!dataFormatadaParaApi || !horarioFinalEscolhido) {
            alert("Por favor, selecione um dia no calendário e um horário disponível.");
            return;
        }

        const idServico = campoOcultoIdServico ? campoOcultoIdServico.value : null;
        const idBarbeiro = campoOcultoIdBarbeiro ? campoOcultoIdBarbeiro.value : null;

        // 2. Monta o pacote de dados (Payload)
        const pacoteDeDados = {
            id_servico: idServico,
            id_barbeiro: idBarbeiro,
            data: dataFormatadaParaApi, // YYYY-MM-DD
            hora: horarioFinalEscolhido // HH:MM
        };

        // Feedback visual (Desabilita botão para não clicar 2x)
        btnConfirmarFinal.disabled = true;
        btnConfirmarFinal.textContent = "Processando...";

        try {
            // 3. Envia para o Django (POST)
            const resposta = await fetch('/clientes/agendamentos/api/salvar-agendamento/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': obterTokenCsrf('csrftoken') // Função obrigatória abaixo
                },
                body: JSON.stringify(pacoteDeDados)
            });

            const dados = await resposta.json();

            if (resposta.ok) {
                alert("Sucesso! " + dados.mensagem);
                // Redireciona para o Dashboard
                window.location.href = '/clientes/agendamentos/agendamento-realizado';
            } else {
                // Mostra o erro que veio do Python (ex: Conflito de horário)
                let msgErro = dados.erro;
                if (typeof msgErro === 'object') {
                    // Limpa o erro se vier como objeto feio {"erro": "..."}
                    msgErro = JSON.stringify(msgErro).replace(/[{}"]/g, ''); 
                }
                alert("Erro ao agendar: " + msgErro);
                
                // Reabilita o botão para tentar de novo
                btnConfirmarFinal.disabled = false;
                btnConfirmarFinal.textContent = "Confirmar Agendamento";
            }

        } catch (erro) {
            console.error(erro);
            alert("Erro de conexão com o servidor.");
            btnConfirmarFinal.disabled = false;
            btnConfirmarFinal.textContent = "Confirmar Agendamento";
        }
    });
}

// =========================================================================
// 9. FUNÇÃO AUXILIAR: CSRF TOKEN (Necessária para segurança do Django)
// =========================================================================
function obterTokenCsrf(name) {
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