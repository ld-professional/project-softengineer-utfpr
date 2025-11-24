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

const slides = document.querySelectorAll(".slide");
const nomeBarbeiro = document.getElementById("nomeBarbeiro");

// coloque os nomes na mesma ordem das imagens
const nomes = ["John China", "Lázaro"];

let index = 0;

function atualizarSlide(novoIndex) {
    slides[index].classList.remove("ativo");
    index = novoIndex;
    slides[index].classList.add("ativo");

    // altera o nome conforme a imagem atual
    nomeBarbeiro.textContent = nomes[index];
}

document.getElementById("next").addEventListener("click", () => {
    atualizarSlide((index + 1) % slides.length);
});

document.getElementById("prev").addEventListener("click", () => {
    atualizarSlide((index - 1 + slides.length) % slides.length);
});

const btnVoltar = document.getElementById('voltar-dash-btn');

if (btnVoltar) {
    btnVoltar.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/agendamentos/escolher_servico/'; 
    });
}

const btnInicio = document.getElementById('inicio-dash-tbm-btn');

if (btnInicio) {
    btnInicio.addEventListener('click', function() {
        // Aqui tem que ser o caminho exato que está no navegador
        window.location.href = '/clientes/dashboard/'; 
    });
}