from django.shortcuts import render

# Create your views here.


# o fluxo para login eh views -> backends.py o CONTEXTO do strategy/ 
# orquestrador = a) escolher o metodo b) buscar o suposto usuario e senha
#
#entao  backends.py-> loginContratoStrategy.py --> gera strategies.py  ( com emailchecker telefonechecker )
#
#detalhe q o bakcends.py tem uma cnstrucao ctrl c + ctrl v e ele espera receber username 
#
#mas o detalhe eh q username eh so o nome da variavel, e vamos passar para username o identifier

def login_view():
    ...