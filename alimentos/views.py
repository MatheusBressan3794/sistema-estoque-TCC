from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.http import Http404, HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import Alimento, Lote, Movimentacao
from .forms import CriarContaForm, CriarAlimentoForm, AlimentoForm, LoteForm, MovimentacaoForm

def logout_view(request):
    logout(request) 
    return redirect('login')

# --- PÁGINAS GERAIS E DASHBOARD ---
@login_required
def inicio(request):
    return render(request, 'alimentos/inicio.html')

@login_required(login_url='login')
def dashboard(request):
    escola_usuario = request.user.perfil.etec
    
    alimentos_faltantes = Alimento.objects.filter(etec=escola_usuario).annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    
    hoje = date.today()
    limite_vencimento = hoje + timedelta(days=15)
    
    lotes_proximos_vencimento = Lote.objects.filter(
        etec=escola_usuario,
        data_validade__lte=limite_vencimento,
        quantidade_atual__gt=0
    ).order_by('data_validade')

    context = {
        'alimentos_faltantes': alimentos_faltantes,
        'lotes_proximos_vencimento': lotes_proximos_vencimento,
        'hoje': hoje,
    }
    return render(request, 'alimentos/dashboard.html', context)


# --- GESTÃO DE ALIMENTOS ---
@login_required
def listar_alimentos(request):
    escola_usuario = request.user.perfil.etec
    busca = request.GET.get('busca', '')
    
    alimentos = Alimento.objects.filter(etec=escola_usuario).order_by('nome')

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

@login_required
def detalhes_alimento(request, id):
    escola_usuario = request.user.perfil.etec
    alimento = get_object_or_404(Alimento, id=id, etec=escola_usuario)
    lotes = alimento.lotes.filter(quantidade_atual__gt=0).order_by('data_validade')

    return render(
        request,
        'alimentos/detalhes_alimento.html',
        {
            'alimento': alimento,
            'lotes': lotes
        }
    )

@login_required
def criar_alimento(request):
    escola_usuario = request.user.perfil.etec
    form = CriarAlimentoForm(request.POST or None)
    
    if form.is_valid():
        alimento = form.save(commit=False)
        alimento.etec = escola_usuario
        alimento.save()
        
        numero_lote = form.cleaned_data['numero_lote']
        data_validade = form.cleaned_data['data_validade']
        quantidade_pacotes = form.cleaned_data['quantidade_inicial']
        
        quantidade_real_estoque = quantidade_pacotes * alimento.quantidade_embalagem
        
        lote = Lote.objects.create(
            etec=escola_usuario,
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

@login_required
def atualizar_alimento(request, id):
    escola_usuario = request.user.perfil.etec
    alimento = get_object_or_404(Alimento, id=id, etec=escola_usuario)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento atualizado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

@login_required
def deletar_alimento(request, id):
    escola_usuario = request.user.perfil.etec
    alimento = get_object_or_404(Alimento, id=id, etec=escola_usuario)
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


# --- LOTES E EDIÇÃO ---
@login_required
def editar_lote(request, id):
    escola_usuario = request.user.perfil.etec
    lote = get_object_or_404(Lote, id=id, etec=escola_usuario)
    form = LoteForm(request.POST or None, instance=lote)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote atualizado com sucesso!')
        return redirect('detalhes_alimento', id=lote.alimento.id)
    return render(request, 'alimentos/lote_form.html', {'form': form, 'lote': lote})


# --- AUTENTICAÇÃO ---
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


# --- MOVIMENTAÇÃO DE ESTOQUE ---
@login_required
def movimentacao_estoque(request):
    escola_usuario = request.user.perfil.etec
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            alimento = form.cleaned_data['alimento']
            lote_selecionado = form.cleaned_data['numero_lote']
            quantidade_pacotes = form.cleaned_data['quantidade']
            data_validade = form.cleaned_data.get('data_validade')

            # Segurança Multitenancy: verificar se o alimento pertence à escola do utilizador
            if alimento.etec != escola_usuario:
                messages.error(request, 'Operação inválida para a sua unidade escolar.')
                return redirect('movimentacao_estoque')

            quantidade_real_estoque = quantidade_pacotes * alimento.quantidade_embalagem

            # --- SAÍDA ---
            if tipo == 'SAIDA':
                lote = lote_selecionado
                
                if not lote or lote.etec != escola_usuario or lote.quantidade_atual < quantidade_real_estoque:
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
                if isinstance(lote_selecionado, Lote) and lote_selecionado.etec == escola_usuario:
                    lote = lote_selecionado
                    lote.quantidade_atual += quantidade_real_estoque
                    lote.save()
                else:
                    numero_lote_str = str(lote_selecionado)
                    lote = Lote.objects.filter(etec=escola_usuario, alimento=alimento, numero_lote=numero_lote_str).first()
                    if lote:
                        lote.quantidade_atual += quantidade_real_estoque
                        lote.save()
                    else:
                        if not data_validade:
                            messages.error(request, 'Informe a data de validade para criar um novo lote.')
                            return render(request, 'alimentos/movimentacao.html', {'form': form})
                        
                        lote = Lote.objects.create(
                            etec=escola_usuario,
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


# --- ALERTAS E ESTOQUE MÍNIMO ---
@login_required
def alerta_estoque_minimo(request):
    escola_usuario = request.user.perfil.etec
    alimentos_criticos = Alimento.objects.filter(etec=escola_usuario).annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    return render(request, 'alimentos/estoque_minimo.html', {'alimentos_criticos': alimentos_criticos})

@login_required
def produtos_em_falta(request):
    escola_usuario = request.user.perfil.etec
    alimentos_faltantes = Alimento.objects.filter(etec=escola_usuario).annotate(
        total_estoque=Coalesce(Sum('lotes__quantidade_atual'), 0),
        estoque_minimo_calc=F('quantidade_minima') * F('quantidade_embalagem')
    ).filter(
        Q(total_estoque__lte=0) | 
        Q(total_estoque__lte=F('estoque_minimo_calc'))
    )
    return render(request, 'alimentos/produtos_em_falta.html', {'alimentos_faltantes': alimentos_faltantes})


# --- RELATÓRIOS E PDF ---
@login_required
def relatorios(request):
    return render(request, 'alimentos/relatorios.html')

@login_required
def relatorio_movimentacoes(request, tipo):
    escola_usuario = request.user.perfil.etec
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
        .filter(lote__etec=escola_usuario, tipo=tipo_valor, data_movimentacao__range=(data_inicio, data_fim))
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

@login_required
def exportar_pdf_movimentacoes(request, tipo):
    escola_usuario = request.user.perfil.etec
    tipos_validos = {
        'entradas': ('ENTRADA', 'Relatório de Entradas'),
        'saidas': ('SAIDA', 'Relatório de Saídas'),
    }

    if tipo not in tipos_validos:
        raise Http404('Tipo de relatório inválido.')

    tipo_valor, titulo = tipos_validos[tipo]
    hoje = timezone.localdate()

    try:
        data_inicio = date.fromisoformat(request.GET.get('data_inicio', str(hoje)))
    except ValueError:
        data_inicio = hoje

    try:
        data_fim = date.fromisoformat(request.GET.get('data_fim', str(hoje)))
    except ValueError:
        data_fim = hoje

    movimentacoes = (
        Movimentacao.objects
        .filter(lote__etec=escola_usuario, tipo=tipo_valor, data_movimentacao__range=(data_inicio, data_fim))
        .select_related('lote', 'lote__alimento')
        .order_by('-data_movimentacao', 'lote__alimento__nome')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{tipo}_{data_inicio}_a_{data_fim}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'TituloRelatorio',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#e65100'),
        spaceAfter=10
    )
    sub_style = ParagraphStyle(
        'SubTituloRelatorio',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20
    )

    elementos.append(Paragraph(titulo, titulo_style))
    elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}", sub_style))
    elementos.append(Spacer(1, 10))

    dados_tabela = [
        ['Data', 'Alimento', 'Lote', 'Quantidade']
    ]

    for mov in movimentacoes:
        alimento = mov.lote.alimento
        if alimento.quantidade_embalagem and alimento.quantidade_embalagem > 0:
            qtd_embalagens = int(mov.quantidade / alimento.quantidade_embalagem)
            qtd_str = f"{qtd_embalagens} {alimento.get_embalagem_display()}s ({mov.quantidade:.2f} {alimento.get_unidade_medida_display()})"
        else:
            qtd_str = f"{mov.quantidade:.2f} {alimento.get_unidade_medida_display()}"

        dados_tabela.append([
            mov.data_movimentacao.strftime('%d/%m/%Y'),
            alimento.nome,
            mov.lote.numero_lote,
            qtd_str
        ])

    if len(dados_tabela) == 1:
        dados_tabela.append(['-', 'Nenhum registro encontrado para este período.', '-', '-'])

    tabela = Table(dados_tabela, colWidths=[80, 160, 110, 190])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f57c00')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))

    elementos.append(tabela)
    doc.build(elementos)

    return response