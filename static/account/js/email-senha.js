// Seleção de Elementos
const email_input = document.getElementById('email');
const form = document.getElementById('form');
const password_input = document.getElementById('password');
const repeat_password_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message');
const themeSwitch = document.getElementById('theme-switch');

// --- LÓGICA DE TEMA (Dark/Light Mode) ---
let lightmode = localStorage.getItem('lightmode');

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


// --- FUNÇÃO GETCOOKIE (Necessária para segurança CSRF) --- basicamente um copia e cola da internet...
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


// --- ABSTRAÇÃO INTELIGENTE: Captura UID e TOKEN da URL ---
// O navegador extrai automaticamente tudo que vem depois da '?'
const params = new URLSearchParams(window.location.search);
const uid = params.get('uid');
const token = params.get('token');

// Verificação de Segurança Imediata
// Se estamos na página de Trocar Senha (tem input password), MAS o link não tem token...
if (password_input && (!uid || !token)) {
    alert("Link inválido ou incompleto. Por favor, solicite a recuperação novamente.");
    window.location.href = '/account/login/'; // Redireciona para segurança
}

console.log({email_input, password_input, repeat_password_input, error_message});

// --- SUBMISSÃO DO FORMULÁRIO ---
form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Cancela o reload da página

    // 1. Validação Visual (Front-end)
    let errors = [];

    // Se for página de Nova Senha
    if (password_input && repeat_password_input) {
        errors = errors.concat(getNewPassword(
            password_input, 
            repeat_password_input
        ));
    }   

    // Se for página de Recuperar Senha
    if (email_input) {
        errors = errors.concat(getForgotPassWord(
            email_input.value
        ));
    }

    // Se houver erros visuais, mostra e para aqui
    if (errors.length > 0) {
        error_message.innerText = errors.join(". ");
        error_message.style.color = "var(--color-incorrect)";
        return;
    }

    // 2. Montar dados para envio (Back-end)
    let data = {};
    let url = ''; 

    if (password_input) {
        // --- FLUXO: NOVA SENHA ---
        url = '/account/nova-senha/'; 
        
        data = {
            // Nomes exatos que o Django SetPasswordForm espera
            new_password1: password_input.value,
            new_password2: repeat_password_input.value,
            uid: uid,     // Pego lá no topo (automático)
            token: token  // Pego lá no topo (automático)
        };

    } else {
        // --- FLUXO: RECUPERAR SENHA ---
        url = '/account/recuperar-senha/';
        
        data = {
            email: email_input.value
        };
    }

    // 3. Envio via Fetch
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Sucesso (200 OK)
            if (password_input) {
                alert("Senha alterada com sucesso!");
                window.location.href = '/account/login/';
            } else {
                error_message.style.color = "green";
                error_message.innerText = result.message || "Se o e-mail existir, enviamos um link!";
                form.reset(); // Limpa o campo de email para não enviar de novo sem querer
            }
        } else {
            // Erro (400/500)
            error_message.style.color = "var(--color-incorrect)";
            
            // Tratamento de erro inteligente (Lista do Django ou Erro simples)
            if (result.errors) {
                // O Django manda erros em JSON string, precisamos converter
                try {
                    const errorData = typeof result.errors === 'string' ? JSON.parse(result.errors) : result.errors;
                    // Pega todas as mensagens de erro de todos os campos e junta
                    const errorList = Object.values(errorData).flat().map(err => err.message || err);
                    error_message.innerText = errorList.join(". ");
                } catch (e) {
                    error_message.innerText = result.errors; // Fallback se não for JSON
                }
            } else {
                error_message.innerText = result.error || result.mensagem || 'Erro ao processar.';
            }
        }
    } catch (err) {
        console.error(err);
        error_message.style.color = "var(--color-incorrect)";
        error_message.innerText = 'Erro de conexão com o servidor.';
    }
});

// --- FUNÇÕES AUXILIARES DE VALIDAÇÃO ---

function getForgotPassWord(email) { 
    let errors = [];
    if (email === '' || email == null) {
        errors.push('Email é obrigatório');
        email_input.parentElement.classList.add('incorrect');
    }
    if (!email.includes('@') || !email.includes('.')) {
        errors.push('Escreva um email válido');
        email_input.parentElement.classList.add('incorrect');
    }
    return errors; 
}

function getNewPassword(passwordInput, repeatPasswordInput) { 
    let errors = [];
    const password = passwordInput?.value || '';
    const repeatPassword = repeatPasswordInput?.value || '';

    if(password === '') {
        errors.push('Senha é obrigatória');
        passwordInput?.parentElement?.classList.add('incorrect');
    }
    if(repeatPassword === '') {
        errors.push('Repetir senha é obrigatório');
        repeatPasswordInput?.parentElement?.classList.add('incorrect');
    }
    if(password.length > 0 && password.length < 8) {
        errors.push('A senha deve ter no mínimo 8 caracteres');
        passwordInput?.parentElement?.classList.add('incorrect');
    }
    if(password && repeatPassword && password !== repeatPassword) {
        errors.push('As senhas não são iguais');
        passwordInput?.parentElement?.classList.add('incorrect');
        repeatPasswordInput?.parentElement?.classList.add('incorrect');
    }
    return errors;
}

const allInputs = [email_input, password_input, repeat_password_input].filter(input => input != null);
allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if(input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    })
});