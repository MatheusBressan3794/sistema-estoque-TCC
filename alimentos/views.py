from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Alimento
from .forms import AlimentoForm, CriarContaForm

# ==========================================
# GESTÃO DE ALIMENTOS / ESTOQUE
# ==========================================

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

def criar_alimento(request):
    form = AlimentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento cadastrado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Alimento atualizado com sucesso!')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

def deletar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    if request.method == 'POST':
        alimento.delete()
        messages.success(request, 'Alimento removido do estoque.')
        return redirect('listar_alimentos')
    return render(request, 'alimentos/confirmar_delete.html', {'alimento': alimento})

# ==========================================
# AUTENTICAÇÃO (CADASTRO E LOGIN)
# ==========================================

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

# ==========================================
# PÁGINAS GERAIS E DASHBOARD
# ==========================================

def inicio(request):
    return render(request, 'alimentos/inicio.html')

def dashboard(request):
    return render(request, 'alimentos/dashboard.html')

def movimentacao(request):
    return render(request, 'alimentos/movimentacao.html')

def relatorios(request):
    return render(request, 'alimentos/relatorios.html')