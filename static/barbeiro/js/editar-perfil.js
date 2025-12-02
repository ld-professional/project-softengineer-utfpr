const form = document.getElementById('form-editar');
const username_input = document.getElementById('username');
const email_input = document.getElementById('email');
const telefone_input = document.getElementById('telefone');
const foto_input = document.getElementById('foto-input');
const preview_img = document.getElementById('preview-img');
const error_message = document.getElementById('error-message');
const themeSwitch = document.getElementById('theme-switch');

// Senhas
const senha_atual_input = document.getElementById('senha_atual');
const nova_senha_input = document.getElementById('nova_senha');

// --- DARK/LIGHT MODE ---
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
        if (lightmode !== 'active') enableLightMode();
        else disableLightMode();
    });
}

// --- PREVIEW IMAGEM ---
if (foto_input) {
    foto_input.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) { preview_img.src = e.target.result; }
            reader.readAsDataURL(e.target.files[0]);
        }
    });
}

// --- MÁSCARA TELEFONE ---
if (telefone_input) {
    telefone_input.addEventListener('input', function(e) {
        let x = e.target.value.replace(/\D/g, '');
        if(x.length > 11) x = x.slice(0,11); 
        x = x.replace(/^(\d{2})(\d)/, '($1) $2');
        x = x.replace(/(\d)(\d{4})$/, '$1-$2');         
        e.target.value = x;
    });
}

// --- ENVIO DO FORMULÁRIO ---
// --- ENVIO DO FORMULÁRIO ---
if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        let errors = [];
        error_message.innerText = ""; 

        // Validações Visuais (Front-end)
        if (!username_input.value) {
            errors.push('Nome de usuário é obrigatório');
            username_input.parentElement.classList.add('incorrect');
        }
        if (!email_input.value) {
            errors.push('Email é obrigatório');
            email_input.parentElement.classList.add('incorrect');
        }
        
        // Verifica tamanho visual (com máscara tem 15 chars: (XX) XXXXX-XXXX)
        // Ou verifica se tem 11 números
        let numerosTelefone = telefone_input.value.replace(/\D/g, '');
        if (numerosTelefone.length !== 11) {
            errors.push('Telefone inválido (precisa de 11 dígitos)');
            telefone_input.parentElement.classList.add('incorrect');
        }

        // Validação Senha (Mantida a lógica correta)
        if (!senha_atual_input.value) {
            errors.push('Digite sua senha atual para confirmar a alteração');
            senha_atual_input.parentElement.classList.add('incorrect');
        }

        if (nova_senha_input.value && nova_senha_input.value.length < 8) {
            errors.push('A nova senha deve ter no mínimo 8 caracteres');
            nova_senha_input.parentElement.classList.add('incorrect');
        }

        if (errors.length > 0) {
            error_message.innerText = errors.join(". ");
            return;
        }

        // --- AQUI ESTÁ A CORREÇÃO MÁGICA ---
        const formData = new FormData(form);
        
        // Pega o valor formatado "(43) 9..."
        const telefoneSujo = formData.get('telefone');
        // Limpa tudo que não é número
        const telefoneLimpo = telefoneSujo.replace(/\D/g, '');
        // Atualiza o dado que será enviado para o servidor
        formData.set('telefone', telefoneLimpo);

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData // Agora vai com o telefone limpo (11 dígitos)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Perfil atualizado com sucesso!');
                if (senha_atual_input) senha_atual_input.value = '';
                if (nova_senha_input) nova_senha_input.value = '';
                window.location.reload();
            } else {
                const msg = result.error || 'Erro desconhecido ao atualizar.';
                error_message.innerText = msg;
                console.log("Erro retornado:", result);
            }

        } catch (err) {
            console.error(err);
            error_message.innerText = 'Erro de conexão com o servidor.';
        }
    });
}

const inputs = [username_input, email_input, telefone_input, senha_atual_input, nova_senha_input];
inputs.forEach(input => {
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