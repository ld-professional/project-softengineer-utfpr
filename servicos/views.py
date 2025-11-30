from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
import json
from .models import Servicos

    

@login_required
@ensure_csrf_cookie
def excluir_servicos(request):

    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')

    if request.method == 'POST':

        data= json.loads(request.body)
        id_servico_selecionado= data['id_agendamentos']

        if id_servico_selecionado == None:
            return JsonResponse ({'status': 'nao existe','error':'selecione algo' })
        
        servico_selecionado=Servicos.objects.get(id_servicos=id_servico_selecionado)

        servico_selecionado.delete()

        return JsonResponse({'status': 'success'})

from .forms import ServicoForm

@login_required
@ensure_csrf_cookie
def barbeiros_editar_servicos(request):


    if hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')

    if request.method == 'GET':

        lista_servicos = Servicos.objects.all().order_by('nome_servico')
        
        contexto = {
            'servicos': lista_servicos
        }
        
        return render(request, 'servicos/editar-servicos.html', contexto)
    
    # 2. Lógica para SALVAR (Adicionar ou Editar)
    if request.method == 'POST':

        try:
            formulario = ServicoForm(request.POST)

            id_servico = request.POST.get('id_servico') # Mantemos o id fora do form para lógica de edição/criação
                                                        # explicacao n ofina lda funcao
            if formulario.is_valid():

                # Os dados foram VALIDADOS e estão limpos
                data_limpa = formulario.cleaned_data
                
                # Obtém os dados validados
                nome = data_limpa['nome_servico']
                preco = data_limpa['preco_servico']
                duracao = data_limpa['slot_duracao_servico']

        
                if id_servico: # para edicao de servico existente

                    servico = get_object_or_404(Servicos, pk=id_servico)
                    servico.nome_servico = nome
                    servico.preco_servico = preco
                    servico.slot_duracao_servico = duracao
                    servico.save()
                else: # par aedicao de servico ( onde pk n existe)

                    Servicos.objects.create(
                        nome_servico=nome,
                        preco_servico=preco,
                        slot_duracao_servico=duracao
                    )
                

                return redirect('barbeiro_editar_servicos')
            
            else:
                print("❌ Formulário Inválido:", formulario.errors)
                return redirect('barbeiro_editar_servicos')

        except Exception as e:
            print(f"Erro ao salvar serviço: {e}")

            return redirect('barbeiro_editar_servicos')


#id_servicos já é o primary_key do modelo e é gerenciado automaticamente pelo Django/Banco de Dados;
#  ele não é um campo que o usuário deve enviar ou que precise de validação de formato.

'''


Quando você usa um ModelForm, o Django espera que os fields que você lista sejam os atributos do modelo
 que o usuário está modificando.

 Se você incluísse o id_servico no ServicoForm, estaria tratando-o como um dado que precisa ser validado
   e mapeado para o modelo, o que é desnecessário para a operação principal de criação/edição dos atributos.

   

   



   mas eh bom validar ne pq vai q o id q veio eh um id errado...
     seria bom se nao veio nada ( nulo) logo criacao ,se veio mas n existe,
     logo erro de id inexistente ,e isso seria no forms q traria este erro ne ?


     No entanto, a validação de que o ID existe no banco de dados e a lógica de criação vs. edição 
     é responsabilidade da View, e não do Django Form.

     O Django Form (e o ModelForm) é projetado para validar os dados que serão salvos (nome, preço, etc.).
       A chave primária (id_servico) que identifica se o objeto já existe não faz parte dessa validação de dados do formulário.

A maneira correta de lidar com a verificação de existência do ID é na sua View:

1. Verificação de ID nulo ou vazio: (Lógica de Criação)

Se id_servico for nulo ou vazio, a View sabe que é um novo objeto a ser criado.

2. Verificação de ID válido, mas inexistente: (Lógica de Erro)

Quando a View tenta buscar o objeto com o ID fornecido, ela deve usar uma função que lida com o caso
 de o objeto não ser encontrado.

A função get_object_or_404 é perfeita para isso e você já a está usando corretamente!
'''