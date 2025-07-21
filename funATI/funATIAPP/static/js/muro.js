const PLACEHOLDER = '¿A quién quieres Funar?';
var contentSpan = document.getElementById('funar-content');
// Inicializar el placeholder si está vacío
if (!contentSpan.innerText.trim()) {
    contentSpan.innerText = PLACEHOLDER;
    contentSpan.classList.add('placeholder');
}
// Al hacer foco, borrar el placeholder
contentSpan.addEventListener('focus', function() {
    if (contentSpan.innerText.trim() === PLACEHOLDER) {
        contentSpan.innerText = '';
        contentSpan.classList.remove('placeholder');
    }
});
// Al perder foco, restaurar el placeholder si está vacío
contentSpan.addEventListener('blur', function() {
    if (!contentSpan.innerText.trim()) {
        contentSpan.innerText = PLACEHOLDER;
        contentSpan.classList.add('placeholder');
    }
});
// Copiar el contenido editable al campo oculto antes de enviar el formulario
var funarForm = document.getElementById('funar-form');
if (funarForm) {
    funarForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var content = contentSpan.innerText.trim();
        if (content === PLACEHOLDER) content = '';
        document.getElementById('hidden-content').value = content;
        var formData = new FormData(this);
        fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                // Recargar solo el contenedor de publicaciones
                loadHTML('#publicaciones', funarForm.getAttribute('data-container-url'));
                // Restaurar el placeholder
                contentSpan.innerText = PLACEHOLDER;
                contentSpan.classList.add('placeholder');
                document.getElementById('hidden-content').value = '';
                document.getElementById('media-input').value = '';
                document.getElementById('funar-btn').disabled = true;
            } else {
                alert('Error al publicar.');
            }
        })
        .catch(() => alert('Error al publicar.'));
    });
}
// Desactivar el botón si no hay texto
function checkFunarContent() {
    var content = contentSpan.innerText.trim();
    document.getElementById('funar-btn').disabled = (!content || content === PLACEHOLDER);
}
contentSpan.addEventListener('input', checkFunarContent);
document.addEventListener('DOMContentLoaded', checkFunarContent);
// Función para cargar un archivo HTML en un elemento
function loadHTML(selector, filePath) {
    fetch(filePath)
        .then(response => response.text())
        .then(html => {
            document.querySelector(selector).innerHTML = html;
        })
        .catch(error => console.error('Error al cargar el archivo:', error));
}
document.addEventListener('DOMContentLoaded', () => {
    if (funarForm) {
        loadHTML('#publicaciones', funarForm.getAttribute('data-container-url'));
    }
});
