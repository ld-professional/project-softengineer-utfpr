const form = document.getElementById('form'); 
const username_input = document.getElementById('username');
const email_input = document.getElementById('email');
const password_input = document.getElementById('password');
const repeatPassword_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message'); 

form.addEventListener('submit', (e) => {

    let errors = [];

    if(username_input) {
        errors = getSignUpFormErrors(username_input.value, email_input.value, password_input.value, repeatPassword_input.value);
    }
    else {
        errors = getLoginFormErrors(email_input.value, password_input.value);
    }

    if(errors.length > 0) {
        e.preventDefault();
        error_message.innerText = errors.join(". ")
    }
})
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


