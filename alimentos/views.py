from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Alimento, Lote, Movimentacao
from .forms import AlimentoForm, MovimentacaoForm, CriarContaForm, CriarAlimentoForm, LoteForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from datetime import date
from django.db.models import Sum
from django.http import Http404
from django.utils import timezone

# Páginas em gerais e dashboard

def inicio(request):
    return render(request, 'alimentos/inicio.html')

@login_required(login_url='login')
def dashboard(request):
    alimentos_faltantes = Alimento.objects.filter(quantidade_embalagem__lte=0)
    
    # Lotes vencidos OU próximos do vencimento (próximos 15 dias)
    hoje = date.today()
    limite_vencimento = hoje + timedelta(days=15)
    
    lotes_proximos_vencimento = Lote.objects.filter(
        data_validade__lte=limite_vencimento, # Removemos o data_validade__gte=hoje daqui
        quantidade_atual__gt=0
    ).order_by('data_validade')

    context = {
        'alimentos_faltantes': alimentos_faltantes,
        'lotes_proximos_vencimento': lotes_proximos_vencimento,
        'hoje': hoje, # Adicionamos o "hoje" aqui para o HTML conseguir usar
    }
    return render(request, 'alimentos/dashboard.html', context)

# Listar os alimentos do estoque
def listar_alimentos(request):
    busca = request.GET.get('busca', '')
    alimentos = Alimento.objects.all()

    if busca:
        alimentos = alimentos.filter(nome__icontains=busca)

    return render(
        request,
        'alimentos/lista.html',
        {
            'alimentos': alimentos,
            'busca': busca
        }
    )

# Detalhes do alimento e seus lotes
def detalhes_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    lotes = alimento.lotes.filter(quantidade_atual__gt=0).order_by('data_validade')

    return render(
        request,
        'alimentos/detalhes_alimento.html',
        {
            'alimento': alimento,
            'lotes': lotes
        }
    )

#Editar lote (número do lote, quantidade e validade)
def editar_lote(request, id):
    lote = get_object_or_404(Lote, id=id)
    form = LoteForm(request.POST or None, instance=lote)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote atualizado com sucesso!')
        return redirect('detalhes_alimento', id=lote.alimento.id)
    return render(request, 'alimentos/lote_form.html', {'form': form, 'lote': lote})

# Criar alimento (AGORA COM LOTE OBRIGATÓRIO)
def criar_alimento(request):
    form = CriarAlimentoForm(request.POST or None)
    
    if form.is_valid():
        # 1. Salva o alimento no banco
        alimento = form.save()
        
        # 2. Pega os dados do lote que o usuário digitou
        numero_lote = form.cleaned_data['numero_lote']
        data_validade = form.cleaned_data['data_validade']
        quantidade_inicial = form.cleaned_data['quantidade_inicial']
        
        # 3. Cria o lote automaticamente vinculado ao alimento
        lote = Lote.objects.create(
            alimento=alimento,
            numero_lote=numero_lote,
            quantidade_atual=quantidade_inicial,
            data_validade=data_validade
        )
        
        # 4. Registra a movimentação de ENTRADA para o histórico
        Movimentacao.objects.create(
            lote=lote,
            tipo='ENTRADA',
            quantidade=quantidade_inicial
        )
        
        messages.success(request, 'Alimento e Lote Inicial cadastrados com sucesso!')
        return redirect('listar_alimentos')
        
    return render(request, 'alimentos/form.html', {'form': form})

# Atualizar alimento (Mantém o form antigo para não exigir lote na edição)
def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento atualizado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

# Deletar alimento que não possui lote cadastrado
def deletar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    tem_lotes = alimento.lotes.exists()

    if request.method == 'POST':
        if tem_lotes:
            messages.error(
                request,
                f'Não é possível excluir "{alimento.nome}" porque já existem '
                f'lotes cadastrados para ele. Remova ou zere os lotes antes '
                f'de excluir o alimento.'
            )
            return redirect('detalhes_alimento', id=alimento.id)

        try:
            alimento.delete()
        except ProtectedError:
            messages.error(
                request,
                f'Não é possível excluir "{alimento.nome}" porque existem '
                f'lotes ou movimentações vinculados a ele.'
            )
            return redirect('detalhes_alimento', id=alimento.id)

        messages.success(request, 'Alimento removido do estoque.')
        return redirect('listar_alimentos')

    return render(
        request,
        'alimentos/confirmar_delete.html',
        {'alimento': alimento, 'tem_lotes': tem_lotes}
    )

# Autenticação (CADASTRO E LOGIN)

def cadastro(request):
    if request.method == 'POST':
        form = CriarContaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para entrar.')
            return redirect('login')
    else:
        form = CriarContaForm()
    
    return render(request, 'alimentos/cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = AuthenticationForm()

    return render(request, 'alimentos/login.html', {'form': form})

# Movimentação de lotes
def movimentacao_estoque(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            alimento = form.cleaned_data['alimento']
            numero_lote = form.cleaned_data['numero_lote']
            quantidade = form.cleaned_data['quantidade']
            data_validade = form.cleaned_data['data_validade']

            lote = Lote.objects.filter(
                alimento=alimento,
                numero_lote=numero_lote
            ).first()

            # ENTRADA
            if tipo == 'ENTRADA':
                if lote:
                    lote.quantidade_atual += quantidade
                    lote.save()
                else:
                    lote = Lote.objects.create(
                        alimento=alimento,
                        numero_lote=numero_lote,
                        quantidade_atual=quantidade,
                        data_validade=data_validade
                    )

                Movimentacao.objects.create(
                    lote=lote,
                    tipo=tipo,
                    quantidade=quantidade
                )

                messages.success(
                    request,
                    'Entrada registrada com sucesso!'
                )

                return redirect('movimentacao_estoque')

            # SAÍDA
            elif tipo in ('SAIDA'):
                if not lote:
                    messages.error(
                        request,
                        'O lote informado não existe para esse alimento.'
                    )
                elif lote.quantidade_atual < quantidade:
                    messages.error(
                        request,
                        f'Quantidade insuficiente. '
                        f'Esse lote possui apenas '
                        f'{lote.quantidade_atual} embalagens.'
                    )
                else:
                    lote.quantidade_atual -= quantidade
                    lote.save()

                    Movimentacao.objects.create(
                        lote=lote,
                        tipo=tipo,
                        quantidade=quantidade
                    )

                    messages.success(
                        request,
                        'Saída registrada com sucesso!'
                    )

                    return redirect('movimentacao_estoque')
    else:
        form = MovimentacaoForm()

    return render(
        request,
        'alimentos/movimentacao.html',
        {'form': form}
    )

# Produtos em falta
@login_required
def produtos_em_falta(request):
    alimentos_faltantes = Alimento.objects.filter(quantidade_embalagem__lte=0)
    
    context = {
        'alimentos_faltantes': alimentos_faltantes,
    }
    return render(request, 'alimentos/produtos_em_falta.html', context)


@login_required(login_url='login')
def relatorios(request):
    return render(request, 'alimentos/relatorios.html')

#Relatório de movimentações (entradas ou saídas), filtrável por data
def relatorio_movimentacoes(request, tipo):

    tipos_validos = {
        'entradas': ('ENTRADA', 'Entradas', 'entrada'),
        'saidas': ('SAIDA', 'Saídas', 'saída'),
    }

    if tipo not in tipos_validos:
        raise Http404('Tipo de relatório inválido.')

    tipo_valor, titulo, singular = tipos_validos[tipo]
    hoje = timezone.localdate()

    # Se a data vier vazia ou inválida no GET, cai no padrão: hoje
    try:
        data_inicio = date.fromisoformat(request.GET.get('data_inicio', ''))
    except ValueError:
        data_inicio = hoje

    try:
        data_fim = date.fromisoformat(request.GET.get('data_fim', ''))
    except ValueError:
        data_fim = hoje

    movimentacoes = (
        Movimentacao.objects
        .filter(tipo=tipo_valor, data_movimentacao__range=(data_inicio, data_fim))
        .select_related('lote', 'lote__alimento')
        .order_by('-data_movimentacao', 'lote__alimento__nome')
    )

    total_quantidade = movimentacoes.aggregate(total=Sum('quantidade'))['total'] or 0

    return render(
        request,
        'alimentos/relatorio_movimentacoes.html',
        {
            'tipo': tipo,
            'titulo': titulo,
            'singular': singular,
            'movimentacoes': movimentacoes,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'total_quantidade': total_quantidade,
        }
    )