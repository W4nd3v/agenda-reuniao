from django.db import models
from django.contrib.auth.models import User

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=150)
    capacidade = models.PositiveIntegerField()
    microfone_disponivel = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nome} ({self.localizacao})'

class Agendamento(models.Model):
    criador = models.ForeignKey(User, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sala.nome} - {self.data} - {self.hora_inicio}'

    class Meta:
        ordering = ['data', 'hora_inicio']
