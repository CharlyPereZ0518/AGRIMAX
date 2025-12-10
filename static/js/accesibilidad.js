document.addEventListener('DOMContentLoaded', function () {
  inicializarSistemaContraste();
  aplicarPreferenciasVisuales();
  configurarGuardadoAutomatico();
  cargarValoresFormulario();
});

/** CONTRASTE — Sistema original */
function inicializarSistemaContraste() {
  const contrasteGuardado = obtenerContrasteGuardado();
  if (contrasteGuardado && contrasteGuardado !== 'normal') {
    aplicarContraste(contrasteGuardado);
  }

  const selectorContraste = document.getElementById('nivel-contraste');
  if (selectorContraste) {
    selectorContraste.addEventListener('change', function () {
      const nivel = this.value;
      aplicarContraste(nivel);
      anunciarCambioContraste(nivel);
    });
  }
}

function aplicarContraste(nivel) {
  const body = document.body;
  body.classList.remove('contraste-alto', 'contraste-muy-alto');
  
  if (nivel !== 'normal') {
    switch (nivel) {
      case 'alto':
        body.classList.add('contraste-alto');
        break;
      case 'muy-alto':
        body.classList.add('contraste-muy-alto');
        break;
    }
  }
  
  body.setAttribute('data-contraste', nivel);
}

function obtenerContrasteGuardado() {
  const body = document.body;
  return body.getAttribute('data-contraste') || 'normal';
}

function anunciarCambioContraste(nivel) {
  const mensajes = {
    'normal': 'Contraste normal activado',
    'alto': 'Contraste alto activado',
    'muy-alto': 'Contraste muy alto activado'
  };

  let anuncio = document.getElementById('aria-live-contraste');
  if (!anuncio) {
    anuncio = document.createElement('div');
    anuncio.id = 'aria-live-contraste';
    anuncio.setAttribute('role', 'status');
    anuncio.setAttribute('aria-live', 'polite');
    anuncio.setAttribute('aria-atomic', 'true');
    anuncio.style.position = 'absolute';
    anuncio.style.left = '-10000px';
    document.body.appendChild(anuncio);
  }

  anuncio.textContent = mensajes[nivel] || 'Contraste actualizado';
  setTimeout(() => { anuncio.textContent = ''; }, 3000);
}

/** SISTEMA DE TEXTO A VOZ */
class LectorPantallaAuto {
    constructor() {
        this.estaLeyendo = false;
        this.utterance = null;
    }
    
    iniciarLecturaAutomatica() {
        if (!('speechSynthesis' in window)) {
            console.log('Navegador no soporta texto a voz');
            return;
        }
        
        this.detenerLectura();
        
        const texto = this.obtenerTextoParaLeer();
        if (!texto) return;
        
        this.utterance = new SpeechSynthesisUtterance(texto);
        this.utterance.lang = 'es-ES';
        this.utterance.rate = 0.9;
        this.utterance.pitch = 1;
        this.utterance.volume = 1;
        
        this.utterance.onstart = () => {
            this.estaLeyendo = true;
            console.log('Lectura automática iniciada');
        };
        
        this.utterance.onend = () => {
            this.estaLeyendo = false;
            console.log('Lectura automática finalizada');
        };
        
        this.utterance.onerror = () => {
            this.estaLeyendo = false;
        };
        
        setTimeout(() => {
            speechSynthesis.speak(this.utterance);
        }, 500);
    }
    
    detenerLectura() {
        if (speechSynthesis.speaking) {
            speechSynthesis.cancel();
        }
        this.estaLeyendo = false;
    }
    
    obtenerTextoParaLeer() {
        const seccionActiva = document.querySelector('.config-section.active');
        if (seccionActiva) {
            const titulo = seccionActiva.querySelector('.section-title')?.textContent || '';
            const subtitulo = seccionActiva.querySelector('.card-title')?.textContent || '';
            
            let texto = `Sección de ${titulo}. ${subtitulo}. `;
            texto = texto.replace(/\s+/g, ' ').trim();
            
            return texto;
        }
        
        return "Configuración de accesibilidad.";
    }
}

const lectorAuto = new LectorPantallaAuto();

/** Cargar valores en el formulario desde localStorage */
function cargarValoresFormulario() {
  // Cursor
  const cursor = localStorage.getItem('cursor_size') || 'default';
  const cursorSelect = document.getElementById('cursor-size');
  if (cursorSelect) cursorSelect.value = cursor;

  // Modo lector
  const lector = localStorage.getItem('modo_lector') || 'off';
  const lectorSelect = document.getElementById('modo-lector');
  if (lectorSelect) lectorSelect.value = lector;

  // Tipo de letra
  const fontFamily = localStorage.getItem('font_family') || 'Arial, sans-serif';
  const fontSelect = document.getElementById('font-select');
  if (fontSelect) {
    for (let i = 0; i < fontSelect.options.length; i++) {
      if (fontSelect.options[i].value === fontFamily) {
        fontSelect.selectedIndex = i;
        break;
      }
    }
  }

  // Tamaño de letra
  const fontSize = localStorage.getItem('font_size') || 'normal';
  const fontSizeSelect = document.getElementById('font-size');
  if (fontSizeSelect) fontSizeSelect.value = fontSize;

  // Modo oscuro
  const modoOscuro = localStorage.getItem('modoOscuro') || 'off';
  const modoOscuroSelect = document.getElementById('modo-nocturno');
  if (modoOscuroSelect) modoOscuroSelect.value = modoOscuro;

  // Modo grises
  const modoGrises = localStorage.getItem('modoGrises') || 'false';
  const modoGrisesSelect = document.getElementById('modo-grises');
  if (modoGrisesSelect) modoGrisesSelect.value = modoGrises === 'true' ? 'on' : 'off';
}

/** VISUAL — Aplica el resto de preferencias */
function aplicarPreferenciasVisuales() {
  const body = document.body;

  // Limpiar todas las clases visuales
  body.classList.remove(
    'cursor-large',
    'modo-lector',
    'modo-grises',
    'font-large',
    'font-x-large',
    'modo-nocturno',
    'cielo-nocturno'
  );

  // Cursor
  const cursor = localStorage.getItem('cursor_size');
  if (cursor === 'large') {
    body.classList.add('cursor-large');
  }

  // Tamaño de letra
  const fontSize = localStorage.getItem('font_size') || 'normal';
  if (fontSize === 'large') {
    body.classList.add('font-large');
  } else if (fontSize === 'x-large') {
    body.classList.add('font-x-large');
  }

  // Tipo de letra
  const fontFamily = localStorage.getItem('font_family');
  if (fontFamily) {
    body.style.fontFamily = fontFamily;
  }

  // Modo lector - CON LECTURA AUTOMÁTICA
  const lector = localStorage.getItem('modo_lector');
  if (lector === 'on') {
    body.classList.add('modo-lector');
    // ACTIVAR LECTURA AUTOMÁTICA
    lectorAuto.iniciarLecturaAutomatica();
  } else {
    body.classList.remove('modo-lector');
    // DETENER LECTURA SI SE DESACTIVA
    lectorAuto.detenerLectura();
  }

  // Modo oscuro
  const modoOscuro = localStorage.getItem('modoOscuro') || 'off';
  if (modoOscuro === 'on') {
    body.classList.add('modo-nocturno');
  } else if (modoOscuro === 'cielo-nocturno') {
    body.classList.add('cielo-nocturno');
  }

  // Modo grises
  const modoGrises = localStorage.getItem('modoGrises');
  if (modoGrises === 'true') {
    body.classList.add('modo-grises');
  }
}

/** Configurar guardado automático */
function configurarGuardadoAutomatico() {
  const form = document.querySelector('#accesibilidad form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    // Obtener valores del formulario
    const contraste = document.getElementById('nivel-contraste')?.value;
    const cursor = document.getElementById('cursor-size')?.value;
    const lector = document.getElementById('modo-lector')?.value;
    const tipografia = document.getElementById('font-select')?.value;
    const tamanoLetra = document.getElementById('font-size')?.value;
    const modoOscuro = document.getElementById('modo-nocturno')?.value;
    const modoGrises = document.getElementById('modo-grises')?.value;

    // Guardar en localStorage
    if (cursor) localStorage.setItem('cursor_size', cursor);
    if (lector) localStorage.setItem('modo_lector', lector);
    if (tipografia) localStorage.setItem('font_family', tipografia);
    if (tamanoLetra) localStorage.setItem('font_size', tamanoLetra);
    if (modoOscuro) localStorage.setItem('modoOscuro', modoOscuro);
    if (modoGrises) localStorage.setItem('modoGrises', modoGrises === 'on' ? 'true' : 'false');

    // Aplicar inmediatamente
    aplicarContraste(contraste || 'normal');
    aplicarPreferenciasVisuales();
    
    // Recargar valores en el formulario
    setTimeout(cargarValoresFormulario, 100);
  });
}

// Detener lectura al cambiar de página
window.addEventListener('beforeunload', function() {
  lectorAuto.detenerLectura();
}); 