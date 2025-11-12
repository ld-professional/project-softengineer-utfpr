const sections = document.querySelectorAll('section');
const themeSwitch = document.getElementById('theme-switch');

let lightmode = localStorage.getItem('lightmode');

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');

                themeSwitch.setAttribute('data-section', entry.target.id);

            } else {
                entry.target.classList.remove('active');
            }
        });
    },
    { threshold: 0.3}
);

sections.forEach(section => {
    observer.observe(section);
});

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

    