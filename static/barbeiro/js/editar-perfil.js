// --- 1. SELEÇÃO DE ELEMENTOS ---
const fileInput = document.getElementById('foto_perfil');
const uploadButton = document.getElementById('btn-upload-photo');
const profileImg = document.getElementById('profile-img');
const formPerfil = document.getElementById('form-perfil');
const errorMessage = document.getElementById('error-message');
const btnSalvar = document.getElementById('btn-salvar');
const themeSwitch = document.getElementById('theme-switch');


// --- 2. FUNÇÃO AUXILIAR: PRÉ-VISUALIZAÇÃO DA FOTO ---
// Carrega a imagem localmente assim que o usuário seleciona um arquivo
function handleFilePreview() {
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            // Atualiza o src da tag <img> para a pré-visualização
            profileImg.src = e.target.result;
        };
        
        // Lê o arquivo como URL de dados (Base64)
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// --- 3. EVENTO DE CLIQUE DO BOTÃO DE UPLOAD ---
// Faz com que o clique no botão visual acione o clique no input file escondido
if (uploadButton && fileInput) {
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Escuta a mudança no input file (quando o arquivo é escolhido)
    fileInput.addEventListener('change', handleFilePreview);
}


// --- 4. FUNÇÃO AUXILIAR: CSRF TOKEN (Necessária para segurança do Django) ---
function obterTokenCsrf(name) {
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


// --- 5. SUBMISSÃO DO FORMULÁRIO ---
if (formPerfil && btnSalvar) {
    formPerfil.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        errorMessage.textContent = ''; 
        
        // Usa FormData para enviar todos os campos, incluindo o arquivo da foto
        const formData = new FormData(formPerfil);
        
        btnSalvar.disabled = true;
        btnSalvar.textContent = "Salvando...";

        try {
            // A rota 'editar-perfil/' deve aceitar requisições POST/PATCH
            const resposta = await fetch(formPerfil.action, {
                method: 'POST', 
                headers: {
                    'X-CSRFToken': obterTokenCsrf('csrftoken')
                    // NÃO inclua 'Content-Type' ao enviar FormData com arquivos
                },
                body: formData
            });

            const dados = await resposta.json();

            if (resposta.ok) {
                // Sucesso
                Swal.fire({
                    icon: "success",
                    title: "Perfil Atualizado!",
                    text: dados.mensagem || "Suas informações foram salvas com sucesso."
                });
                // Recarrega a página para mostrar a nova foto/dados
                setTimeout(() => { window.location.reload(); }, 1500); 

            } else {
                // Erro (Ex: Senha atual incorreta, validação de campo)
                let msg = dados.erro || "Houve um erro ao tentar salvar os dados.";
                Swal.fire({
                    icon: "error",
                    title: "Erro na Edição",
                    text: msg
                });
                errorMessage.textContent = msg; 
            }

        } catch (erro) {
            console.error('Erro de conexão ou JS:', erro);
            Swal.fire({
                icon: "error",
                title: "Falha de Conexão",
                text: "Não foi possível conectar ao servidor para salvar."
            });
            errorMessage.textContent = "Falha de conexão.";
        }
        
        // Reabilita o botão
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Alterações";
    });
}


// --- 6. TEMA DARK/LIGHT (Reutilização da lógica do tema) ---
const htmlElement = document.documentElement;

const toggleLightMode = (enable) => {
    if (enable) {
        htmlElement.classList.add('lightmode');
        localStorage.setItem('lightmode', 'active');
    } else {
        htmlElement.classList.remove('lightmode');
        localStorage.removeItem('lightmode');
    }
};

if (themeSwitch) {
    themeSwitch.addEventListener('click', () => {
        const isLightModeActive = htmlElement.classList.contains('lightmode');
        toggleLightMode(!isLightModeActive);
    });
}