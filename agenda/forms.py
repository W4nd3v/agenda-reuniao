from django import forms
from .models import Agendamento, Sala
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from datetime import datetime

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['sala', 'data', 'hora_inicio', 'hora_fim']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get("sala")
        data = cleaned_data.get("data")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")

        # Hora início antes de hora fim
        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise ValidationError("Hora de início deve ser antes da hora de fim.")

        # Verificar se a data/hora está no passado
        if data and hora_inicio:
            agora = make_aware(datetime.now())
            agendamento_datetime = make_aware(datetime.combine(data, hora_inicio))
            if agendamento_datetime < agora:
                raise ValidationError("Não é permitido agendar para datas/horários passados.")

        # Conflito com outros agendamentos
        if sala and data and hora_inicio and hora_fim:
            conflito = Agendamento.objects.filter(
                sala=sala,
                data=data,
                hora_inicio__lt=hora_fim,
                hora_fim__gt=hora_inicio
            ).exists()
            if conflito:
                raise ValidationError("Este horário já está reservado para a sala escolhida.")


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'localizacao', 'capacidade', 'microfone_disponivel']