// Recebe os dados do HTML pelo ID
const form = document.getElementById('form'); 
const username_input = document.getElementById('username');
const email_input = document.getElementById('email');
const indentifier_input = document.getElementById('indentifier');
const telefone_input = document.getElementById('telefone');
const password_input = document.getElementById('password');
const repeatPassword_input = document.getElementById('repeat-password');
const error_message = document.getElementById('error-message'); 
const themeSwitch = document.getElementById('theme-switch');

// pega o estado atual do modo (se esstá claro ou escuro)
let lightmode = localStorage.getItem('lightmode');






// Verifica se a variável 'form' aponta para algo real no HTML.
// Se 'form' for null (ou seja, não estamos na página de login/cadastro e o getElementById falhou),
// esse IF impede que o código tente acessar memória inválida e trave o site. 
// (Similar a checar se um ponteiro é NULL em C antes de usar).
if (form) {

    // Adiciona um "Ouvinte" (Listener). Fica esperando o evento 'submit' (clicar no botão).
    // 'async' avisa que dentro dessa função teremos operações lentas (rede) e precisaremos pausar (await).
    form.addEventListener('submit', async (e) => {

        // "Prevent Default": Impede o navegador de recarregar a página inteira (comportamento padrão do HTML).
        // Nós queremos controlar o envio via JavaScript silenciosamente, sem piscar a tela.
        e.preventDefault();

        // 🔹 1. VALIDAÇÃO LOCAL
        // Cria um Vetor Dinâmico (Array) vazio para armazenar as strings de erro.
        // Em C++, seria algo como: std::vector<string> errors;
        let errors = [];

        // Lógica de decisão: Se o ponteiro 'username_input' existe (não é null),
        // então o HTML tem campo de usuário, logo é CADASTRO. Senão, é LOGIN.
        if (username_input) {
            // Chama validação de cadastro e preenche o vetor 'errors'
            errors = getSignUpFormErrors(
                username_input.value,
                email_input.value,
                password_input.value,
                repeatPassword_input.value,
                telefone_input
            );
        } else {
            // Chama validação de login e preenche o vetor 'errors'
            errors = getLoginFormErrors(
                indentifier_input.value,
                password_input.value
            );
        }

        // Se o vetor não estiver vazio (tamanho > 0), temos erros.
        if (errors.length > 0) {
            // .join(". ") percorre o vetor, pega todas as strings e junta numa só, separando por ponto.
            // Exibe no HTML e dá 'return' para MATAR a função aqui. O código para e não envia nada.
            error_message.innerText = errors.join(". ");
            return;
        }

        // 🔹 2. PREPARAÇÃO DOS DADOS (STRUCT)
        // Cria um objeto vazio para preencher com os dados que vamos enviar.
        let data = {};
        let url = ""; // String vazia para guardar o endereço de destino

        if (username_input) {
            // Preenche struct para Cadastro
            data.username = username_input.value;
            data.email = email_input.value;
            data.telefone = telefone_input.value;
            data.password = password_input.value;
            // nome das variaveis aqui  deve ser igual ao do account/forms.py
             data.password_confirm = repeatPassword_input.value;
            url = '/account/signup/'; // Rota do Django para criar conta
        } else {
            // Preenche struct para Login
            data.identifier = indentifier_input.value; // Usando chave com erro de digitação conforme seu HTML
            data.password = password_input.value;
            url = '/account/login/'; // Rota do Django para logar
        }

        // 🔹 3. ENVIO (FETCH)
        // Bloco TRY/CATCH: Tenta executar código perigoso (conectar na internet).
        // Se a internet cair ou servidor sumir, ele pula pro 'catch' em vez de travar o programa.
        try {
            // FETCH: Função que faz a requisição HTTP (bate na porta do servidor).
            // 'await': Manda o JavaScript PAUSAR a execução nesta linha e esperar o servidor responder.
            // Sem 'await', o código continuaria rodando sem ter a resposta na mão (ponteiro inválido/undefined).
            const response = await fetch(url, {
                method: 'POST', // Método de envio
                headers: {
                    'Content-Type': 'application/json', // Avisa que o corpo é JSON
                    'X-CSRFToken': getCookie('csrftoken') // Anexa o Token de segurança do Django
                },
                body: JSON.stringify(data) // Serializa: Transforma o Objeto JS em Texto JSON puro
            });

            // O servidor respondeu! Mas a resposta vem bruta.
            // 'response.json()' lê o texto da resposta e Desserializa (transforma de volta em Objeto JS).
            // Também precisa de 'await' porque ler o corpo da resposta leva tempo.
            const result = await response.json();

            // response.ok verifica o código HTTP (200 = Sucesso, 400/500 = Erro)
            if (response.ok) {
                // SUCESSO:
                // window.location.href é o comando para o navegador carregar outra URL.
                // Se o backend mandou 'redirect_url', vai pra lá. Senão, vai pro dashboard padrão.
                window.location.href = result.redirect_url || '/cliente/dashboard'; 
                } else {
                // Se o Django mandou lista de erros (validação do form)
                if (result.errors) {
                    // 1. Pega os valores (ex: arrays de erros)
                    // 2. 'flat()' junta tudo num array só
                    // 3. 'map' PEGA SÓ O TEXTO DA MENSAGEM (Isso resolve o [object Object])
                    // 4. 'join' junta os textos com ponto final
                    const listaErros = Object.values(result.errors)
                        .flat()
                        .map(erro => erro.message || erro) // <--- O SEGREDO ESTÁ AQUI
                        .join(". ");
                    
                    error_message.innerText = listaErros;
                } 
                // Se for erro genérico
                else {
                    error_message.innerText = result.error || 'Erro desconhecido.';
                }
            }
        } catch (err) {
            // CATCH (ERRO CRÍTICO):
            // Só cai aqui se falhar a conexão física (DNS, Sem Internet, Servidor Offline).
            // 'err' é a variável que o navegador preenche com os detalhes técnicos do erro.
            console.error(err);
            error_message.innerText = 'Erro de conexão com o servidor.';
        }
    });
}








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

// Fução que indentidica se existe ou não erro nos campos de cadastro
function getSignUpFormErrors(username, email, password, repeatPassword, telefone) { 
    let errors = [];

    // nome de usuário vazio
    if (username === '' || username == null) {
        errors.push('Nome de usuário é obrigatório');
        username_input.parentElement.classList.add('incorrect');
    }

    // (ADICIONADO) Verifica se telefone existe antes de validar
    if (telefone && telefone.value.replace(/\D/g, '').length !== 11) {
        errors.push('Telefone deve ter 11 dígitos');
        telefone.parentElement.classList.add('incorrect');
    }   

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

    // se a senha não é vazia
    if (password === '' || password == null) {
        errors.push('Senha é obrigatória');
        password_input.parentElement.classList.add('incorrect');
    }

    // se a senha repetida não é vazia
    if (repeatPassword === '' || repeatPassword == null) {
        errors.push('Repetir senha é obrigatório');
        repeatPassword_input.parentElement.classList.add('incorrect');
    }

    // se a senha tem no minimo 8 caracteres
    if(password.length < 8) {
        errors.push('A senha deve ter no mínimo 8 caracteres');
        password_input.parentElement.classList.add('incorrect');
    }

    // se a senha e a senha repetida são iguais
    if (password !== repeatPassword) {
        errors.push('As senhas não são iguais');
        password_input.parentElement.classList.add('incorrect');
        repeatPassword_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

// Fução que indentidica se existe ou não erro nos campos de login
function getLoginFormErrors(indentifier, password) {
    let errors = [];

    // se o indentificador é vazio
    if (indentifier === '' || indentifier == null) {
        errors.push('Um identificador é obrigatório');
        indentifier_input.parentElement.classList.add('incorrect');
    }

    // se a senha é vazia
    if (password === '' || password == null) {
        errors.push('Senha é obrigatória');
        password_input.parentElement.classList.add('incorrect');
    }

    return errors;
}

// (ADICIONADO) O if abaixo é essencial: Se não tiver telefone (Login), o código pula e não trava.
if (telefone_input) {
    // limita o que o campo de telefone recebe para abenas numeros e formata para numero de telefone brasileiro
    telefone_input.addEventListener('input', function(e) {
        let x = e.target.value.replace(/\D/g, '');
        if(x.length > 11) x = x.slice(0,11); 
        
        x = x.replace(/^(\d{2})(\d)/, '($1) $2');
        x = x.replace(/(\d)(\d{4})$/, '$1-$2');         

        e.target.value = x;
    });
}

// fica atualizando o erro, para verificar se ele foi corrigido ou não
const allInputs = [username_input, email_input, password_input, repeatPassword_input, indentifier_input, telefone_input].filter(input => input != null);
allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if(input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect');
            error_message.innerText = '';
        }
    })
})

// (ADICIONADO) Função obrigatória para o Django aceitar o POST
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
// este getcookie hechamado na hora de enviar json pro servidor, o que ocorre eh o seguinte, o usuario digita a url,
// o navegador envia um json co ma url q vc digitou pro servidor, que chega em urls.py faz o roetametn oate a views.py correta
//ela recebe, e ve if == GET retorna entao um HTMl + json com o token crfs, e na proxiam vez q chamar este url mas sendo por POST
// logo ele verifica se tem o token, se tiver, entao o post pode continaur sendo processado na views.py...
// ou seja em emetodo GET, mesmo q na views.py tem o decorator em cima da def, ela so eh para qndo vc esta tratando um 
// rquest.method != GET
