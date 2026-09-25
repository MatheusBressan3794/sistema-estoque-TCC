document.addEventListener('DOMContentLoaded', function () {
    // 1. Lógica da Sidebar
    const sidebar = document.querySelector('#app-sidebar');
    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (sidebar && toggle) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('is-open');
        });
    }

    // 2. Lógica do Modo Noturno
    const toggleButton = document.getElementById('darkModeToggle');
    const body = document.body;

    // Verificar preferência guardada anteriormente no navegador
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="bi bi-sun-fill me-1"></i> Modo Claro';
        }
    }

    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
                toggleButton.innerHTML = '<i class="bi bi-sun-fill me-1"></i> Modo Claro';
            } else {
                localStorage.setItem('theme', 'light');
                toggleButton.innerHTML = '<i class="bi bi-moon-fill me-1"></i> Modo Noturno';
            }
        });
    }
});