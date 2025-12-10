// Funciones para el modal de productos
function openModal(product) {
    document.getElementById(product + '-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
    if (event.target.classList.contains('product-modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Funciones para el menú hamburguesa
document.addEventListener('DOMContentLoaded', function() {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const overlay = document.getElementById('overlay');
    
    // Abrir/cerrar menú
    hamburgerBtn.addEventListener('click', function() {
        dropdownMenu.classList.toggle('show');
        overlay.classList.toggle('active');
    });

    // Cerrar menú al hacer clic en el overlay
    overlay.addEventListener('click', function() {
        dropdownMenu.classList.remove('show');
        overlay.classList.remove('active');
    });

    // Cerrar menú al hacer clic en un enlace
    document.querySelectorAll('.dropdown-menu a').forEach(link => {
        link.addEventListener('click', function() {
            dropdownMenu.classList.remove('show');
            overlay.classList.remove('active');
        });
    });
});

// Modificar `addToCart` para enviar al servidor
function addToCart(productId, productName, productPrice, productImage) {
    // Crear formulario para enviar datos
    const formData = new FormData();
    formData.append('producto_id', productId);
    formData.append('cantidad', 1);

    // Enviar petición al servidor
    fetch('/agregar_al_carrito', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showNotification(`${productName} agregado al carrito ✅`);
        } else {
            showNotification(`Error al agregar ${productName} ❌`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al agregar al carrito ❌');
    });
}


// Función para mostrar una notificación
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerText = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 2000);
}

// Estilos de la notificación
const style = document.createElement('style');
style.innerHTML = `
    .notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        opacity: 1;
        transition: opacity 0.5s ease-in-out;
    }
`;
document.head.appendChild(style);
