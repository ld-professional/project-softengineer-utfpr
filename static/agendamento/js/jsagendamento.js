const themeSwitch = document.getElementById('theme-switch');

// pega o estado atual do modo (se esstá claro ou escuro)
let lightmode = localStorage.getItem('lightmode');

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

themeSwitch.addEventListener('click', () => {
    lightmode = localStorage.getItem('lightmode');
    if (lightmode !== 'active') {
        enableLightMode();
    } else {
        disableLightMode();
    }
});

const blocos = document.querySelectorAll('.link-bloco');
let blocoSelecionado = null;

blocos.forEach(bloco => {
    bloco.addEventListener('click', () => {

        // Remove seleção anterior
        blocos.forEach(b => b.classList.remove('selecionado'));

        // Adiciona seleção ao clicado
        bloco.classList.add('selecionado');

        // Pega o título do serviço (conteúdo do <h2>)
        blocoSelecionado = bloco.querySelector('h2').textContent;
    });
});


const btnVoltar = document.getElementById('voltar-dash-btn');

if (btnVoltar) {
    btnVoltar.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/dashboard/'; 
    });
}

const btnInicio = document.getElementById('inicio-dash-tbm-btn');

if (btnInicio) {
    btnInicio.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/dashboard/'; 
    });
}

