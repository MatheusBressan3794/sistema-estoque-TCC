document.addEventListener("DOMContentLoaded", function () {
    const selectTipo = document.querySelector("#id_tipo");
    const grupoValidade = document.querySelector("#grupo-data-validade");
    const inputValidade = document.querySelector("#id_data_validade");

    function atualizarCampos() {
        if (!selectTipo || !grupoValidade) return;

        if (selectTipo.value === "SAIDA") {
            grupoValidade.style.display = "none";
            if (inputValidade) {
                inputValidade.value = ""; // Limpa a data para não enviar dados fantasmas
                inputValidade.removeAttribute("required");
            }
        } else {
            grupoValidade.style.display = "block";
            if (inputValidade) {
                inputValidade.setAttribute("required", "required");
            }
        }
    }

    if (selectTipo) {
        selectTipo.addEventListener("change", atualizarCampos);
        atualizarCampos(); // Executa ao carregar a página
    }
});