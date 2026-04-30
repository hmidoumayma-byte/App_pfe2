// GestiAbsence — Global JS utilities

// Auto-dismiss alerts after 5s
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.alert.fade.show').forEach(function (el) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert.close();
        });
    }, 5000);

    // Activate tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // Highlight active sidebar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link-sidebar').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// CSRF helper for fetch
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
}

// Ajax POST helper
async function ajaxPost(url, data) {
    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    const res = await fetch(url, { method: 'POST', body: formData });
    return res.json();
}

// Toast notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || (() => {
        const el = document.createElement('div');
        el.id = 'toast-container';
        el.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;';
        document.body.appendChild(el);
        return el;
    })();

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} shadow-sm`;
    toast.style.cssText = 'min-width:260px;border-radius:10px;animation:fadeInUp .3s ease;';
    toast.innerHTML = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}
