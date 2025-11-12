const form = document.getElementById('form'); 
const username_input = document.getElementById('username');
const email_input = document.getElementById('email');
const password_input = document.getElementById('password');
const repeatPassword_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message'); 
const themeSwitch = document.getElementById('theme-switch');

let lightmode = localStorage.getItem('lightmode');

form.addEventListener('submit', async (e) => {
    e.preventDefault(); // cancela o envio padrão

    // 🔹 1. Validação
    let errors = [];

    if (username_input) {
        // Formulário de cadastro
        errors = getSignUpFormErrors(
            username_input.value,
            email_input.value,
            password_input.value,
            repeatPassword_input.value
        );
    } else {
        // Formulário de login
        errors = getLoginFormErrors(
            email_input.value,
            password_input.value
        );
    }

    // Se houver erros, mostra e para o fluxo
    if (errors.length > 0) {
        error_message.innerText = errors.join(". ");
        return;
    }

    // 🔹 2. Montar dados para envio
    let data = {};
    let url = "";

    if (username_input) {
        // Cadastro
        data.username = username_input.value;
        data.email = email_input.value;
        data.password = password_input.value;
        data.repeat_password = repeatPassword_input.value;
        url = '/account/signup/'; 
    } else {
        // Login
        data.email = email_input.value;
        data.password = password_input.value;
        url = '/account/login/';
    }

    // 🔹 3. Envio via fetch
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // se usar Django
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Sucesso → redireciona ou faz algo
            window.location.href = result.redirect_url || '/cliente/dashboard'; 
        } else {
            // Erro vindo do backend
            error_message.innerText = result.error || 'Erro ao tentar logar.';
        }
    } catch (err) {
        console.error(err);
        error_message.innerText = 'Erro de conexão com o servidor.';
    }
});




function getSignUpFormErrors(username, email, password, repeatPassword) { 
    let errors = [];

    if (username === '' || username == null) {
        errors.push('Nome de usuário é obrigatório');
        username_input.parentElement.classList.add('incorrect');
    }
    if (email === '' || email == null) {
        errors.push('Email é obrigatório');
        email_input.parentElement.classList.add('incorrect');
    }

    if (!email.includes('@') || !email.includes('.')) {
        errors.push('Escreva um email válido');
        email_input.parentElement.classList.add('incorrect');
    }

    if (password === '' || password == null) {
        errors.push('Senha é obrigatória');
        password_input.parentElement.classList.add('incorrect');
    }
    if (repeatPassword === '' || repeatPassword == null) {
        errors.push('Repetir senha é obrigatório');
        repeatPassword_input.parentElement.classList.add('incorrect');
    }

    if(password.length < 8) {
        errors.push('A senha deve ter no mínimo 8 caracteres');
        password_input.parentElement.classList.add('incorrect');
    }

    if (password !== repeatPassword) {
        errors.push('As senhas não são iguais');
        password_input.parentElement.classList.add('incorrect');
        repeatPassword_input.parentElement.classList.add('incorrect');
    }


    return errors;
}

function getLoginFormErrors(email, password) {
    let errors = [];

    if (email === '' || email == null) {
        errors.push('Email é obrigatório');
        email_input.parentElement.classList.add('incorrect');
    }
    
    if (!email.includes('@') || !email.includes('.')) {
        errors.push('Escreva um email válido');
        email_input.parentElement.classList.add('incorrect');
    }

    if (password === '' || password == null) {
        errors.push('Senha é obrigatória');
        password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}



const allInputs = [username_input, email_input, password_input, repeatPassword_input].filter(input => input != null);
allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if(input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }

    })
})

const enanableLightMode = () => {
    document.body.classList.add('lightmode');
    localStorage.setItem('lightmode', 'active');
};
const disableLightMode = () => {
    document.body.classList.remove('lightmode');
    localStorage.setItem('lightmode', null);
};

if (lightmode === 'active') {
    enanableLightMode();
}

themeSwitch.addEventListener('click', () => {
    lightmode = localStorage.getItem('lightmode');
    if (lightmode !== 'active') {
        enanableLightMode();
    } else {
        disableLightMode();
    }
});
