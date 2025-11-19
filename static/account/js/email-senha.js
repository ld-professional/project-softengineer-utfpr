const email_input = document.getElementById('email');
const form = document.getElementById('form');
const password_input = document.getElementById('password');
const repeat_password_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message');

const themeSwitch = document.getElementById('theme-switch');

// pega o estado atual do modo (se esstá claro ou escuro)
let lightmode = localStorage.getItem('lightmode');

console.log({email_input, password_input, repeat_password_input, error_message});

form.addEventListener('submit', async (e) => {
    e.preventDefault(); // cancela o envio padrão

    // 🔹 1. Validação
    let errors = [];

    // Página de Nova Senha
    if (password_input && repeat_password_input) {
        errors = errors.concat(getNewPassword(
            password_input, 
            repeat_password_input
        ));
    }   

    // Página de Recuperar Senha
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
        // --- FLUXO: NOVA SENHA ---
        
        // CORREÇÃO 1: Pegar o UID e TOKEN da URL do navegador
        // O link do e-mail é algo como: .../nova-senha/?uid=MQ&token=abc...
        const urlParams = new URLSearchParams(window.location.search);
        const uid = urlParams.get('uid');
        const token = urlParams.get('token');

        if (!uid || !token) {
            error_message.innerText = "Link inválido. Verifique o link no seu e-mail.";
            return;
        }

        // CORREÇÃO 2: Usar os nomes de campo que o Django (SetPasswordForm) exige q eh newpasswrd1 para a senha e a repeticao
        // sendo new psswd2
        data.new_password1 = password_input.value;
        data.new_password2 = repeat_password_input.value;
        data.uid = uid;     // Envia o ID codificado
        data.token = token; // Envia o token de segurança

        // CORREÇÃO 3: URL correta do seu urls.py
        url = '/account/nova-senha/'; 
    } else {
        // --- FLUXO: RECUPERAR SENHA ---
        data.email = email_input.value;
        // CORREÇÃO 3: URL correta do seu urls.py
        url = '/account/recuperar-senha/'; 
    }

    // 🔹 3. Envio via fetch
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                // CORREÇÃO 4: Removido o getCookie pois estamos usando @csrf_exempt
                // 'X-CSRFToken': getCookie?.('csrftoken') 
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Sucesso
            if (password_input) {
                // Se mudou a senha, avisa e manda pro login
                alert("Senha alterada com sucesso!");
                window.location.href = '/account/login/';
            } else {
                // Se pediu recuperação, mostra msg verde
                error_message.style.color = "green";
                error_message.innerText = result.message || "E-mail enviado!";
            }
        } else {
            // Erro vindo do backend
            error_message.style.color = "var(--color-incorrect)"; // Garante cor vermelha
            
            // CORREÇÃO 5: Tratar lista de erros do Django (JSON)
            if (result.errors) {
                const errorData = JSON.parse(result.errors);
                const errorList = Object.values(errorData).flat().map(err => err.message || err);
                error_message.innerText = errorList.join(". ");
            } else {
                // Erro genérico (ex: token inválido)
                error_message.innerText = result.error || 'Erro ao processar.';
            }
        }
    } catch (err) {
        console.error(err);
        error_message.innerText = 'Erro de conexão com o servidor.';
    }
});


// darkmode (Mantido igual)
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

function getForgotPassWord(email) { 
    let errors = [];

    // se o email é vazio
    if (email === '' || email == null) {
        errors.push('Email é obrigatório');
        email_input.parentElement.classList.add('incorrect');
    }

    // se o email é um email
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

    // se a senha não é vazia
    if(password === '') {
        errors.push('Senha é obrigatória');
        passwordInput?.parentElement?.classList.add('incorrect');
    }

    // se a senha repetida não é vazia
    if(repeatPassword === '') {
        errors.push('Repetir senha é obrigatório');
        repeatPasswordInput?.parentElement?.classList.add('incorrect');
    }

    // se a senha tem no mínimo 8 caracteres
    if(password.length > 0 && password.length < 8) {
        errors.push('A senha deve ter no mínimo 8 caracteres');
        passwordInput?.parentElement?.classList.add('incorrect');
    }

    // se a senha e a senha repetida são iguais
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
})