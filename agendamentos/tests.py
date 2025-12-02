from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time, date

# Mantenha suas importações de models aqui...
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from clientes.models import Cliente
from .models import Agendamentos
from .views import buscar_horarios_api, validar_data_hora_futura

User = get_user_model()

class DisponibilidadeAPITeste(TestCase):

    def setUp(self):
        # MANTENHA O SETUP EXATAMENTE COMO ESTAVA
        self.client = Client()
        self.url = reverse('api_buscar_horarios')

        self.user_admin = User.objects.create_superuser(
            username='admin_test', password='senha_forte', email='admin@test.com', telefone='41999999999'
        )
        self.user_cliente = User.objects.create_user(
            username='client_test', password='senha_forte', email='client@test.com', telefone='41999999990'
        )
        self.cliente = Cliente.objects.create(fk_user=self.user_cliente)

        self.user_barbeiro = User.objects.create_user(
            username='barber_test', password='senha_forte', email='barber@test.com', telefone='41999999991'
        )
        self.barbeiro = Barbeiro.objects.create(fk_user=self.user_barbeiro)

        self.servico_60 = Servicos.objects.create(
            nome_servico='Corte e Barba', preco_servico=100.00, slot_duracao_servico=2
        )

        # Barbeiro trabalha na SEGUNDA-FEIRA (0)
        self.dia_semana_num = 0 
        Horarios_de_trabalho.objects.create(
            fk_barbeiro=self.barbeiro,
            dia_semana=self.dia_semana_num,
            hora_inicio=time(9, 0),
            hora_fim=time(17, 0)
        )
        
        self.client.login(username='client_test', password='senha_forte')

    def test_01_validacao_data_passada(self):
        data_passada = date(2020, 1, 1)
        self.assertFalse(validar_data_hora_futura(data_passada))

    def test_02_consulta_sem_barbeiro_no_dia(self):
        """A API deve retornar lista vazia se o barbeiro não trabalhar no dia."""
        # Se hoje é segunda(0), 2-0 = 2 (Quarta). Quarta o barbeiro não trabalha.
        data_quarta = date.today() + timedelta(days=((2 - date.today().weekday()) % 7))
        
        response = self.client.get(self.url, {
            'data': data_quarta.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['horarios']), 0)

    def test_03_slot_disponivel_e_duracao_correta(self):
        """Verifica slots gerados. Se cair hoje, pula pra semana que vem para evitar erro de horário passado."""
        
        hoje = date.today()
        dias_para_frente = (self.dia_semana_num - hoje.weekday() + 7) % 7
        
        # CORREÇÃO CRÍTICA: Se for hoje (0), soma 7 dias.
        # Isso garante que pegamos a próxima segunda, com horário LIVRE.
        if dias_para_frente == 0:
            dias_para_frente = 7
            
        data_alvo = hoje + timedelta(days=dias_para_frente)

        response = self.client.get(self.url, {
            'data': data_alvo.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Agora sim, deve haver 15 slots (9:00 até 16:00 inicio)
        self.assertEqual(len(data['horarios']), 15) 
        self.assertIn('09:00', data['horarios'])

    def test_04_exclusao_por_agendamento(self):
        """Verifica bloqueio de horário."""
        
        # CORREÇÃO CRÍTICA: Mesma lógica, garantir data futura
        hoje = date.today()
        dias_para_frente = (self.dia_semana_num - hoje.weekday() + 7) % 7
        if dias_para_frente == 0:
            dias_para_frente = 7
            
        data_alvo = hoje + timedelta(days=dias_para_frente)
        
        # Cria agendamento às 10:00 na data futura
        inicio_agendamento = timezone.make_aware(datetime.combine(data_alvo, time(10, 0)))
        
        Agendamentos.objects.create(
            fk_cliente=self.cliente,
            fk_barbeiro=self.barbeiro,
            fk_servicos=self.servico_60,
            data_e_horario_inicio=inicio_agendamento
        )
        
        response = self.client.get(self.url, {
            'data': data_alvo.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })
        
        self.assertEqual(response.status_code, 200)
        horarios = response.json()['horarios']

        # 10:00 bloqueia 09:30, 10:00 e 10:30 (para serviço de 60m / slot de 30m)
        self.assertNotIn('09:30', horarios) 
        self.assertNotIn('10:00', horarios) 
        self.assertNotIn('10:30', horarios) 
        self.assertIn('09:00', horarios) 
        self.assertIn('11:00', horarios)