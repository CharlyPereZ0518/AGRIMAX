document.addEventListener('DOMContentLoaded', function() {
    // Cambiar entre secciones de configuración
    const menuItems = document.querySelectorAll('.config-menu li');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remover clase active de todos los items
            menuItems.forEach(i => i.classList.remove('active'));
            
            // Agregar clase active al item clickeado
            this.classList.add('active');
            
            // Ocultar todas las secciones
            document.querySelectorAll('.config-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Mostrar la sección correspondiente
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // Manejar el feedback de mensajes flash
    const feedbackElements = document.querySelectorAll('.feedback');
    feedbackElements.forEach(feedback => {
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 500);
        }, 3000);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Cargar preferencias actuales del localStorage
    cargarPreferencias();
    
    // Cambiar entre secciones de configuración
    const menuItems = document.querySelectorAll('.config-menu li');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remover clase active de todos los items
            menuItems.forEach(i => i.classList.remove('active'));
            
            // Agregar clase active al item clickeado
            this.classList.add('active');
            
            // Ocultar todas las secciones
            document.querySelectorAll('.config-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Mostrar la sección correspondiente
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // Guardar preferencias de accesibilidad en localStorage cuando cambien
    document.querySelectorAll('#accesibilidad select').forEach(select => {
        select.addEventListener('change', function() {
            guardarPreferencia(this.name, this.value);
            aplicarPreferencias(); // Aplicar inmediatamente
        });
    });

    // Manejar el feedback de mensajes flash
    const feedbackElements = document.querySelectorAll('.feedback');
    feedbackElements.forEach(feedback => {
        setTimeout(() => {
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 500);
        }, 3000);
    });
});

function cargarPreferencias() {
    // Cargar valores del localStorage y establecerlos en los selects
    const preferencias = {
        'nivel_contraste': localStorage.getItem('nivel_contraste') || 'normal',
        'cursor_size': localStorage.getItem('cursor_size') || 'default',
        'modo_lector': localStorage.getItem('modo_lector') || 'off',
        'font_size': localStorage.getItem('font_size') || 'normal',
        'modo_nocturno': localStorage.getItem('modo_nocturno') || 'off',
        'modo_grises': localStorage.getItem('modo_grises') || 'off'
    };

    // Establecer valores en los selects
    Object.keys(preferencias).forEach(key => {
        const select = document.querySelector(`[name="${key}"]`);
        if (select) {
            select.value = preferencias[key];
        }
    });
}

function guardarPreferencia(nombre, valor) {
    localStorage.setItem(nombre, valor);
    console.log(`Guardado: ${nombre} = ${valor}`);
}

function aplicarPreferencias() {
    const body = document.body;
    
    // Remover todas las clases previas
    body.classList.remove(
        'contraste-alto', 'contraste-muy-alto', 'modo-nocturno', 'modo-grises',
        'cursor-large', 'modo-lector', 'font-large', 'font-x-large'
    );
    
    // Aplicar contraste
    const contraste = localStorage.getItem('nivel_contraste') || 'normal';
    if (contraste !== 'normal') {
        body.classList.add(contraste === 'alto' ? 'contraste-alto' : 'contraste-muy-alto');
    }
    
    // Aplicar modo oscuro
    const modoOscuro = localStorage.getItem('modo_nocturno') || 'off';
    if (modoOscuro === 'on') {
        body.classList.add('modo-nocturno');
    }
    
    // Aplicar escala de grises
    const modoGrises = localStorage.getItem('modo_grises') || 'off';
    if (modoGrises === 'on') {
        body.classList.add('modo-grises');
    }
    
    // Aplicar cursor grande
    const cursorSize = localStorage.getItem('cursor_size') || 'default';
    if (cursorSize === 'large') {
        body.classList.add('cursor-large');
    }
    
    // Aplicar modo lector
    const modoLector = localStorage.getItem('modo_lector') || 'off';
    if (modoLector === 'on') {
        body.classList.add('modo-lector');
    }
    
    // Aplicar tamaño de fuente
    const fontSize = localStorage.getItem('font_size') || 'normal';
    if (fontSize !== 'normal') {
        body.classList.add(fontSize === 'large' ? 'font-large' : 'font-x-large');
    }
    
    // Aplicar familia de fuente
    const fontFamily = localStorage.getItem('font_family') || 'Arial, sans-serif';
    body.style.fontFamily = fontFamily;
}

// También aplica las preferencias al cargar la página
aplicarPreferencias();