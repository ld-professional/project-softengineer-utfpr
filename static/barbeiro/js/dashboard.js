const themeSwitch = document.getElementById('theme-switch');


let lightmode = localStorage.getItem('lightmode');


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


document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.getElementById('logout-button');

    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            
            const csrftoken = getCookie('csrftoken');
            
            
            
            fetch('/clientes/logout/', { 
                method: 'POST',
                
                headers: {
                    'X-CSRFToken': csrftoken, 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({}) 
            })
            .then(response => {
                
                
                
                
                if (response.ok) {
                    window.location.href = '/account/login'; 
                } else {
                    
                    console.error('Logout falhou com status:', response.status);
                    alert('Falha ao sair. Tente novamente. Status: ' + response.status);
                }
            })
            .catch(error => {
                
                console.error('Erro de rede:', error);
                alert('Erro de conexão.');
            });
        });
    }
});



document.addEventListener('DOMContentLoaded', function() {
    
    
    const logoutButton = document.getElementById('logout-button');
    

    
    const agendamentosButton = document.getElementById('agenda-btn');

    
    if (agendamentosButton) {
        agendamentosButton.addEventListener('click', function() {
            
            
            
            const urlDestino = '/barbeiro/agendamentos/minha-agenda/'; 
            
            
            window.location.href = urlDestino;
        });
    }


    const meusServicosButton = document.getElementById('servicos-btn');

    
    if (meusServicosButton) {
        meusServicosButton.addEventListener('click', function() {
            
            
            const urlDestino = '/barbeiro/servicos/meus-servicos/';

            
            window.location.href = urlDestino;
        });
    }



    const meusAgendamentosButton = document.getElementById('Agendamentos-btn');

    
    if (meusAgendamentosButton) {
        meusAgendamentosButton.addEventListener('click', function() {
            
            
            const urlDestino = '/barbeiro/agendamentos/';

            
            window.location.href = urlDestino;
        });
    }

    const editarPerfilButton = document.getElementById('editar-perfil-btn');

    
    if (editarPerfilButton) {
        editarPerfilButton.addEventListener('click', function() {
            
            
            const urlDestino = '/barbeiro/editar-perfil/';

            
            window.location.href = urlDestino;
        });
    }
})