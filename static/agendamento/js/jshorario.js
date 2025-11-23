const themeSwitch = document.getElementById('theme-switch');
const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevButton');
const nextBtn = document.getElementById('nextButton');

let currentDate = new Date();

const updateCalendar = () => {
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();

    const firstDay = new Date(currentYear, currentMonth, 0);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const totalDays = lastDay.getDate();
    const firstDayIndex = firstDay.getDay();
    const lastDayIndex = lastDay.getDay();

    const monthYearString = currentDate.toLocaleString
    ('pt-BR', { month: 'long', year: 'numeric' });
    const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);
    monthYearElement.textContent = capitalize(monthYearString);

    let datesHTML = '';

    for (let i = firstDayIndex; i > 0; i--) {
        const prevDate = new Date(currentYear, currentMonth, 0 - i + 1);
        datesHTML += `<div class="date inactive">${prevDate.getDate()}</div>`;
    }

    for (let i = 1; i <= totalDays; i++) {
        const date = new Date(currentYear, currentMonth, i);
        const activeClass = date.toDateString() === currentDate.toDateString() ? 'active' : '';
        datesHTML += `<div class="date ${activeClass}" data-day="${i}">${i}</div>`;
    }

    for (let i = 1; i <= (7 - lastDayIndex); i++) {
        const nextDate = new Date(currentYear, currentMonth + 1, i);
        datesHTML += `<div class="date inactive">${nextDate.getDate()}</div>`;
    }

    datesElement.innerHTML = datesHTML;

    document.querySelectorAll(".date").forEach(day => {
        day.addEventListener("click", () => {
            if (day.classList.contains("inactive")) return; // desativa meses adjacentes

            const dayNumber = parseInt(day.dataset.day);

            // Atualiza a data atual para o dia clicado
            currentDate.setDate(dayNumber);

            // Atualiza o calendário para marcar o dia ativo
            updateCalendar();

            showStaticTimes(currentDate);

            console.log(currentDate);
        });
    });
}

function showStaticTimes(date) {
    const listaHorarios = document.getElementById("listaHorarios");

    // Limpa apenas a lista de horários
    listaHorarios.innerHTML = "";

    // Horários estáticos
    const horarios = ["08:00", "09:00", "10:00", "14:00", "15:00", "16:00", "18:00"];

    const dia = date.getDate();
    const mes = date.getMonth() + 1;
    const ano = date.getFullYear();

    horarios.forEach(h => {
        listaHorarios.innerHTML += `<div class="horario">${h}</div>`;
    });
}


prevBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateCalendar();
})

nextBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateCalendar();
})

showStaticTimes(currentDate);
updateCalendar();


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