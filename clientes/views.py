from django.shortcuts import render

# Create your views here.
def cliente_dashboard(request):
    
    if request.body == 'GET':
        return render(request,'dashboard')