document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('#app-sidebar');
    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (sidebar && toggle) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('is-open');
        });
    }
});