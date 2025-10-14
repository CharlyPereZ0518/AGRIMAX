document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('toggle-dark');
    const label = document.getElementById('darkmode-label');

    // Al cargar, aplica el modo nocturno si está guardado
    if (localStorage.getItem('darkmode') === 'on') {
        document.body.classList.add('darkmode');
        if (toggle) toggle.checked = true;
        if (label) label.textContent = 'Activado';
    }

    // Cambia el modo nocturno al usar el switch
    if (toggle) {
        toggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('darkmode');
                if (label) label.textContent = 'Activado';
                localStorage.setItem('darkmode', 'on');
            } else {
                document.body.classList.remove('darkmode');
                if (label) label.textContent = 'Desactivado';
                localStorage.setItem('darkmode', 'off');
            }
        });
    }
});