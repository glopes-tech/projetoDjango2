from rest_framework import serializers
from enquete.models import Area, Tecnologia, Enquete, Pergunta, Opcao, Aluno, Resposta, MultiplaEscolhaResposta
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AlunoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 

    class Meta:
        model = Aluno
        fields = ['id', 'user', 'nome', 'data_nascimento', 'cpf', 'telefone']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'nome', 'descricao', 'slug', 'total_enquetes', 'enquetes_ativas']

class TecnologiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnologia
        fields = ['id', 'nome', 'descricao', 'total_perguntas']

class OpcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcao
        fields = ['id', 'texto', 'ativa', 'ordem', 'peso', 'pergunta']
        read_only_fields = ['pergunta'] 

class PerguntaSerializer(serializers.ModelSerializer):
    opcoes = OpcaoSerializer(many=True, read_only=True, source='opcao_set') 

    class Meta:
        model = Pergunta
        fields = ['id', 'texto', 'tipo', 'ativa', 'tecnologia', 'enquete', 'opcoes', 'total_opcoes', 'opcoes_ativas']
        read_only_fields = ['enquete'] 

class EnqueteSerializer(serializers.ModelSerializer):
    perguntas = PerguntaSerializer(many=True, read_only=True, source='perguntas.all') 
    area = AreaSerializer(read_only=True)
    tecnologias = TecnologiaSerializer(many=True, read_only=True)

    class Meta:
        model = Enquete
        fields = ['id', 'titulo', 'descricao', 'ativa', 'data_criacao', 'data_expiracao', 'area', 'tecnologias', 'total_perguntas', 'perguntas_ativas', 'perguntas']

class RespostaSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer(read_only=True)
    pergunta = PerguntaSerializer(read_only=True)
    opcao = OpcaoSerializer(read_only=True)

    class Meta:
        model = Resposta
        fields = ['id', 'aluno', 'pergunta', 'opcao', 'data_resposta', 'texto_opcao', 'texto_pergunta']
        read_only_fields = ['pergunta', 'opcao', 'aluno'] 

class MultiplaEscolhaRespostaSerializer(serializers.ModelSerializer):
    aluno = AlunoSerializer(read_only=True)
    pergunta = PerguntaSerializer(read_only=True)
    opcoes = OpcaoSerializer(many=True, read_only=True)

    class Meta:
        model = MultiplaEscolhaResposta
        fields = ['id', 'aluno', 'pergunta', 'opcoes', 'data_resposta']
        read_only_fields = ['pergunta', 'opcoes', 'aluno'] 