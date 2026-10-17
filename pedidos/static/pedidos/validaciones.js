(() => {
    const form = document.querySelector('#pedido-form');
    if (!form) return;

    const fields = {
        numero_pedido: {
            element: form.querySelector('#id_numero_pedido'),
            validate: (value) => value.trim() ? '' : 'Escribe el número del pedido.',
        },
        cliente: {
            element: form.querySelector('#id_cliente'),
            validate: (value) => value.trim().length >= 3
                ? ''
                : 'Escribe el nombre del cliente (mínimo 3 caracteres).',
        },
        descripcion: {
            element: form.querySelector('#id_descripcion'),
            validate: (value) => value.trim() ? '' : 'Escribe la descripción del pedido.',
        },
        valor_total: {
            element: form.querySelector('#id_valor_total'),
            validate: (value) => Number.isFinite(Number(value)) && Number(value) > 0
                ? ''
                : 'El valor total debe ser un número mayor que cero.',
        },
        estado: {
            element: form.querySelector('#id_estado'),
            validate: (value) => ['pendiente', 'confirmado', 'cancelado'].includes(value)
                ? ''
                : 'Selecciona un estado permitido.',
        },
    };

    const formError = document.querySelector('#errores-formulario');

    function validateField(field) {
        if (!field.element) return true;
        const message = field.validate(field.element.value);
        const feedback = form.querySelector(`[data-error-for="${field.element.id}"]`);
        field.element.classList.toggle('is-invalid', Boolean(message));
        field.element.setAttribute('aria-invalid', message ? 'true' : 'false');
        if (feedback) feedback.textContent = message;
        return !message;
    }

    Object.values(fields).forEach((field) => {
        if (!field.element) return;
        field.element.addEventListener('input', () => validateField(field));
        field.element.addEventListener('change', () => validateField(field));
        field.element.addEventListener('blur', () => validateField(field));
    });

    form.addEventListener('submit', (event) => {
        const valid = Object.values(fields).map(validateField).every(Boolean);
        if (!valid) {
            event.preventDefault();
            formError.textContent = 'Revisa los campos marcados antes de guardar el pedido.';
            formError.classList.remove('d-none');
            form.querySelector('.is-invalid')?.focus();
            return;
        }
        formError.classList.add('d-none');
        formError.textContent = '';
    });
})();