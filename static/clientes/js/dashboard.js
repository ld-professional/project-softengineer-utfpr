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


// parte de logout

// 1. Função auxiliar para obter o valor de um cookie
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

document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.getElementById('logout-button');

    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            // 2. Obtém o token CSRF do cookie
            const csrftoken = getCookie('csrftoken');
            
            // 3. Executa a requisição POST
            fetch('/logout/', {
                method: 'POST',
                // 🟢 Inclui o token no cabeçalho 'X-CSRFToken'
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                    // Content-Type pode ser opcionalmente JSON, ou vazio se não houver corpo
                },
                // O corpo da requisição pode ser vazio ou {}
                body: JSON.stringify({})
            })
            .then(response => {
                // 4. Se a requisição for bem-sucedida, o Django View (logout_view)
                // retorna um redirecionamento 302 para 'pagina_inicial'.
                
                // Redireciona o navegador manualmente após o sucesso.
                // Na prática, é mais limpo pedir ao servidor a URL de redirecionamento.
                
                // Se o servidor retornar 200 (em vez de 302), você deve redirecionar:
                if (response.ok || response.status === 302) {
                    window.location.href = '/'; // Redireciona para a home page
                } else {
                    console.error('Logout falhou com status:', response.status);
                    alert('Falha ao sair. Tente novamente.');
                }
            })
            .catch(error => {
                console.error('Erro de rede:', error);
                alert('Erro de conexão.');
            });
        });
    }
});