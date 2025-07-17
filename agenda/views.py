from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .forms import AgendamentoForm, SalaForm
from .models import Agendamento, Sala
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import calendar
from datetime import date, datetime
from django.utils.dateparse import parse_date, parse_time
from django.utils.timezone import now

@login_required
def detalhes_dia(request, sala_id, data):
    sala = get_object_or_404(Sala, pk=sala_id)
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Data inválida.')
        return redirect('agenda:dashboard')

    agendamentos = Agendamento.objects.filter(sala=sala, data=data_obj).order_by('hora_inicio')
    agora = now()

    return render(request, 'agenda/agendamentos/detalhes_dia.html', {
        'sala': sala,
        'data': data_obj,
        'agendamentos': agendamentos,
        'agora': agora
    })


@login_required
def dashboard_salas(request):
    salas = Sala.objects.all()
    return render(request, 'agenda/dashboard.html', {'salas': salas})


@login_required
def meus_agendamentos(request):
    agendamentos = Agendamento.objects.filter(criador=request.user).order_by('-data', '-hora_inicio')

    status = request.GET.get('status')
    hoje = timezone.localdate()

    if status == 'futuros':
        agendamentos = agendamentos.filter(data__gte=hoje)
    elif status == 'realizados':
        agendamentos = agendamentos.filter(data__lt=hoje)
    elif status == 'cancelados':
        # se for implementado campo `cancelado` ou `ativo`, aplicar aqui
        pass

    return render(request, 'agenda/agendamentos/lista.html', {
        'agendamentos': agendamentos,
        'modo': 'meus'
    })


@staff_member_required
def todos_agendamentos(request):
    agendamentos = Agendamento.objects.all().order_by('-data', '-hora_inicio')

    filtro_data = request.GET.get('data')
    filtro_tipo = request.GET.get('tipo_evento')  # se for implementado

    if filtro_data:
        agendamentos = agendamentos.filter(data=filtro_data)

    return render(request, 'agenda/agendamentos/lista.html', {
        'agendamentos': agendamentos,
        'modo': 'admin'
    })


TECNICOS_EMAILS = [
    'wanderson.info@tuboarte.com.br',
    # 'support@tuboarte.com.br',
    # 'henrique.info@tuboarte.com.br',
    # 'adeliano.info@tuboarte.com.br',
    # 'central@tuboarte.com.br'
]
@login_required
def novo_agendamento(request):
    sala_id = request.GET.get('sala')
    data_raw = request.GET.get('data')  # ex: "2025-07-18"
    hora_inicio_raw = request.GET.get('hora_inicio')  # ex: "14:00"
    hora_fim_raw = request.GET.get('hora_fim')  # ex: "15:30"

    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.criador = request.user
            agendamento.save()
            return redirect('agenda:meus_agendamentos')
    else:
        inicial = {}
        if sala_id:
            inicial['sala'] = sala_id
        if data_raw:
            data_formatada = parse_date(data_raw)
            if data_formatada:
                inicial['data'] = data_formatada
        if hora_inicio_raw:
            hora_ini = parse_time(hora_inicio_raw)
            if hora_ini:
                inicial['hora_inicio'] = hora_ini
        if hora_fim_raw:
            hora_fim = parse_time(hora_fim_raw)
            if hora_fim:
                inicial['hora_fim'] = hora_fim

        form = AgendamentoForm(initial=inicial)

    return render(request, 'agenda/novo.html', {'form': form})
# @login_required
# def novo_agendamento(request):
#     sala_id = request.GET.get('sala')
#     data_inicial = request.GET.get('data')

#     if request.method == 'POST':
#         form = AgendamentoForm(request.POST)
#         if form.is_valid():
#             agendamento = form.save(commit=False)
#             agendamento.criador = request.user
#             agendamento.save()
#             # Envia email etc...
#             return redirect('agenda:meus_agendamentos')
#     else:
#         inicial = {}
#         if sala_id:
#             inicial['sala'] = sala_id
#         if data_inicial:
#             inicial['data'] = data_inicial
#         form = AgendamentoForm(initial=inicial)

#     return render(request, 'agenda/novo.html', {'form': form})
# @login_required
# def novo_agendamento(request):
#     if request.method == 'POST':
#         form = AgendamentoForm(request.POST)
#         if form.is_valid():
#             agendamento = form.save(commit=False)
#             agendamento.criador = request.user
#             agendamento.save()
#             # Notificar por e-mail
#             destinatarios = [request.user.email] + TECNICOS_EMAILS
#             send_mail(
#                 subject='Novo Agendamento de Sala',
#                 message=f'{request.user.get_full_name()} agendou {agendamento.sala.nome} em {agendamento.data} das {agendamento.hora_inicio} às {agendamento.hora_fim}.',
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=destinatarios
#             )
#             messages.success(request, 'Agendamento realizado com sucesso!')
#             return redirect('meus_agendamentos')
#     else:
#         form = AgendamentoForm()
#     return render(request, 'agenda/novo.html', {'form': form})

# @login_required
# def meus_agendamentos(request):
#     agendamentos = Agendamento.objects.filter(criador=request.user)
#     return render(request, 'agenda/lista.html', {'agendamentos': agendamentos})

@login_required
def cancelar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk, criador=request.user)
    if request.method == 'POST':
        agendamento.delete()
        messages.success(request, 'Agendamento cancelado com sucesso.')
        return redirect('agenda:meus_agendamentos')
    return render(request, 'agenda/cancelar.html', {'agendamento': agendamento})


def teste(request):
    return HttpResponse("Teste de view funcionando!")


@staff_member_required
def listar_salas(request):
    salas = Sala.objects.all()
    return render(request, 'agenda/salas/listar.html', {'salas': salas})

@staff_member_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala criada com sucesso!')
            return redirect('agenda:listar_salas')
    else:
        form = SalaForm()
    return render(request, 'agenda/salas/form.html', {'form': form, 'titulo': 'Nova Sala'})

@staff_member_required
def editar_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala atualizada com sucesso!')
            return redirect('agenda:listar_salas')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'agenda/salas/form.html', {'form': form, 'titulo': 'Editar Sala'})

@staff_member_required
def excluir_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        sala.delete()
        messages.success(request, 'Sala excluída com sucesso!')
        return redirect('agenda:listar_salas')
    return render(request, 'agenda/salas/confirmar_exclusao.html', {'sala': sala})


@login_required
def calendario_sala(request, sala_id, ano=None, mes=None):
    sala = get_object_or_404(Sala, pk=sala_id)
    
    today = date.today()
    ano = int(ano) if ano else today.year
    mes = int(mes) if mes else today.month

    cal = calendar.Calendar(firstweekday=0)
    dias_mes = cal.itermonthdates(ano, mes)

    # Buscar agendamentos do mês
    agendamentos = Agendamento.objects.filter(
        sala=sala,
        data__year=ano,
        data__month=mes
    ).values_list('data', flat=True).distinct()

    dias_com_agendamento = set(agendamentos)

    # Matriz de semanas do calendário
    semanas = []
    semana = []

    for dia in dias_mes:
        tem_agendamento = dia in dias_com_agendamento
        semana.append({
            'dia': dia,
            'mes_atual': dia.month == mes,
            'tem_agendamento': tem_agendamento,
        })
        if len(semana) == 7:
            semanas.append(semana)
            semana = []

    contexto = {
        'sala': sala,
        'ano': ano,
        'mes': mes,
        'mes_nome': calendar.month_name[mes].capitalize(),
        'semanas': semanas,
        'anterior': (ano, mes - 1) if mes > 1 else (ano - 1, 12),
        'proximo': (ano, mes + 1) if mes < 12 else (ano + 1, 1),
    }

    return render(request, 'agenda/agendamentos/calendario.html', contexto)