const themeSwitch = document.getElementById('theme-switch');

// Pega o estado atual do modo (se está claro ou escuro) do armazenamento local.
let lightmode = localStorage.getItem('lightmode');

// Funções para manipular o tema
const enableLightMode = () => {
    // Adiciona a classe que aplica o estilo claro
    document.body.classList.add('lightmode');
    // Marca o estado como 'ativo' no localStorage
    localStorage.setItem('lightmode', 'active');
};
const disableLightMode = () => {
    // Remove a classe para retornar ao tema padrão (geralmente escuro)
    document.body.classList.remove('lightmode');
    // Remove o estado
    localStorage.setItem('lightmode', null);
};

// Aplica o tema imediatamente se estiver ativo no localStorage
if (lightmode === 'active') {
    enableLightMode();
}

// Adiciona o listener para o botão de alternância
themeSwitch.addEventListener('click', () => {
    lightmode = localStorage.getItem('lightmode');
    if (lightmode !== 'active') {
        enableLightMode();
    } else {
        disableLightMode();
    }
});


// ----------------------------------------------------------------------

// === 🔑 Lógica de Logout Segura (via Fetch/POST) ===

// 1. Função auxiliar para obter o valor de um cookie
// ESSENCIAL: O token CSRF é lido do cookie para ser enviado no cabeçalho.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // O nome do token CSRF do Django é 'csrftoken'
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Garante que o código de logout só rode após o DOM estar totalmente carregado
document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.getElementById('logout-button');

    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            // 2. Obtém o token CSRF do cookie
            const csrftoken = getCookie('csrftoken');
            
            // 3. Executa a requisição POST (Obrigatório por segurança CSRF)
            // CORREÇÃO APLICADA: Incluído o prefixo '/clientes/' para resolver o erro 404.
            fetch('/clientes/logout/', { 
                method: 'POST',
                // 🟢 Inclui o token no cabeçalho 'X-CSRFToken'
                headers: {
                    'X-CSRFToken': csrftoken, // Django verifica este cabeçalho para validar o CSRF
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({}) // Corpo da requisição pode ser vazio
            })
            .then(response => {
                // 4. Tratamento da Resposta
                
                // response.ok é true para status 200-299.
                // Como a view retorna 204 No Content, response.ok será true no sucesso.
                if (response.ok) {
                    window.location.href = '/'; // Redireciona APENAS no sucesso do logout
                } else {
                    // Se falhar (ex: 403 Forbidden por CSRF inválido, ou 404 de novo, ou 500)
                    console.error('Logout falhou com status:', response.status);
                    alert('Falha ao sair. Tente novamente. Status: ' + response.status);
                }
            })
            .catch(error => {
                // 5. Tratamento de Erros de Rede (ex: servidor offline)
                console.error('Erro de rede:', error);
                alert('Erro de conexão.');
            });
        });
    }
});