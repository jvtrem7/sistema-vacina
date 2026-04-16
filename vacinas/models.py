
from django.db import models

class Paciente(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

class Vacina(models.Model):
    nome_vacina = models.CharField(max_length=100)
    lote = models.CharField(max_length=50)
    data_aplicacao = models.DateTimeField(auto_now_add=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome_vacina} - {self.paciente.nome}"