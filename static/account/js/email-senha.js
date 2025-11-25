const email_input = document.getElementById('email');
const form = document.getElementById('form');
const password_input = document.getElementById('password');
// No seu HTML o ID é 'repeat-password'
const repeat_password_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message');
const themeSwitch = document.getElementById('theme-switch');

// pega o estado atual do modo (se esstá claro ou escuro)

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

// --- Lógica de Envio ---

form.addEventListener('submit', async (e) => {
    e.preventDefault(); // cancela o envio padrão

    // 🔹 1. Validação
    let errors = [];

    // Se tem campo de senha, estamos na página de Nova Senha
    if (password_input && repeat_password_input) {
        errors = errors.concat(getNewPassword(
            password_input, 
            repeat_password_input
        ));
    }   

    // Se tem campo de email, estamos na página de Recuperar Senha
    if (email_input) {
        errors = errors.concat(getForgotPassWord(
            email_input.value
        ));
    }

    // Se houver erros, mostra e para o fluxo
    if (errors.length > 0) {
        error_message.innerText = errors.join(". ");
        return;
    }

    // 🔹 2. Montar dados para envio
    let data = {};
    let url = ''; 

    if (password_input) {
        //Envia as duas senhas com os nomes do Django ---
        data.new_password1 = password_input.value;
        data.new_password2 = repeat_password_input.value;
        
        url = window.location.href; 

    } else {


        
        /* EXPLICACAO IMPORTANTE (TOKEN DA URL):
           O Django enviou um link pro email do usuario tipo: .../reset/UID/TOKEN/
           - UID: Identifica quem é o usuário (ex: Joao).
           - TOKEN DA URL: É a permissão temporária pra mudar a senha.
           
           Como o JavaScript sabe pra onde enviar?
           Usamos 'window.location.href'. Isso pega o endereço completo que está 
           na barra do navegador agora (incluindo o UID e o TOKEN).
           
           Ao enviar o POST para essa mesma URL, o Django lê o UID/TOKEN lá no backend,
           confirma que é válido e altera a senha. O Session ID não é usado aqui
           porque o usuário geralmente não está logado.
        */

        // --- Lógica de Recuperar Senha ---
        data.email = email_input.value;
        // URL definida no seu urls.py para receber o email e enviar o link
        url = '/account/esqueceu-senha/';
    }

    // 🔹 3. Envio via fetch
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
            alert(result.message || "Sucesso!"); 
            // Redireciona para o login após o sucesso
            window.location.href = '/account/login/'; 
        } else {
            // --- CORREÇÃO AQUI ---
            // O Python pode mandar 'error' (string) ou 'errors' (objeto do Django Form)
            
            if (result.error) {
                // Erro simples (ex: "Email inválido")
                error_message.innerText = result.error;
            } 
            else if (result.errors) {
                // Erros de validação do Django (ex: Senha muito curta)
                // O formato vem assim: { "new_password1": ["A senha é muito parecida com o usuário"] }
                
                // Pega a primeira mensagem de erro que encontrar
                const primeiraChave = Object.keys(result.errors)[0];
                const mensagemErro = result.errors[primeiraChave][0];
                
                error_message.innerText = mensagemErro;
            } 
            else {
                error_message.innerText = 'Ocorreu um erro desconhecido.';
            }
        }
    } catch (err) {
        console.error(err);
        error_message.innerText = 'Erro de conexão com o servidor.';
    }
});

// --- Funções Auxiliares ---

function getForgotPassWord(email) { 
    let errors = [];
    if (!email) {
        errors.push('Email é obrigatório');
        if(email_input) email_input.parentElement.classList.add('incorrect');
    }
    if (email && (!email.includes('@') || !email.includes('.'))) {
        errors.push('Escreva um email válido');
        if(email_input) email_input.parentElement.classList.add('incorrect');
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

// Limpar erros visuais ao digitar
const allInputs = [email_input, password_input, repeat_password_input].filter(input => input != null);
allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if(input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    })
});

// Função getCookie (Essencial para o Django aceitar o POST)
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
