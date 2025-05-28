from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Area(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Área de Programação"
        verbose_name_plural = "Áreas de Programação"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    @property
    def total_enquetes(self):
        return self.enquete_set.count()

    @property
    def enquetes_ativas(self):
        return self.enquete_set.filter(ativa=True).count()

class Tecnologia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tecnologia"
        verbose_name_plural = "Tecnologias"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def total_perguntas(self):
        total = 0
        for enquete in self.enquete_set.all():
            total += enquete.perguntas.all.filter(tecnologia=self).count()
        return total

    @property
    def enquetes_relacionadas(self):
        return [enquete.titulo for enquete in self.enquete_set.all()]

class Enquete(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tecnologias = models.ManyToManyField(Tecnologia, blank=True)

    class Meta:
        verbose_name = "Enquete"
        verbose_name_plural = "Enquetes"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

    @property
    def total_perguntas(self):
        return self.perguntas.count()

    @property
    def perguntas_ativas(self):
        return self.perguntas.filter(ativa=True).count()

class Pergunta(models.Model):
    UNICA_ESCOLHA = 'UNICA_ESCOLHA'
    MULTIPLA_ESCOLHA = 'MULTIPLA_ESCOLHA'
    
    TIPO_CHOICES = [
        (UNICA_ESCOLHA, 'Única Escolha'),
        (MULTIPLA_ESCOLHA, 'Múltipla Escolha'),
    ]
    
    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='perguntas')
    tecnologia = models.ForeignKey(Tecnologia, on_delete=models.SET_NULL, null=True, blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pergunta"
        verbose_name_plural = "Perguntas"
        ordering = ['id']

    def __str__(self):
        return self.texto[:50]

    @property
    def total_opcoes(self):
        return self.opcao_set.count()

    @property
    def opcoes_ativas(self):
        return self.opcao_set.filter(ativa=True).count()

class Opcao(models.Model):
    texto = models.CharField(max_length=255)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    peso = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Opção"
        verbose_name_plural = "Opções"
        ordering = ['ordem']

    def __str__(self):
        return self.texto

    @property
    def total_respostas(self):
        return self.resposta_set.count()

    @property
    def percentual_respostas(self):
        total_respostas_pergunta = self.pergunta.resposta_set.count()
        if total_respostas_pergunta > 0:
            return (self.resposta_set.count() / total_respostas_pergunta) * 100
        return 0

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aluno', null=True)  # Adicione este campo
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    nivel = models.CharField(max_length=50, choices=[('iniciante', 'Iniciante'), ('intermediario', 'Intermediário'), ('avancado', 'Avançado')])
    tecnologias_interesse = models.ManyToManyField(Tecnologia, blank=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def total_respostas(self):
        return self.resposta_set.count()

    @property
    def enquetes_participadas(self):
        return len(set(resposta.pergunta.enquete for resposta in self.resposta_set.all()))

class Resposta(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resposta"
        verbose_name_plural = "Respostas"
        # unique_together = ('aluno', 'pergunta')
        ordering = ['-data_resposta']

    def __str__(self):
        aluno_nome = self.aluno.nome if self.aluno else "Anônimo"
        return f"Resposta de {aluno_nome} para {self.pergunta.texto[:30]}"

    @property
    def texto_opcao(self):
        return self.opcao.texto

    @property
    def texto_pergunta(self):
        return self.pergunta.texto

class MultiplaEscolhaResposta(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    opcoes = models.ManyToManyField(Opcao)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resposta Múltipla Escolha"
        verbose_name_plural = "Respostas Múltiplas Escolhas"
        # unique_together = ('aluno', 'pergunta')
        ordering = ['-data_resposta']

    def __str__(self):
        aluno_nome = self.aluno.nome if self.aluno else "Anônimo"
        return f"Respostas de {aluno_nome} para {self.pergunta.texto[:30]}"