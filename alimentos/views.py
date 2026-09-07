from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Alimento, Lote, Movimentacao
from .forms import AlimentoForm, MovimentacaoForm, CriarContaForm

#Listar os alimentos do estoque
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
    #Mostra lotes com 1 ou mais cadastros
    lotes = alimento.lotes.filter(quantidade_atual__gt=0).order_by('data_validade')

    return render(
        request,
        'alimentos/detalhes_alimento.html',
        {
            'alimento': alimento,
            'lotes': lotes
        }
    )

#Criar alimento
def criar_alimento(request):
    form = AlimentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento cadastrado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

#Atualizar alimento
def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento atualizado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

#Deletar alimento que não possui lote cadastrado
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

#Autenticação (CADASTRO E LOGIN)

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

#Páginas em gerais e dashboard

def inicio(request):
    return render(request, 'alimentos/inicio.html')

def dashboard(request):
    return render(request, 'alimentos/dashboard.html')

def relatorios(request):
    return render(request, 'alimentos/relatorios.html')

def movimentacao_estoque(request):

    if request.method == 'POST':

        form = MovimentacaoForm(request.POST)

        if form.is_valid():

            tipo = form.cleaned_data['tipo']
            alimento = form.cleaned_data['alimento']
            numero_lote = form.cleaned_data['numero_lote']
            quantidade = form.cleaned_data['quantidade']
            data_validade = form.cleaned_data['data_validade']

            # Procura o lote daquele alimento
            lote = Lote.objects.filter(
                alimento=alimento,
                numero_lote=numero_lote
            ).first()

            # ENTRADA
            if tipo == 'ENTRADA':

                if lote:
                    # Se o lote já existe, soma a quantidade
                    lote.quantidade_atual += quantidade
                    lote.save()

                else:
                    # Se o lote não existe, cria um novo
                    lote = Lote.objects.create(
                        alimento=alimento,
                        numero_lote=numero_lote,
                        quantidade_atual=quantidade,
                        data_validade=data_validade
                    )

                # Registra a movimentação
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
            elif tipo in ('SAIDA', 'DESCARTE'):

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

                    # Retira a quantidade do lote
                    lote.quantidade_atual -= quantidade
                    lote.save()

                    # Registra a movimentação
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