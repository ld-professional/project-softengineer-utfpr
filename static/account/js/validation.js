// --- SELEÇÃO DE ELEMENTOS ---
const form = document.getElementById('form'); 
const username_input = document.getElementById('username'); // Só existe no cadastro
const email_input = document.getElementById('email');       // Só existe no cadastro
const telefone_input = document.getElementById('telefone'); // Só existe no cadastro
const identifier_input = document.getElementById('identifier'); // Só existe no Login
const password_input = document.getElementById('password');
const repeatPassword_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message'); 
const themeSwitch = document.getElementById('theme-switch');

// --- MODO ESCURO/CLARO ---
let lightmode = localStorage.getItem('lightmode');

const enableLightMode = () => {
    document.body.classList.add('lightmode');
    localStorage.setItem('lightmode', 'active');
};
const disableLightMode = () => {
    document.body.classList.remove('lightmode');
    localStorage.setItem('lightmode', null);
};

if (lightmode === 'active') enableLightMode();

themeSwitch.addEventListener('click', () => {
    lightmode = localStorage.getItem('lightmode');
    if (lightmode !== 'active') {
        enableLightMode();
    } else {
        disableLightMode();
    }
});


// 1. Função para ler o cookie que o @ensure_csrf_cookie da account view login por exemplo ou cadastro mandou eh um 
// algorimto copia e cola da internet
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


// --- SIMPLIFICAÇÃO DO TELEFONE (Só Números, Max 11) ---
if (telefone_input) {
    telefone_input.addEventListener('input', function(e) {
        // Remove tudo que não for número
        let limpo = e.target.value.replace(/\D/g, '');
        
        // Trava em 11 dígitos (DDD + Número)
        if (limpo.length > 11) limpo = limpo.slice(0, 11);
        
        e.target.value = limpo;
    });
}

// --- SUBMISSÃO DO FORMULÁRIO ---
form.addEventListener('submit', async (e) => {
    e.preventDefault(); 

    let errors = [];
    let data = {};
    let url = "";

    // --- DECISÃO: É CADASTRO OU LOGIN? ---
    if (username_input) {
        // === MODO CADASTRO ===
        errors = getSignUpFormErrors(
            username_input.value,
            email_input.value,
            password_input.value,
            repeatPassword_input.value,
            telefone_input.value
        );

        data = {
            username: username_input.value,
            email: email_input.value,
            telefone: telefone_input.value, // Vai enviar só números (ex: 41999998888)
            password: password_input.value,
            password_confirm: repeatPassword_input.value // Nome igual ao do forms.py
        };
        url = '/account/signup/';

    } else {
        // === MODO LOGIN ===
        errors = getLoginFormErrors(
            identifier_input.value,
            password_input.value
        );

        // Envia 'identifier' e o Django descobre se é email ou telefone no backend
        data = {
            identifier: identifier_input.value,
            password: password_input.value
        };
        url = '/account/login/';
    }

    // Se tiver erro visual, para aqui
    if (errors.length > 0) {
        error_message.innerText = errors.join(". ");
        error_message.style.color = "var(--color-incorrect)";
        return;
    }

    // Envio para o servidor
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // <--- O CRÁCHÁ DE SEGURANÇA
             },
            body: JSON.stringify(data)
            
        });

        const result = await response.json();

        if (response.ok) {
            // Sucesso!
            window.location.href = result.redirect_url || '/cliente/dashboard'; 
        } else {
            // Erro do Backend
            error_message.style.color = "var(--color-incorrect)";
            
            if (result.errors) {
                // Tenta ler a lista de erros do Django
                try {
                    const errorData = typeof result.errors === 'string' ? JSON.parse(result.errors) : result.errors;
                    const errorList = Object.values(errorData).flat().map(err => err.message || err);
                    error_message.innerText = errorList.join(". ");
                } catch (e) {
                    error_message.innerText = result.errors;
                }
            } else {
                // Erro simples
                error_message.innerText = result.error || result.mensagem || 'Erro ao processar.';
            }
        }
    } catch (err) {
        console.error(err);
        error_message.innerText = 'Erro de conexão com o servidor.';
    }
});

// --- FUNÇÕES DE VALIDAÇÃO ---

function getSignUpFormErrors(username, email, password, repeatPassword, telefone) { 
    let errors = [];

    if (!username) errors.push('Nome de usuário é obrigatório');
    
    if (!email) {
        errors.push('Email é obrigatório');
    } else if (!email.includes('@')) {
        errors.push('Email inválido');
    }

    // Validação simples de tamanho do telefone
    if (!telefone || telefone.length !== 11) {
        errors.push('Telefone deve ter 11 dígitos (DDD + Número)');
        telefone_input?.parentElement.classList.add('incorrect');
    }

    if (!password) {
        errors.push('Senha é obrigatória');
    } else if (password.length < 8) {
        errors.push('A senha deve ter no mínimo 8 caracteres');
    }

    if (password !== repeatPassword) {
        errors.push('As senhas não são iguais');
        repeatPassword_input?.parentElement.classList.add('incorrect');
    }

    // Marca visualmente os campos com erro
    if(errors.length > 0) {
        if(!username) username_input.parentElement.classList.add('incorrect');
        if(!email || !email.includes('@')) email_input.parentElement.classList.add('incorrect');
        if(!password || password.length < 8) password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

function getLoginFormErrors(identifier, password) {
    let errors = [];
    
    if (!identifier) {
        errors.push('Digite seu E-mail, Telefone ou Usuário');
        identifier_input.parentElement.classList.add('incorrect');
    }
    if (!password) {
        errors.push('Senha é obrigatória');
        password_input.parentElement.classList.add('incorrect');
    }
    return errors;
}

// Limpa a classe de erro (vermelho) quando o usuário começa a digitar
const allInputs = [username_input, email_input, password_input, repeatPassword_input, identifier_input, telefone_input].filter(input => input != null);

allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if(input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    })
});