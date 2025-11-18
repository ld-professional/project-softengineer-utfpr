from django.shortcuts import render

# Create your views here.

def pagina_inicial_home(request):
    """
    Esta view simplesmente renderiza a página principal (home).
    """
    # Retorna o template localizado em 'templates/core/home.html'
    return render(request, 'core/home.html')

