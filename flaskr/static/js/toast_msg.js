
function showToast(message, category) {
    const categoryMap = {
        'error': 'danger',
        'danger': 'danger',
        'warning': 'warning',
        'success': 'success',
        'info': 'info',
        'primary': 'primary',
        'secondary': 'secondary'
    };

    const bootstrapCategory = categoryMap[category] || 'info';
    const container = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();

    const toastEl = document.createElement('div');
    toastEl.className = `toast text-white bg-${bootstrapCategory} border-0`;
    toastEl.setAttribute('id', toastId);
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);

    const toast = new bootstrap.Toast(toastEl, {
        delay: 4000,
        autohide: true
    });

    toast.show();

    toastEl.addEventListener('hidden.bs.toast', function () {
        toastEl.remove();
    });
}
document.addEventListener('DOMContentLoaded', function () {
    const messagesElement = document.getElementById('flash-messages');
    if (messagesElement) {
        const messages = JSON.parse(messagesElement.textContent);
        for (const [category, message] of messages) {
            showToast(message, category);
        }
    }
});