from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Paciente(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome
    
class PostoSaude(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return self.nome
    
class Estoque(models.Model):
    nome_vacina = models.CharField(max_length=100)
    lote = models.CharField(max_length=50)
    quantidade_atual = models.IntegerField(default=0)
    data_validade = models.DateField()
    fornecedor = models.CharField(max_length=100, default="Secretaria de Saúde")
    posto = models.ForeignKey(PostoSaude, on_delete=models.CASCADE, related_name='vacinas_estoque', null=True, blank=True)

    def __str__(self):
        return f"{self.nome_vacina} - Lote: {self.lote}"

class Vacina(models.Model):
    nome_vacina = models.CharField(max_length=100)
    lote = models.CharField(max_length=50)
    data_aplicacao = models.DateTimeField(auto_now_add=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    item_estoque = models.ForeignKey(Estoque, on_delete=models.SET_NULL, null=True, verbose_name="Vacina do Estoque")
    posto = models.ForeignKey('PostoSaude', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nome_vacina} - {self.paciente.nome}"

@receiver(post_save, sender=Vacina)
def baixar_estoque(sender, instance, created, **kwargs):
    if created and instance.item_estoque:
        estoque = instance.item_estoque
        if estoque.quantidade_atual > 0:
            estoque.quantidade_atual -= 1
            estoque.save()