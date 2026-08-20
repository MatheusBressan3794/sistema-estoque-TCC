from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Alimento
from .forms import AlimentoForm

# --- Páginas Públicas & Autenticação ---

def inicio(request):
    return render(request, 'alimentos/inicio.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()

    return render(request, 'alimentos/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('login')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso! Faça seu login.")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'alimentos/cadastro.html', {'form': form})


# --- Páginas Protegidas (Exigem Login) ---

@login_required
def dashboard(request):
    return render(request, 'alimentos/dashboard.html')


@login_required
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


@login_required
def criar_alimento(request):
    form = AlimentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})


@login_required
def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})


@login_required
def deletar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    if request.method == 'POST':
        alimento.delete()
        return redirect('listar_alimentos')
    return render(request, 'alimentos/confirmar_delete.html', {'alimento': alimento})


@login_required
def movimentacao(request):
    return render(request, 'alimentos/movimentacao.html')


@login_required
def relatorios(request):
    return render(request, 'alimentos/relatorios.html')