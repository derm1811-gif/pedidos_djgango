(() => {
    const form = document.querySelector('#producto-form');
    if (!form) return;

    const fields = {
        nombre: {
            element: form.querySelector('#nombre'),
            validate: (value) => value.trim().length >= 3
                ? ''
                : 'Escribe un nombre de al menos 3 caracteres.',
        },
        descripcion: {
            element: form.querySelector('#descripcion'),
            validate: (value) => {
                if (!value.trim()) return 'La descripción es obligatoria.';
                if (value.length > 1000) return 'La descripción no puede superar 1000 caracteres.';
                return '';
            },
        },
        precio: {
            element: form.querySelector('#precio'),
            validate: (value) => Number.isFinite(Number(value)) && Number(value) > 0
                ? ''
                : 'El precio debe ser un número mayor que cero.',
        },
        cantidad_disponible: {
            element: form.querySelector('#cantidad_disponible'),
            validate: (value) => /^\d+$/.test(value) && Number(value) >= 0
                ? ''
                : 'La cantidad debe ser un número entero igual o superior a cero.',
        },
    };
    const resumen = form.querySelector('#errores-formulario');

    function validarCampo(field) {
        if (!field.element) return true;
        const mensaje = field.validate(field.element.value);
        const ayuda = form.querySelector(`[data-error-for="${field.element.id}"]`);
        field.element.classList.toggle('is-invalid', Boolean(mensaje));
        field.element.setAttribute('aria-invalid', mensaje ? 'true' : 'false');
        if (ayuda) ayuda.textContent = mensaje;
        return !mensaje;
    }

    Object.values(fields).forEach((field) => {
        if (!field.element) return;
        field.element.addEventListener('input', () => validarCampo(field));
        field.element.addEventListener('change', () => validarCampo(field));
        field.element.addEventListener('blur', () => validarCampo(field));
    });

    form.addEventListener('submit', (event) => {
        const valido = Object.values(fields).map(validarCampo).every(Boolean);
        if (!valido) {
            event.preventDefault();
            resumen.textContent = 'Corrige los campos marcados antes de guardar el producto.';
            resumen.classList.remove('d-none');
            form.querySelector('.is-invalid')?.focus();
            return;
        }
        resumen.classList.add('d-none');
        resumen.textContent = '';
    });
})();