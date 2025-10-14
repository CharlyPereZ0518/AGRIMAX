// contraste.js - Sistema de contraste para accesibilidad

document.addEventListener('DOMContentLoaded', function() {
    inicializarSistemaContraste();
});

/**
 * Inicializa el sistema de contraste
 */
function inicializarSistemaContraste() {
    // Cargar y aplicar contraste guardado al cargar la página
    const contrasteGuardado = obtenerContrasteGuardado();
    if (contrasteGuardado && contrasteGuardado !== 'normal') {
        aplicarContraste(contrasteGuardado);
    }

    // Listener para el selector de contraste
    const selectorContraste = document.getElementById('nivel-contraste');
    if (selectorContraste) {
        // Aplicar el contraste inmediatamente al cambiar (sin necesidad de guardar)
        selectorContraste.addEventListener('change', function() {
            const nivel = this.value;
            aplicarContraste(nivel);
            anunciarCambioContraste(nivel);
        });
    }
}

/**
 * Aplica el nivel de contraste seleccionado
 * @param {string} nivel - normal, alto, muy-alto, oscuro
 */
function aplicarContraste(nivel) {
    const body = document.body;
    
    // Remover todas las clases de contraste
    body.classList.remove('contraste-alto', 'contraste-muy-alto', 'modo-oscuro');
    
    // Aplicar la clase correspondiente SOLO si NO es normal
    if (nivel !== 'normal') {
        switch(nivel) {
            case 'alto':
                body.classList.add('contraste-alto');
                break;
            case 'muy-alto':
                body.classList.add('contraste-muy-alto');
                break;
            case 'oscuro':
                body.classList.add('modo-oscuro');
                break;
        }
    }
    // Si es 'normal', simplemente se eliminaron todas las clases
    
    // Actualizar el atributo data-contraste para persistencia
    body.setAttribute('data-contraste', nivel);
    
    // Actualizar el selector si existe y no es el que disparó el cambio
    const selector = document.getElementById('nivel-contraste');
    if (selector && selector.value !== nivel) {
        selector.value = nivel;
    }
    
    console.log('Contraste aplicado:', nivel);
}

/**
 * Obtiene el contraste guardado del atributo data del body
 * @returns {string} Nivel de contraste guardado o 'normal' por defecto
 */
function obtenerContrasteGuardado() {
    const body = document.body;
    return body.getAttribute('data-contraste') || 'normal';
}

/**
 * Anuncia el cambio de contraste para lectores de pantalla
 * @param {string} nivel - Nivel aplicado
 */
function anunciarCambioContraste(nivel) {
    const mensajes = {
        'normal': 'Contraste normal activado',
        'alto': 'Contraste alto activado. Los colores son más definidos',
        'muy-alto': 'Contraste muy alto activado. Modo blanco y negro',
        'oscuro': 'Modo oscuro activado. Fondo oscuro con texto claro'
    };
    
    // Crear o actualizar elemento para anuncio ARIA
    let anuncio = document.getElementById('aria-live-contraste');
    if (!anuncio) {
        anuncio = document.createElement('div');
        anuncio.id = 'aria-live-contraste';
        anuncio.setAttribute('role', 'status');
        anuncio.setAttribute('aria-live', 'polite');
        anuncio.setAttribute('aria-atomic', 'true');
        anuncio.style.position = 'absolute';
        anuncio.style.left = '-10000px';
        anuncio.style.width = '1px';
        anuncio.style.height = '1px';
        anuncio.style.overflow = 'hidden';
        document.body.appendChild(anuncio);
    }
    
    // Anunciar el cambio
    anuncio.textContent = mensajes[nivel] || 'Contraste actualizado';
    
    // Limpiar el mensaje después de 3 segundos
    setTimeout(() => {
        anuncio.textContent = '';
    }, 3000);
}

/**
 * Función para forzar un contraste específico (útil para testing)
 * @param {string} nivel - Nivel de contraste a aplicar
 */
function forzarContraste(nivel) {
    aplicarContraste(nivel);
    const selector = document.getElementById('nivel-contraste');
    if (selector) {
        selector.value = nivel;
    }
}

/**
 * Obtiene el nivel de contraste actual
 * @returns {string} Nivel de contraste actual
 */
function obtenerContrasteActual() {
    const body = document.body;
    if (body.classList.contains('contraste-alto')) return 'alto';
    if (body.classList.contains('contraste-muy-alto')) return 'muy-alto';
    if (body.classList.contains('modo-oscuro')) return 'oscuro';
    return 'normal';
}

// Exportar funciones para uso global
window.contrasteUtils = {
    aplicar: aplicarContraste,
    obtener: obtenerContrasteActual,
    forzar: forzarContraste,
    anunciar: anunciarCambioContraste
};

console.log('Sistema de contraste inicializado correctamente');