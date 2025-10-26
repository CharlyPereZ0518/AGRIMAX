// accesibilidad.js
const fontSizeRange = document.getElementById('fontSizeRange');
const fontSizeValue = document.getElementById('fontSizeValue');

// Cargar el valor guardado al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  const savedFontSize = localStorage.getItem('fontSize');
  if (savedFontSize) {
    document.body.style.fontSize = `${savedFontSize}%`;
    fontSizeRange.value = savedFontSize;
    fontSizeValue.textContent = `${savedFontSize}%`;
  }
});

// Actualizar el tamaño de fuente y guardar
fontSizeRange.addEventListener('input', () => {
  const newSize = fontSizeRange.value;
  document.body.style.fontSize = `${newSize}%`;
  fontSizeValue.textContent = `${newSize}%`;
  localStorage.setItem('fontSize', newSize);
});