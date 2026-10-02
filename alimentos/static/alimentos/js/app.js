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
    const updateThemeButton = (isDark) => {
        if (!toggleButton) return;

        if (toggleButton.classList.contains('auth-theme-toggle')) {
            const icon = isDark ? 'bi-sun-fill' : 'bi-moon-fill';
            const label = isDark ? 'Ativar modo claro' : 'Ativar modo escuro';
            toggleButton.innerHTML = `<i class="bi ${icon}" aria-hidden="true"></i>`;
            toggleButton.setAttribute('aria-label', label);
            toggleButton.title = label;
            return;
        }

        toggleButton.innerHTML = isDark
            ? '<i class="bi bi-sun-fill me-1"></i> Modo Claro'
            : '<i class="bi bi-moon-fill me-1"></i> Modo Noturno';
    };

    // Verificar preferência guardada anteriormente no navegador
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        updateThemeButton(true);
    }

    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
                updateThemeButton(true);
            } else {
                localStorage.setItem('theme', 'light');
                updateThemeButton(false);
            }
        });
    }
});