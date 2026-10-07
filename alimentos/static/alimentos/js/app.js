document.addEventListener('DOMContentLoaded', function () {
    // 1. Lógica da Sidebar Responsiva (Mobile / Toggle)
    const sidebar = document.querySelector('#app-sidebar');
    const toggle = document.querySelector('[data-sidebar-toggle]');
    const appLayout = document.querySelector('#appLayout');

    if (sidebar && toggle) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('is-open');
            if (appLayout) {
                appLayout.classList.toggle('sidebar-expanded');
            }
        });

        // Opcional: Fecha a sidebar ao clicar fora em ecrãs móveis
        document.addEventListener('click', function (event) {
            if (window.innerWidth < 992) {
                const isClickInside = sidebar.contains(event.target) || toggle.contains(event.target);
                if (!isClickInside && sidebar.classList.contains('is-open')) {
                    sidebar.classList.remove('is-open');
                    if (appLayout) {
                        appLayout.classList.remove('sidebar-expanded');
                    }
                }
            }
        });
    }

    // 2. Lógica do Modo Noturno (Dark Mode) com persistência em localStorage
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