// /static/js/accesibilidad-global.js (para vistas sin configuración)
document.addEventListener('DOMContentLoaded', function () {
  inicializarSistemaContraste();
  aplicarPreferenciasVisuales();
});

function aplicarPreferenciasVisuales() {
  const body = document.body;
  
  // Aplicar clases desde localStorage
  const cursor = localStorage.getItem('cursor_size');
  if (cursor === 'large') body.classList.add('cursor-large');
  
  const fontSize = localStorage.getItem('font_size');
  if (fontSize === 'large') body.classList.add('font-large');
  else if (fontSize === 'x-large') body.classList.add('font-x-large');
  
  const fontFamily = localStorage.getItem('font_family');
  if (fontFamily) body.style.fontFamily = fontFamily;
  
  const modoOscuro = localStorage.getItem('modoOscuro');
  if (modoOscuro === 'on') body.classList.add('modo-nocturno');
  else if (modoOscuro === 'cielo-nocturno') body.classList.add('cielo-nocturno');
  
  const modoGrises = localStorage.getItem('modoGrises');
  if (modoGrises === 'true') body.classList.add('modo-grises');
  
  const lector = localStorage.getItem('modo_lector');
  if (lector === 'on') {
    body.classList.add('modo-lector');
    // Activar lector global si existe
    if (window.lectorGlobal) lectorGlobal.iniciarLecturaAutomatica();
  }
}