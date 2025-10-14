// Espera a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {
    const fontSizeRange = document.getElementById('fontSizeRange');
    const fontSizeValue = document.getElementById('fontSizeValue');

    if (fontSizeRange && fontSizeValue) {
        // Evento para cuando el usuario mueve la barra
        fontSizeRange.addEventListener('input', () => {
            const sizePercent = fontSizeRange.value;
            fontSizeValue.textContent = `${sizePercent}%`;   // Muestra el valor actual
            document.body.style.fontSize = `${sizePercent}%`; // Cambia el tamaño del texto en toda la página
            localStorage.setItem('fontSizePreference', sizePercent); // Guarda la preferencia
        });

        // Al cargar la página, revisa si el usuario ya guardó un tamaño
        const savedSize = localStorage.getItem('fontSizePreference');
        if (savedSize) {
            fontSizeRange.value = savedSize;
            fontSizeValue.textContent = `${savedSize}%`;
            document.body.style.fontSize = `${savedSize}%`;
        }
    }
});
