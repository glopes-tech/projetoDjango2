from django.contrib import admin
from .models import Area, Enquete, Pergunta, Opcao, Aluno, Resposta, MultiplaEscolhaResposta

class OpcaoInline(admin.TabularInline):  
    model = Opcao
    extra = 3  

class PerguntaAdmin(admin.ModelAdmin):
    inlines = [OpcaoInline]
    list_display = ('texto', 'tipo', 'enquete', 'ativa')
    list_filter = ('enquete', 'tipo', 'ativa')
    search_fields = ('texto',)

class EnqueteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'area', 'data_criacao', 'ativa')
    list_filter = ('area', 'ativa')
    search_fields = ('titulo', 'descricao')
    date_hierarchy = 'data_criacao'
    filter_horizontal = ('tecnologias',)  

class AreaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}  # Preenche o slug automaticamente

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_inscricao', 'nivel')
    list_filter = ('nivel',)
    search_fields = ('nome', 'email')
    filter_horizontal = ('tecnologias_interesse',)

class RespostaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'pergunta', 'opcao', 'data_resposta')
    list_filter = ('pergunta', 'aluno')
    date_hierarchy = 'data_resposta'

class MultiplaEscolhaRespostaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'pergunta', 'data_resposta')
    list_filter = ('pergunta', 'aluno')
    date_hierarchy = 'data_resposta'
    filter_horizontal = ('opcoes',)


admin.site.register(Area, AreaAdmin)
admin.site.register(Enquete, EnqueteAdmin)
admin.site.register(Pergunta, PerguntaAdmin)
admin.site.register(Opcao)  # Registro básico, sem personalização
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Resposta, RespostaAdmin)
admin.site.register(MultiplaEscolhaResposta, MultiplaEscolhaRespostaAdmin)