from django.shortcuts import render

# Create your views here.
def cliente_dashboard(request):
    
    if request.method == 'GET':
        return render(request,'/clientes/dashboard.html')