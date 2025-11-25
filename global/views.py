from django.shortcuts import render,redirect 
import core.constantes as t
from servicos.models import Servicos



def pagina_inicial_home(request):
  
    servicos_list = Servicos.objects.all()
    
    context = {
        'servicos': servicos_list,
    }
    
    return render(request, t.HOME, context)



def verficacao_login_agendar(request):


    if request.user.is_authenticated:
        return redirect('clientepagina_inicial_dashboard')
     
    else:
        return redirect('login')
                                          
    