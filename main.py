from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from barbeiro.models import Barbeiro, Excecoes, Horarios_de_trabalho
from servicos.models import Servicos
from agendamentos.models import Agendamentos

def gerar_disponibilidade(barbeiro_id, servico_id, data_inicial):
    """
    Função que gera o calendário de horários disponíveis para um barbeiro
    considerando:
      - horário de trabalho
      - exceções (folgas, férias, ausências)
      - agendamentos já existentes
    """

    barbeiro = get_object_or_404(Barbeiro, id_barbeiro=barbeiro_id)
    servico = get_object_or_404(Servicos, id_servicos=servico_id)

    disponibilidade = []

    # Gera os próximos 7 dias (ex: quarta até próxima terça)
    for i in range(7):
        dia = data_inicial + timedelta(days=i)
        dia_semana = dia.weekday() + 1 if dia.weekday() < 6 else 0  
        # weekday() -> retorna um número de 0 a 6 (Segunda=0 ... Domingo=6)
        # Nosso array dias_da_semana começa em Domingo=0, então:
        #   Se for segunda a sábado (0 a 5), somamos 1
        #   Se for domingo (6), colocamos 0

        # Busca o horário de trabalho do barbeiro neste dia da semana
        horario_trabalho = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=barbeiro,
            dia_semana=dia_semana
        ).first()
        # .filter() retorna um QuerySet (tipo uma lista de objetos)
        # .first() retorna o primeiro objeto ou None se não existir

        if not horario_trabalho:
            continue  # se o barbeiro não trabalha nesse dia, pula o loop

        # Junta a data do dia com o horário de início e fim do expediente
        inicio = datetime.combine(dia, horario_trabalho.hora_inicio)
        fim = datetime.combine(dia, horario_trabalho.hora_fim)
        # datetime.combine(date, time) -> cria um datetime completo (data + hora)
        # Exemplo: 2025-11-12 + 09:00 => 2025-11-12 09:00:00

        # Duração do serviço em "slots" de 30 minutos
        duracao_slots = servico.slot_duracao_servico  
        # Ex: 1 = 30min, 2 = 1h, 3 = 1h30
        # Isso determina quantos blocos consecutivos o cliente precisa reservar

        slots = []
        atual = inicio
        while atual < fim:
            slot = {
                "inicio": atual,
                "fim": atual + timedelta(minutes=30),
                "status": "livre"  # começa livre e pode virar "ocupado" ou "excecao"
            }
            slots.append(slot)
            atual += timedelta(minutes=30)
        # Aqui criamos uma lista de dicionários, um pra cada bloco de 30min.
        # Exemplo:
        # [{"inicio": 09:00, "fim": 09:30, "status": "livre"}, ...]

        # Agora buscamos exceções e agendamentos para o barbeiro neste dia
        excecoes = Excecoes.objects.filter(
            fk_barbeiro=barbeiro,
            data_inicio__date=dia
        )
        agendamentos = Agendamentos.objects.filter(
            fk_barbeiro=barbeiro,
            data_e_horario__date=dia
        )

        # --- MARCA EXCEÇÕES ---
        for exc in excecoes:
            for slot in slots:
                # Se o horário do slot estiver dentro do intervalo da exceção
                if slot["inicio"] >= exc.data_inicio and slot["inicio"] < exc.data_fim:
                    slot["status"] = "excecao"

        # --- MARCA AGENDAMENTOS EXISTENTES ---
        for ag in agendamentos:
            duracao = ag.fk_servicos.slot_duracao_servico
            for slot in slots:
                # Se o slot estiver dentro do período do agendamento
                if slot["inicio"] >= ag.data_e_horario and slot["inicio"] < ag.data_e_horario + timedelta(minutes=30 * duracao):
                    slot["status"] = "ocupado"
        # Note que multiplicamos 30 minutos pela duração (em slots) do serviço agendado
        # pra bloquear o tempo correto. Ex: 2 slots = 1 hora = 30*2 minutos.

        disponibilidade.append({
            "dia": dia.strftime("%A %d/%m"),  # Ex: "Quarta 12/11"
            "slots": slots
        })

    return disponibilidade


