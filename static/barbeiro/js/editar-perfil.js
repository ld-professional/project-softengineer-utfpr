// Obtém elementos do DOM
const form = document.getElementById('form-editar');
const username_input = document.getElementById('username');
const email_input = document.getElementById('email');
const telefone_input = document.getElementById('telefone');
const foto_input = document.getElementById('foto-input');
const preview_img = document.getElementById('preview-img');
const error_message = document.getElementById('error-message');
const themeSwitch = document.getElementById('theme-switch');

// --- LÓGICA DE DARK/LIGHT MODE (Mantida igual ao validation.js) ---
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

if (themeSwitch) {
    themeSwitch.addEventListener('click', () => {
        lightmode = localStorage.getItem('lightmode');
        if (lightmode !== 'active') {
            enableLightMode();
        } else {
            disableLightMode();
        }
    });
}

// --- PRÉ-VISUALIZAÇÃO DA IMAGEM ---
if (foto_input) {
    foto_input.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview_img.src = e.target.result;
            }
            reader.readAsDataURL(e.target.files[0]);
        }
    });
}

// --- MÁSCARA DE TELEFONE ---
if (telefone_input) {
    telefone_input.addEventListener('input', function(e) {
        let x = e.target.value.replace(/\D/g, '');
        if(x.length > 11) x = x.slice(0,11); 
        x = x.replace(/^(\d{2})(\d)/, '($1) $2');
        x = x.replace(/(\d)(\d{4})$/, '$1-$2');         
        e.target.value = x;
    });
}

// --- ENVIO DO FORMULÁRIO (FETCH COM FORMDATA) ---
if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        let errors = [];

        // Validações
        if (!username_input.value) {
            errors.push('Nome de usuário é obrigatório');
            username_input.parentElement.classList.add('incorrect');
        }
        if (!email_input.value) {
            errors.push('Email é obrigatório');
            email_input.parentElement.classList.add('incorrect');
        }
        if (telefone_input.value.replace(/\D/g, '').length !== 11) {
            errors.push('Telefone inválido');
            telefone_input.parentElement.classList.add('incorrect');
        }

        if (errors.length > 0) {
            error_message.innerText = errors.join(". ");
            return;
        }

        // PREPARAÇÃO DOS DADOS (O Segredo para enviar Foto)
        // FormData pega todos os inputs do form automaticamente, inclusive arquivos
        const formData = new FormData(form);

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    // IMPORTANTE: NÃO definir Content-Type aqui. 
                    // O navegador define automaticamente como multipart/form-data com o boundary correto.
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData // Envia o FormData direto
            });

            const result = await response.json();

            if (response.ok) {
                // Sucesso
                alert(result.message || 'Perfil atualizado!');
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else {
                    window.location.reload();
                }
            } else {
                // Erro do Django
                error_message.innerText = result.error || 'Erro ao atualizar.';
            }

        } catch (err) {
            console.error(err);
            error_message.innerText = 'Erro de conexão com o servidor.';
        }
    });
}

// Remove classe de erro ao digitar
[username_input, email_input, telefone_input].forEach(input => {
    if(input) {
        input.addEventListener('input', () => {
            if(input.parentElement.classList.contains('incorrect')) {
                input.parentElement.classList.remove('incorrect');
                error_message.innerText = '';
            }
        });
    }
});

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