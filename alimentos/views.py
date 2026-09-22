from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ProtectedError, Sum, F, Q
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from datetime import date, timedelta
from .models import Alimento, Lote, Movimentacao
from .forms import AlimentoForm, MovimentacaoForm, CriarContaForm, CriarAlimentoForm, LoteForm
from django.db.models.expressions import ExpressionWrapper
from django.db.models import FloatField
from django.db.models.functions import Cast, Coalesce

# Páginas em gerais e dashboard

def inicio(request):
    return render(request, 'alimentos/inicio.html')

@login_required(login_url='login')
def dashboard(request):
    alimentos_faltantes = Alimento.objects.annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    
    hoje = date.today()
    limite_vencimento = hoje + timedelta(days=15)
    
    lotes_proximos_vencimento = Lote.objects.filter(
        data_validade__lte=limite_vencimento,
        quantidade_atual__gt=0
    ).order_by('data_validade')

    context = {
        'alimentos_faltantes': alimentos_faltantes,
        'lotes_proximos_vencimento': lotes_proximos_vencimento,
        'hoje': hoje,
    }
    return render(request, 'alimentos/dashboard.html', context)

# Listar os alimentos do estoque
def listar_alimentos(request):
    busca = request.GET.get('busca', '')
    
    alimentos = Alimento.objects.all().order_by('nome')

    if busca:
        alimentos = alimentos.filter(nome__icontains=busca)

    for alimento in alimentos:
        total_qnt = alimento.lotes.filter(quantidade_atual__gt=0).aggregate(total=Sum('quantidade_atual'))['total'] or 0.0
        alimento.total_estoque = total_qnt
        
        if alimento.quantidade_embalagem and alimento.quantidade_embalagem > 0:
            alimento.pacotes_totais = total_qnt / alimento.quantidade_embalagem
        else:
            alimento.pacotes_totais = 0.0

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

# Editar lote (número do lote, quantidade e validade)
def editar_lote(request, id):
    lote = get_object_or_404(Lote, id=id)
    form = LoteForm(request.POST or None, instance=lote)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote atualizado com sucesso!')
        return redirect('detalhes_alimento', id=lote.alimento.id)
    return render(request, 'alimentos/lote_form.html', {'form': form, 'lote': lote})

# Criar alimento
def criar_alimento(request):
    form = CriarAlimentoForm(request.POST or None)
    
    if form.is_valid():
        alimento = form.save()
        
        numero_lote = form.cleaned_data['numero_lote']
        data_validade = form.cleaned_data['data_validade']
        quantidade_pacotes = form.cleaned_data['quantidade_inicial']
        
        quantidade_real_estoque = quantidade_pacotes * alimento.quantidade_embalagem
        
        lote = Lote.objects.create(
            alimento=alimento,
            numero_lote=numero_lote,
            quantidade_atual=quantidade_real_estoque,
            data_validade=data_validade
        )
        
        Movimentacao.objects.create(
            lote=lote,
            tipo='ENTRADA',
            quantidade=quantidade_real_estoque
        )
        
        messages.success(request, 'Alimento e Lote Inicial cadastrados com sucesso!')
        return redirect('listar_alimentos')
        
    return render(request, 'alimentos/form.html', {'form': form})

# Atualizar alimento
def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento atualizado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

# Deletar alimento
def deletar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    tem_lotes = alimento.lotes.exists()

    if request.method == 'POST':
        if tem_lotes:
            messages.error(
                request,
                f'Não é possível excluir "{alimento.nome}" porque já existem lotes cadastrados para ele.'
            )
            return redirect('detalhes_alimento', id=alimento.id)

        try:
            alimento.delete()
        except ProtectedError:
            messages.error(request, f'Não é possível excluir "{alimento.nome}" porque existem lotes vinculados.')
            return redirect('detalhes_alimento', id=alimento.id)

        messages.success(request, 'Alimento removido do estoque.')
        return redirect('listar_alimentos')

    return render(request, 'alimentos/confirmar_delete.html', {'alimento': alimento, 'tem_lotes': tem_lotes})

# Autenticação
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
# Movimentação de lotes
# Movimentação de lotes
def movimentacao_estoque(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            alimento = form.cleaned_data['alimento']
            lote_selecionado = form.cleaned_data['numero_lote'] # Agora é um objeto Lote ou texto dependendo do fluxo
            quantidade_pacotes = form.cleaned_data['quantidade']
            data_validade = form.cleaned_data.get('data_validade')

            quantidade_real_estoque = quantidade_pacotes * alimento.quantidade_embalagem

            # --- SAÍDA ---
            if tipo == 'SAIDA':
                # Como virou um Select, o usuário escolhe um lote existente da lista
                lote = lote_selecionado
                
                if not lote or lote.quantidade_atual < quantidade_real_estoque:
                    pacotes_disponiveis = int(lote.quantidade_atual / alimento.quantidade_embalagem) if lote and alimento.quantidade_embalagem > 0 else 0
                    messages.error(
                        request,
                        f'Quantidade insuficiente. Este lote possui apenas {pacotes_disponiveis} pacotes disponíveis.'
                    )
                else:
                    lote.quantidade_atual -= quantidade_real_estoque
                    lote.save()

                    Movimentacao.objects.create(
                        lote=lote,
                        tipo=tipo,
                        quantidade=quantidade_real_estoque
                    )

                    messages.success(request, 'Saída registrada com sucesso!')
                    return redirect('movimentacao_estoque')

            # --- ENTRADA ---
            elif tipo == 'ENTRADA':
                # Na entrada, se ele selecionou um lote existente da lista, reaproveita. 
                # (Se você ainda permite digitar novo lote na entrada, tratamos aqui)
                if isinstance(lote_selecionado, Lote):
                    lote = lote_selecionado
                    lote.quantidade_atual += quantidade_real_estoque
                    lote.save()
                else:
                    # Caso seja um texto livre (se mantido)
                    numero_lote_str = str(lote_selecionado)
                    lote = Lote.objects.filter(alimento=alimento, numero_lote=numero_lote_str).first()
                    if lote:
                        lote.quantidade_atual += quantidade_real_estoque
                        lote.save()
                    else:
                        if not data_validade:
                            messages.error(request, 'Informe a data de validade para criar um novo lote.')
                            return render(request, 'alimentos/movimentacao.html', {'form': form})
                        
                        lote = Lote.objects.create(
                            alimento=alimento,
                            numero_lote=numero_lote_str,
                            quantidade_atual=quantidade_real_estoque,
                            data_validade=data_validade
                        )

                Movimentacao.objects.create(
                    lote=lote,
                    tipo=tipo,
                    quantidade=quantidade_real_estoque
                )

                messages.success(request, 'Entrada registrada com sucesso!')
                return redirect('movimentacao_estoque')
    else:
        form = MovimentacaoForm()

    return render(request, 'alimentos/movimentacao.html', {'form': form})

# Produtos em falta e Alerta de Estoque Mínimo
@login_required
def alerta_estoque_minimo(request):
    alimentos_criticos = Alimento.objects.annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    return render(request, 'alimentos/estoque_minimo.html', {'alimentos_criticos': alimentos_criticos})

@login_required
def produtos_em_falta(request):
    alimentos_faltantes = Alimento.objects.annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    return render(request, 'alimentos/produtos_em_falta.html', {'alimentos_faltantes': alimentos_faltantes})

@login_required(login_url='login')
def relatorios(request):
    return render(request, 'alimentos/relatorios.html')

def relatorio_movimentacoes(request, tipo):
    tipos_validos = {
        'entradas': ('ENTRADA', 'Entradas', 'entrada'),
        'saidas': ('SAIDA', 'Saídas', 'saída'),
    }

    if tipo not in tipos_validos:
        raise Http404('Tipo de relatório inválido.')

    tipo_valor, titulo, singular = tipos_validos[tipo]
    hoje = timezone.localdate()

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