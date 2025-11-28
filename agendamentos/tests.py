from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time, date

from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from clientes.models import Cliente
from .models import Agendamentos

from .views import buscar_horarios_api, validar_data_hora_futura

User = get_user_model()


class DisponibilidadeAPITeste(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('api_buscar_horarios')

        #Cria o ademir
        self.user_admin = User.objects.create_superuser(
            username='admin_test', password='senha_forte', email='admin@test.com', telefone='41999999999'
        )

        #Cria o user
        self.user_cliente = User.objects.create_user(
            username='client_test', password='senha_forte', email='client@test.com', telefone='41999999990'
        )
        self.cliente = Cliente.objects.create(fk_user=self.user_cliente)

        #Cria o barbeiro
        self.user_barbeiro = User.objects.create_user(
            username='barber_test', password='senha_forte', email='barber@test.com', telefone='41999999991'
        )
        self.barbeiro = Barbeiro.objects.create(fk_user=self.user_barbeiro)

        #Cria o serviço
        self.servico_60 = Servicos.objects.create(
            nome_servico='Corte e Barba', preco_servico=100.00, slot_duracao_servico=2
        )

        #Horario de trabalho
        self.dia_semana_num = 0 
        Horarios_de_trabalho.objects.create(
            fk_barbeiro=self.barbeiro,
            dia_semana=self.dia_semana_num,
            hora_inicio=time(9, 0),
            hora_fim=time(17, 0)
        )
        
        #Login
        self.client.login(username='client_test', password='senha_forte')


    def test_01_validacao_data_passada(self):
        data_passada = date(2020, 1, 1)
        self.assertFalse(validar_data_hora_futura(data_passada))

    def test_02_consulta_sem_barbeiro_no_dia(self):
        """A API deve retornar lista vazia se o barbeiro não trabalhar no dia."""
        data_quarta = date.today() + timedelta(days=((2 - date.today().weekday()) % 7))
        
        # Faz a requisição get
        response = self.client.get(self.url, {
            'data': data_quarta.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['horarios']), 0)


    def test_03_slot_disponivel_e_duracao_correta(self):
        """Verifica se todos os slots são gerados corretamente (9h às 17h para um serviço de 60 minutos)."""
        
        data_alvo = date.today() + timedelta(days=(0 - date.today().weekday() + 7) % 7)

        response = self.client.get(self.url, {
            'data': data_alvo.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Horários esperados: 9:00, 9:30, 10:00, ..., 16:00
        # Serviço de 60 min = 15 slots
        
        self.assertEqual(len(data['horarios']), 15) # Deve haver 15 slots de 30 min
        self.assertIn('09:00', data['horarios'])
        self.assertNotIn('16:30', data['horarios']) # 16:30 + 60min > 17:00

    def test_04_exclusao_por_agendamento(self):
        """Verifica se um agendamento existente bloqueia o horário corret"""
        
        data_alvo = date.today() + timedelta(days=(0 - date.today().weekday() + 7) % 7)
        inicio_agendamento = timezone.make_aware(datetime.combine(data_alvo, time(10, 0)))
        
        #Cria um agendamento que dura 60 minutos
        Agendamentos.objects.create(
            fk_cliente=self.cliente,
            fk_barbeiro=self.barbeiro,
            fk_servicos=self.servico_60,
            data_e_horario_inicio=inicio_agendamento
        )
        
        #Consulta a disponibilidade
        response = self.client.get(self.url, {
            'data': data_alvo.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        horarios = response.json()['horarios']

        # O agendamento de 10:00 (que dura 60 minutos) bloqueia:
        # 09:30 (porque 09:30 + 60 min colide com 10:00)
        # O agendamento de 10:00 - 11:00 bloqueia o início dos slots que colidem.
        # Slot 10:00 (Colide com o agendamento existente)
        # Slot 10:30 (Colide)
        
        self.assertNotIn('09:30', horarios) # O slot de 60 min que começa aqui ia dar bo
        self.assertNotIn('10:00', horarios) 
        self.assertNotIn('10:30', horarios) 
        self.assertIn('09:00', horarios) # Deve estar disponível
        self.assertIn('11:00', horarios) # Deve estar disponível