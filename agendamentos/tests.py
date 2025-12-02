from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta, time, date

from barbeiro.models import Barbeiro, Horarios_de_trabalho
from servicos.models import Servicos
from clientes.models import Cliente
from .models import Agendamentos
from .views import validar_data_hora_futura

User = get_user_model()


class DisponibilidadeAPITeste(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('api_buscar_horarios')

        #criamos o usuário
        self.user_cliente = User.objects.create_user(
            username='client_test',
            password='senha_forte',
            email='client@test.com',
            telefone='41999999990'
        )
        #criamos o cliente
        self.cliente = Cliente.objects.create(fk_user=self.user_cliente)
        #criamos o barbeiro
        self.user_barbeiro = User.objects.create_user(
            username='barber_test',
            password='senha_forte',
            email='barber@test.com',
            telefone='41999999991'
        )
        self.barbeiro = Barbeiro.objects.create(fk_user=self.user_barbeiro)

        # Login
        self.client.login(username='client_test', password='senha_forte')

        # Serviço de 60 min
        self.servico_60 = Servicos.objects.create(
            nome_servico='Corte e Barba',
            preco_servico=100.00,
            slot_duracao_servico=2  
        )

        # Barbeiro trabalha na segunda (0)
        self.weekday = 0
        Horarios_de_trabalho.objects.create(
            fk_barbeiro=self.barbeiro,
            dia_semana=self.weekday,
            hora_inicio=time(9, 0),
            hora_fim=time(17, 0)
        )

    #data passada não deve ser válida
    def test_01_validacao_data_passada(self):
        self.assertFalse(validar_data_hora_futura(date(2020, 1, 1)))

    #se o barbeiro não trabalha no dia, nada é retornado
    def test_02_consulta_sem_barbeiro_no_dia(self):
        hoje = date.today()

        dia_hoje = hoje.weekday()
        if dia_hoje == self.weekday:
            data_teste = hoje + timedelta(days=1)
        else:
            data_teste = hoje

        resp = self.client.get(self.url, {
            'data': data_teste.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })

        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data['horarios'], [])

    #verifica se os slots estão corretos
    def test_03_slots_disponiveis(self):
        hoje = date.today()
        dias_ate_segunda = (self.weekday - hoje.weekday() + 7) % 7

        if dias_ate_segunda == 0:
            dias_ate_segunda = 7

        data_teste = hoje + timedelta(days=dias_ate_segunda)

        resp = self.client.get(self.url, {
            'data': data_teste.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })

        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(len(data['horarios']), 15)
        self.assertIn('09:00', data['horarios'])
        self.assertIn('16:00', data['horarios'])

    #agendamentos já realizados devem limitar os horários adequadamente
    def test_04_bloqueio_por_agendamento(self):

        hoje = date.today()
        dias_ate_segunda = (self.weekday - hoje.weekday() + 7) % 7
        if dias_ate_segunda == 0:
            dias_ate_segunda = 7

        data_teste = hoje + timedelta(days=dias_ate_segunda)

        inicio_ag = timezone.make_aware(datetime.combine(data_teste, time(10, 0)))

        Agendamentos.objects.create(
            fk_cliente=self.cliente,
            fk_barbeiro=self.barbeiro,
            fk_servicos=self.servico_60,
            data_e_horario_inicio=inicio_ag
        )

        resp = self.client.get(self.url, {
            'data': data_teste.strftime('%Y-%m-%d'),
            'id_barbeiro': self.barbeiro.pk,
            'id_servico': self.servico_60.pk
        })

        self.assertEqual(resp.status_code, 200)
        horarios = resp.json()['horarios']

        self.assertNotIn('09:30', horarios)
        self.assertNotIn('10:00', horarios)
        self.assertNotIn('10:30', horarios)
        self.assertIn('09:00', horarios)
        self.assertIn('11:00', horarios)