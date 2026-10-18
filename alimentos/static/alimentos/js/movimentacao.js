// Tela de movimentação: filtra os lotes pelo alimento escolhido e
// alterna os campos conforme o tipo (entrada ou saída)
document.addEventListener('DOMContentLoaded', function () {
    var tipo = document.getElementById('id_tipo');
    var alimento = document.getElementById('id_alimento');
    var loteSelect = document.getElementById('id_numero_lote');
    var novoLote = document.getElementById('id_novo_lote');
    var grupoLote = document.getElementById('grupo-lote-existente');
    var grupoNovo = document.getElementById('grupo-novo-lote');
    var grupoValidade = document.getElementById('grupo-data-validade');
    var inputValidade = document.getElementById('id_data_validade');
    var labelLote = grupoLote.querySelector('label');

    // Guarda as opções originais do select de lotes
    var opcoes = Array.prototype.slice.call(loteSelect.options);
    var opcaoVazia = opcoes.filter(function (o) { return o.value === ''; })[0];
    var opcoesLotes = opcoes.filter(function (o) { return o.value !== ''; });

    // Mostra no select só os lotes do alimento escolhido
    function filtrarLotes() {
        var selecionado = loteSelect.value;
        var idAlimento = alimento.value;
        var visiveis = opcoesLotes.filter(function (o) {
            return idAlimento !== '' && o.getAttribute('data-alimento') === idAlimento;
        });

        loteSelect.innerHTML = '';
        loteSelect.appendChild(opcaoVazia);
        visiveis.forEach(function (o) { loteSelect.appendChild(o); });

        if (idAlimento === '') {
            opcaoVazia.textContent = 'Selecione um alimento primeiro';
        } else if (visiveis.length === 0) {
            opcaoVazia.textContent = 'Nenhum lote com estoque para este alimento';
        } else {
            opcaoVazia.textContent = 'Selecione um lote';
        }

        var aindaValido = visiveis.some(function (o) { return o.value === selecionado; });
        loteSelect.value = aindaValido ? selecionado : '';
    }

    // A data de validade só aparece quando está sendo criado um lote novo.
    // Quando esconde, limpa a data pra não enviar dados fantasmas.
    function atualizarValidade() {
        var mostrar = tipo.value === 'ENTRADA' && novoLote.value.trim() !== '';
        grupoValidade.style.display = mostrar ? '' : 'none';
        if (!mostrar && inputValidade) { inputValidade.value = ''; }
    }

    // Entrada: pode escolher lote existente OU digitar um novo. Saída: só lote existente.
    function atualizarCampos() {
        var entrada = tipo.value === 'ENTRADA';
        grupoNovo.style.display = entrada ? '' : 'none';
        labelLote.textContent = entrada ? 'Lote existente:' : 'Lote:';
        if (!entrada) { novoLote.value = ''; }
        atualizarValidade();
    }

    tipo.addEventListener('change', atualizarCampos);
    alimento.addEventListener('change', filtrarLotes);

    novoLote.addEventListener('input', function () {
        if (novoLote.value.trim() !== '') { loteSelect.value = ''; }
        atualizarValidade();
    });

    loteSelect.addEventListener('change', function () {
        if (loteSelect.value !== '') { novoLote.value = ''; atualizarValidade(); }
    });

    filtrarLotes();
    atualizarCampos();
});