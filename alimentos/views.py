from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from .models import Alimento
from .forms import AlimentoForm

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
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

def atualizar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    form = AlimentoForm(request.POST or None, instance=alimento)
    if form.is_valid():
        form.save()
        return redirect('listar_alimentos')
    return render(request, 'alimentos/form.html', {'form': form})

def deletar_alimento(request, id):
    alimento = get_object_or_404(Alimento, id=id)
    if request.method == 'POST':
        alimento.delete()
        return redirect('listar_alimentos')
    return render(request, 'alimentos/confirmar_delete.html', {'alimento': alimento})
