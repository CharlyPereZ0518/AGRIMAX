// Configuración de preferencias de accesibilidad
let preferencias = {
    contraste: 'normal',
    cursor: 'normal',
    lectorPantalla: false,
    tipoLetra: 'Arial',
    tamañoLetra: 'normal',
    modoOscuro: false,
    escalaGrises: false
};

// Variables para el lector de pantalla
let speechSynthesis = window.speechSynthesis;
let speechUtterance = null;
let isReaderModeActive = false;

// Inicializar accesibilidad en todas las páginas
document.addEventListener('DOMContentLoaded', function() {
    cargarPreferencias();
    aplicarPreferencias();
    
    // ✅ INICIALIZAR LECTOR EN TODAS LAS VISTAS SI ESTÁ ACTIVADO EN PREFERENCIAS
    if (preferencias.lectorPantalla) {
        isReaderModeActive = true;
        setTimeout(() => {
            enableScreenReader();
            
            // Leer información de la página actual
            const pageTitle = document.title || 'Página sin título';
            const mainHeading = document.querySelector('h1')?.textContent || '';
            let welcomeText = `Página cargada: ${pageTitle}`;
            if (mainHeading) {
                welcomeText += `. ${mainHeading}`;
            }
            speakText(welcomeText);
        }, 800);
    }
    
    // Si estamos en la página de configuración, configurar los event listeners
    if (window.location.pathname.includes('/admin/accesibilidad')) {
        configurarEventListenersConfiguracion();
    }
});

// Configurar event listeners solo para la página de configuración
function configurarEventListenersConfiguracion() {
    // Contraste
    document.querySelectorAll('input[name="contraste"]').forEach(radio => {
        radio.addEventListener('change', function() {
            preferencias.contraste = this.value;
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Contraste actualizado');
            if (isReaderModeActive) speakText('Contraste actualizado a ' + this.value);
        });
    });

    // Cursor
    document.querySelectorAll('input[name="cursor"]').forEach(radio => {
        radio.addEventListener('change', function() {
            preferencias.cursor = this.value;
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Tamaño de cursor actualizado');
            if (isReaderModeActive) speakText('Cursor ' + this.value);
        });
    });

    // Lector pantalla - SOLO PARA CONFIGURACIÓN
    const lectorPantallaToggle = document.getElementById('lectorPantalla');
    if (lectorPantallaToggle) {
        lectorPantallaToggle.addEventListener('change', function() {
            const wasActive = isReaderModeActive;
            preferencias.lectorPantalla = this.checked;
            actualizarTextoSwitch('lectorPantalla', this.checked);
            
            if (this.checked && !wasActive) {
                isReaderModeActive = true;
                enableScreenReader();
                speakText('Modo lector activado. Página de configuración de accesibilidad');
            } else if (!this.checked && wasActive) {
                isReaderModeActive = false;
                disableScreenReader();
                speechSynthesis.cancel();
            }
            
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Modo lector ' + (this.checked ? 'activado' : 'desactivado'));
        });
    }

    // Tipo letra
    const tipoLetraSelect = document.getElementById('tipoLetra');
    if (tipoLetraSelect) {
        tipoLetraSelect.addEventListener('change', function() {
            preferencias.tipoLetra = this.value;
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Tipo de letra cambiado a ' + this.value);
            if (isReaderModeActive) speakText('Fuente cambiada a ' + this.value);
        });
    }

    // Tamaño letra
    document.querySelectorAll('input[name="tamañoLetra"]').forEach(radio => {
        radio.addEventListener('change', function() {
            preferencias.tamañoLetra = this.value;
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Tamaño de letra actualizado');
            if (isReaderModeActive) speakText('Tamaño de texto ' + this.value);
        });
    });

    // Modo oscuro
    const modoOscuroToggle = document.getElementById('modoOscuro');
    if (modoOscuroToggle) {
        modoOscuroToggle.addEventListener('change', function() {
            preferencias.modoOscuro = this.checked;
            actualizarTextoSwitch('modoOscuro', this.checked);
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Modo oscuro ' + (this.checked ? 'activado' : 'desactivado'));
            if (isReaderModeActive) speakText('Modo oscuro ' + (this.checked ? 'activado' : 'desactivado'));
        });
    }

    // Escala grises
    const escalaGrisesToggle = document.getElementById('escalaGrises');
    if (escalaGrisesToggle) {
        escalaGrisesToggle.addEventListener('change', function() {
            preferencias.escalaGrises = this.checked;
            actualizarTextoSwitch('escalaGrises', this.checked);
            aplicarPreferencias();
            guardarPreferencias();
            mostrarFlash('Escala de grises ' + (this.checked ? 'activada' : 'desactivada'));
            if (isReaderModeActive) speakText('Escala de grises ' + (this.checked ? 'activada' : 'desactivada'));
        });
    }
}

// Cargar preferencias guardadas del localStorage
function cargarPreferencias() {
    const guardadas = localStorage.getItem('adminPreferenciasAccesibilidad');
    if (guardadas) {
        preferencias = JSON.parse(guardadas);
        
        // Si estamos en la página de configuración, actualizar el formulario
        if (window.location.pathname.includes('/admin/accesibilidad')) {
            actualizarFormulario();
        }
    }
}

// Actualizar formulario con valores guardados (solo en página de configuración)
function actualizarFormulario() {
    // Contraste
    const contrasteRadio = document.querySelector(`input[name="contraste"][value="${preferencias.contraste}"]`);
    if (contrasteRadio) contrasteRadio.checked = true;
    
    // Cursor
    const cursorRadio = document.querySelector(`input[name="cursor"][value="${preferencias.cursor}"]`);
    if (cursorRadio) cursorRadio.checked = true;
    
    // Lector de pantalla
    const lectorPantalla = document.getElementById('lectorPantalla');
    if (lectorPantalla) {
        lectorPantalla.checked = preferencias.lectorPantalla;
        actualizarTextoSwitch('lectorPantalla', preferencias.lectorPantalla);
    }
    
    // Tipo de letra
    const tipoLetra = document.getElementById('tipoLetra');
    if (tipoLetra) tipoLetra.value = preferencias.tipoLetra;
    
    // Tamaño de letra
    const tamañoLetraRadio = document.querySelector(`input[name="tamañoLetra"][value="${preferencias.tamañoLetra}"]`);
    if (tamañoLetraRadio) tamañoLetraRadio.checked = true;
    
    // Modo oscuro
    const modoOscuro = document.getElementById('modoOscuro');
    if (modoOscuro) {
        modoOscuro.checked = preferencias.modoOscuro;
        actualizarTextoSwitch('modoOscuro', preferencias.modoOscuro);
    }
    
    // Escala de grises
    const escalaGrises = document.getElementById('escalaGrises');
    if (escalaGrises) {
        escalaGrises.checked = preferencias.escalaGrises;
        actualizarTextoSwitch('escalaGrises', preferencias.escalaGrises);
    }
}

// Actualizar texto de los switches (solo en página de configuración)
function actualizarTextoSwitch(id, activado) {
    const label = document.querySelector(`label[for="${id}"]`);
    if (label) {
        label.textContent = activado ? 'Activado' : 'Desactivado';
    }
}

// Aplicar preferencias a todas las páginas
function aplicarPreferencias() {
    console.log('Aplicando preferencias de accesibilidad:', preferencias);
    
    // Aplicar filtros acumulativos
    let filtros = [];
    
    // Contraste
    if (preferencias.contraste === 'alto') {
        filtros.push('contrast(1.8)');
    } else if (preferencias.contraste === 'maximo') {
        filtros.push('contrast(2.5)');
    }
    
    // Escala de grises
    if (preferencias.escalaGrises) {
        filtros.push('grayscale(1)');
    }
    
    // Aplicar todos los filtros
    if (filtros.length > 0) {
        document.body.style.filter = filtros.join(' ');
    } else {
        document.body.style.filter = 'none';
    }

    // Cursor
    document.body.classList.remove('cursor-grande', 'cursor-extra-grande');
    
    if (preferencias.cursor === 'grande') {
        document.body.classList.add('cursor-grande');
    } else if (preferencias.cursor === 'extra-grande') {
        document.body.classList.add('cursor-extra-grande');
    }

    // Tipo de letra
    const elementosTexto = document.querySelectorAll('body, .card, .container, p, span, div, h1, h2, h3, h4, h5, h6');
    elementosTexto.forEach(el => {
        el.style.fontFamily = preferencias.tipoLetra + ', Arial, sans-serif';
    });

    // Tamaño de letra
    document.body.classList.remove('texto-pequeno', 'texto-grande', 'texto-muy-grande');
    
    if (preferencias.tamañoLetra === 'pequeno') {
        document.body.classList.add('texto-pequeno');
    } else if (preferencias.tamañoLetra === 'grande') {
        document.body.classList.add('texto-grande');
    } else if (preferencias.tamañoLetra === 'muy-grande') {
        document.body.classList.add('texto-muy-grande');
    }

    // Modo oscuro
    if (preferencias.modoOscuro) {
        document.body.classList.add('modo-nocturno');
    } else {
        document.body.classList.remove('modo-nocturno');
    }
}

// Guardar preferencias en localStorage
function guardarPreferencias() {
    localStorage.setItem('adminPreferenciasAccesibilidad', JSON.stringify(preferencias));
    console.log('Preferencias guardadas en localStorage:', preferencias);
}

// FUNCIONES DEL LECTOR DE PANTALLA - ACTIVAS EN TODAS LAS VISTAS

// Función para habilitar el lector
function enableScreenReader() {
    console.log('🔄 Activando lector de pantalla en:', window.location.href);
    
    // Agregar eventos para leer elementos al interactuar
    document.addEventListener('focus', handleElementFocus, true);
    document.addEventListener('mouseover', handleElementHover, true);
    document.addEventListener('click', handleElementClick, true);
    document.addEventListener('input', handleElementInput, true);
    
    // Agregar atributos ARIA mejorados a todos los elementos interactivos
    mejorarAccesibilidadElementos();
    
    console.log('✅ Lector de pantalla ACTIVO en todas las vistas');
}

// Función para deshabilitar el lector
function disableScreenReader() {
    console.log('🔄 Desactivando lector de pantalla');
    
    document.removeEventListener('focus', handleElementFocus, true);
    document.removeEventListener('mouseover', handleElementHover, true);
    document.removeEventListener('click', handleElementClick, true);
    document.removeEventListener('input', handleElementInput, true);
    
    console.log('✅ Lector de pantalla DESACTIVADO');
}

// Mejorar accesibilidad de todos los elementos
function mejorarAccesibilidadElementos() {
    // Botones
    document.querySelectorAll('button, [role="button"]').forEach(el => {
        if (!el.hasAttribute('aria-label')) {
            const label = el.textContent?.trim() || el.title || 'botón';
            el.setAttribute('aria-label', label);
        }
    });
    
    // Enlaces
    document.querySelectorAll('a').forEach(el => {
        if (!el.hasAttribute('aria-label') && el.textContent?.trim()) {
            el.setAttribute('aria-label', `Enlace: ${el.textContent.trim()}`);
        }
    });
    
    // Inputs
    document.querySelectorAll('input, select, textarea').forEach(el => {
        if (!el.hasAttribute('aria-label')) {
            const label = el.placeholder || el.title || el.getAttribute('data-label') || 'campo de entrada';
            el.setAttribute('aria-label', label);
        }
    });
    
    // Imágenes
    document.querySelectorAll('img').forEach(el => {
        if (!el.hasAttribute('alt') && !el.hasAttribute('aria-label')) {
            el.setAttribute('aria-label', 'imagen');
        }
    });
    
    // Tarjetas
    document.querySelectorAll('.card, .tarjeta, [class*="card"]').forEach(el => {
        if (!el.hasAttribute('aria-label')) {
            const title = el.querySelector('.card-title, .titulo, h1, h2, h3, h4, h5, h6')?.textContent?.trim();
            el.setAttribute('aria-label', title ? `Tarjeta: ${title}` : 'tarjeta');
        }
    });
    
    // Navegación
    document.querySelectorAll('.nav-link, [class*="nav"], .menu-item').forEach(el => {
        if (!el.hasAttribute('aria-label') && el.textContent?.trim()) {
            el.setAttribute('aria-label', `Navegación: ${el.textContent.trim()}`);
        }
    });
}

// Función para leer texto
function speakText(text, interrupt = true) {
    if (!isReaderModeActive || !speechSynthesis) {
        console.log('🔇 Lector no activo o no soportado');
        return;
    }
    
    if (interrupt) {
        speechSynthesis.cancel();
    }
    
    try {
        speechUtterance = new SpeechSynthesisUtterance(text);
        speechUtterance.lang = 'es-ES';
        speechUtterance.rate = 0.9;
        speechUtterance.pitch = 1.0;
        speechUtterance.volume = 1.0;
        
        speechUtterance.onstart = () => console.log('🔊 Hablando:', text);
        speechUtterance.onerror = (e) => console.error('❌ Error síntesis de voz:', e);
        
        speechSynthesis.speak(speechUtterance);
    } catch (error) {
        console.warn('⚠️ Error al usar síntesis de voz:', error);
    }
}

// Manejar foco en elementos
function handleElementFocus(event) {
    if (!isReaderModeActive) return;
    
    const element = event.target;
    let text = '';
    
    if (element.tagName === 'BUTTON' || element.getAttribute('role') === 'button') {
        text = element.textContent?.trim() || element.getAttribute('aria-label') || 'botón';
    } else if (element.tagName === 'INPUT') {
        const type = element.getAttribute('type');
        const placeholder = element.getAttribute('placeholder');
        const label = element.getAttribute('aria-label');
        text = label || placeholder || `${type || 'campo'} de entrada`;
    } else if (element.tagName === 'SELECT') {
        text = 'lista desplegable';
    } else if (element.tagName === 'A') {
        text = `Enlace: ${element.textContent?.trim() || element.getAttribute('aria-label') || 'enlace'}`;
    } else if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(element.tagName.toLowerCase())) {
        text = `Título: ${element.textContent}`;
    } else if (element.classList.contains('card') || element.getAttribute('aria-label')?.includes('tarjeta')) {
        text = element.getAttribute('aria-label') || 'tarjeta';
    } else if (element.classList.contains('nav-link') || element.getAttribute('aria-label')?.includes('Navegación')) {
        text = element.getAttribute('aria-label') || 'elemento de navegación';
    }
    
    if (text) {
        speakText(text);
    }
}

// Manejar hover en elementos
function handleElementHover(event) {
    if (!isReaderModeActive) return;
    
    const element = event.target;
    let shouldSpeak = false;
    let text = '';
    
    // Solo leer elementos interactivos o importantes
    if (element.tagName === 'BUTTON' || 
        element.tagName === 'A' ||
        element.getAttribute('role') === 'button' ||
        element.classList.contains('btn') ||
        element.classList.contains('nav-link') ||
        element.classList.contains('card') ||
        element.classList.contains('option-btn')) {
        
        text = element.getAttribute('aria-label') || 
               element.textContent?.trim() || 
               element.title || 
               'elemento';
        shouldSpeak = true;
    }
    
    if (shouldSpeak && text) {
        speakText(text, false);
    }
}

// Manejar clic en elementos
function handleElementClick(event) {
    if (!isReaderModeActive) return;
    
    const element = event.target;
    let text = '';
    
    if (element.tagName === 'BUTTON' || element.getAttribute('role') === 'button') {
        text = `Clic en: ${element.textContent?.trim() || element.getAttribute('aria-label') || 'botón'}`;
    } else if (element.tagName === 'A') {
        text = `Navegando a: ${element.textContent?.trim() || element.getAttribute('aria-label') || 'enlace'}`;
    } else if (element.tagName === 'INPUT' && element.type === 'radio') {
        text = `Seleccionado: ${element.value}`;
    } else if (element.tagName === 'INPUT' && element.type === 'checkbox') {
        text = element.checked ? 'Casilla activada' : 'Casilla desactivada';
    } else if (element.classList.contains('card')) {
        text = `Tarjeta seleccionada: ${element.getAttribute('aria-label') || 'tarjeta'}`;
    }
    
    if (text) {
        speakText(text);
    }
}

// Manejar input en campos de texto
function handleElementInput(event) {
    if (!isReaderModeActive) return;
    
    const element = event.target;
    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
        if (element.type === 'text' || element.type === 'email' || element.type === 'password') {
            const value = element.value;
            if (value.length > 0) {
                // Leer el último carácter escrito (opcional)
                // speakText(value.slice(-1), false);
            }
        }
    }
}

// Mostrar flash message personalizado
function mostrarFlash(mensaje) {
    // Eliminar flash anterior si existe
    const flashAnterior = document.querySelector('.custom-flash');
    if (flashAnterior) {
        flashAnterior.remove();
    }

    // Crear nuevo flash
    const flash = document.createElement('div');
    flash.className = 'custom-flash';
    flash.innerHTML = `
        <strong>✓</strong> ${mensaje}
    `;

    // Agregar al body
    document.body.appendChild(flash);

    // Auto-eliminar después de 3 segundos
    setTimeout(() => {
        if (flash.parentNode) {
            flash.remove();
        }
    }, 3000);
}

// Función para restablecer todas las preferencias
function resetearAccesibilidad() {
    preferencias = {
        contraste: 'normal',
        cursor: 'normal',
        lectorPantalla: false,
        tipoLetra: 'Arial',
        tamañoLetra: 'normal',
        modoOscuro: false,
        escalaGrises: false
    };
    
    // Desactivar lector si estaba activo
    if (isReaderModeActive) {
        isReaderModeActive = false;
        disableScreenReader();
        speechSynthesis.cancel();
    }
    
    localStorage.removeItem('preferenciasAccesibilidad');
    aplicarPreferencias();
    mostrarFlash('Accesibilidad restablecida');
    
    // Si estamos en la página de configuración, actualizar el formulario
    if (window.location.pathname.includes('/admin/accesibilidad')) {
        actualizarFormulario();
    }
}

// Asegurar que el lector se desactive al salir de la página
window.addEventListener('beforeunload', function() {
    if (isReaderModeActive) {
        speechSynthesis.cancel();
    }
});

// Manejar cambios de visibilidad de página
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isReaderModeActive) {
        speechSynthesis.pause();
    } else if (!document.hidden && isReaderModeActive && speechSynthesis.paused) {
        speechSynthesis.resume();
    }
});

// Debug: Verificar estado del lector
console.log('🎯 Módulo de accesibilidad cargado');
console.log('📍 Página actual:', window.location.href);
console.log('🔊 Estado lector:', isReaderModeActive ? 'ACTIVO' : 'INACTIVO');