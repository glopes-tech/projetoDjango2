from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.forms import formset_factory
from .models import Enquete, Pergunta, Opcao, Area, Resposta, MultiplaEscolhaResposta, Aluno # Importe Aluno
from .forms import EnqueteForm, OpcaoForm, PerguntaForm, OpcaoFormSet, AreaForm, RespostaForm, MultiplaEscolhaRespostaForm
from django.contrib import messages
from django.db import IntegrityError
#from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'enquete/home.html')

class AreaListView(generic.ListView):
    model = Area
    template_name = 'enquete/area_list.html'
    context_object_name = 'areas'

class AreaCreateView(generic.CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'enquete/area_form.html'
    success_url = reverse_lazy('enquete:area_list')

class AreaUpdateView(generic.UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'enquete/area_form.html'
    success_url = reverse_lazy('enquete:area_list')

class AreaDetailView(generic.DetailView):
    model = Area
    template_name = 'enquete/area_detail.html'
    context_object_name = 'area'

class AreaDeleteView(generic.DeleteView):
    model = Area
    template_name = 'enquete/confirm_delete.html'
    success_url = reverse_lazy('enquete:area_list')

# Views baseadas em Funções com Métodos

def enquete_list(request):
    enquetes = Enquete.objects.all()
    return render(request, 'enquete/enquete_list.html', {'enquetes': enquetes})

def enquete_detail(request, pk):
    enquete = get_object_or_404(Enquete, pk=pk)
    perguntas = enquete.pergunta_set.filter(ativa=True).order_by('id')
    return render(request, 'enquete/enquete_detail.html', {'enquete': enquete, 'perguntas': perguntas})

def enquete_create(request):
    if request.method == 'POST':
        form = EnqueteForm(request.POST)
        if form.is_valid():
            enquete = form.save()
            messages.success(request, f"Enquete '{enquete.titulo}' criada com sucesso!")
            return redirect('enquete:enquete_detail', pk=enquete.id)
    else:
        form = EnqueteForm()
    return render(request, 'enquete/enquete_form.html', {'form': form})

def enquete_edit(request, pk):
    enquete = get_object_or_404(Enquete, pk=pk)
    if request.method == 'POST':
        form = EnqueteForm(request.POST, instance=enquete)
        if form.is_valid():
            enquete = form.save()
            messages.success(request, f"Enquete '{enquete.titulo}' atualizada com sucesso!")
            return redirect('enquete:enquete_detail', pk=enquete.id)
    else:
        form = EnqueteForm(instance=enquete)
    return render(request, 'enquete/enquete_form.html', {'form': form})

def enquete_delete(request, pk):
    enquete = get_object_or_404(Enquete, pk=pk)
    if request.method == 'POST':
        enquete.delete()
        messages.success(request, f"Enquete '{enquete.titulo}' deletada com sucesso!")
        return redirect('enquete:enquete_list')
    return render(request, 'enquete/confirm_delete.html', {'object': enquete})

# Views para Pergunta (Funções)
def pergunta_list(request, enquete_id):
    enquete = get_object_or_404(Enquete, pk=enquete_id)
    perguntas = enquete.pergunta_set.all()
    return render(request, 'enquete/pergunta_list.html', {'enquete': enquete, 'perguntas': perguntas})

def pergunta_detail(request, pk):
    pergunta = get_object_or_404(Pergunta, pk=pk)
    return render(request, 'enquete/pergunta_detail.html', {'pergunta': pergunta})

def pergunta_create(request, enquete_id):
    enquete = get_object_or_404(Enquete, pk=enquete_id)
    if request.method == 'POST':
        form = PerguntaForm(request.POST, initial={'enquete': enquete})
        if form.is_valid():
            pergunta = form.save(commit=False)
            pergunta.enquete = enquete
            pergunta.save()
            messages.success(request, f"Pergunta '{pergunta.texto}' criada com sucesso!")
            return redirect('enquete:pergunta_detail', pk=pergunta.id)
    else:
        form = PerguntaForm(initial={'enquete': enquete})
    return render(request, 'enquete/pergunta_form.html', {'form': form, 'enquete': enquete})

def pergunta_edit(request, pk):
    pergunta = get_object_or_404(Pergunta, pk=pk)
    if request.method == 'POST':
        form = PerguntaForm(request.POST, instance=pergunta)
        if form.is_valid():
            form.save()
            messages.success(request, f"Pergunta '{pergunta.texto}' atualizada com sucesso!")
            return redirect('enquete:pergunta_detail', pk=pergunta.id)
    else:
        form = PerguntaForm(instance=pergunta)
    return render(request, 'enquete/pergunta_form.html', {'form': form, 'pergunta': pergunta})

def pergunta_delete(request, pk):
    pergunta = get_object_or_404(Pergunta, pk=pk)
    enquete_id = pergunta.enquete.id
    if request.method == 'POST':
        pergunta.delete()
        messages.success(request, f"Pergunta '{pergunta.texto}' deletada com sucesso!")
        return redirect('enquete:enquete_detail', pk=enquete_id)
    return render(request, 'enquete/confirm_delete.html', {'object': pergunta})

# Views para Opcao (Funções)
def opcao_create(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    if request.method == 'POST':
        form = OpcaoForm(request.POST) # Não passe initial aqui, o save(commit=False) é o correto
        if form.is_valid():
            try:
                opcao = form.save(commit=False)
                opcao.pergunta = pergunta # Associe a pergunta antes de salvar
                opcao.save()
                messages.success(request, f"Opção '{opcao.texto}' criada com sucesso!")
                return redirect('enquete:pergunta_detail', pk=pergunta.id)
            except IntegrityError:
                messages.error(request, "Erro de integridade: a opção pode já existir ou há um problema com os dados.")
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao criar a opção: {e}")
    else:
        form = OpcaoForm() # Não passe initial aqui, o formulário é para criar uma nova opção
    return render(request, 'enquete/opcao_form.html', {'form': form, 'pergunta': pergunta})

def opcao_edit(request, pk):
    opcao = get_object_or_404(Opcao, pk=pk)
    if request.method == 'POST':
        form = OpcaoForm(request.POST, instance=opcao)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Opção '{opcao.texto}' atualizada com sucesso!")
                return redirect('enquete:pergunta_detail', pk=opcao.pergunta.id)
            except IntegrityError:
                messages.error(request, "Erro de integridade: a opção pode já existir ou há um problema com os dados.")
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao atualizar a opção: {e}")
    else:
        form = OpcaoForm(instance=opcao)
    return render(request, 'enquete/opcao_form.html', {'form': form, 'opcao': opcao})

def opcao_delete(request, pk):
    opcao = get_object_or_404(Opcao, pk=pk)
    pergunta_id = opcao.pergunta.id
    if request.method == 'POST':
        opcao.delete()
        messages.success(request, f"Opção '{opcao.texto}' deletada com sucesso!")
        return redirect('enquete:pergunta_detail', pk=pergunta_id)
    return render(request, 'enquete/confirm_delete.html', {'object': opcao})

def responder_enquete(request, enquete_id):
    enquete = get_object_or_404(Enquete, pk=enquete_id)
    perguntas = enquete.pergunta_set.filter(ativa=True).order_by('id')

    perguntas_forms = []
    for pergunta in perguntas:
        form = None # Inicializa form para garantir que sempre tenha um valor
        if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
            if request.method == 'POST':
                form = RespostaForm(request.POST, pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
            else: # GET request
                form = RespostaForm(pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
        elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
            if request.method == 'POST':
                form = MultiplaEscolhaRespostaForm(request.POST, pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
            else: # GET request
                form = MultiplaEscolhaRespostaForm(pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
        else:
            # Lidar com tipos de pergunta desconhecidos ou inativos se necessário
            # Por exemplo, você pode pular esta pergunta ou adicionar uma mensagem de erro
            messages.warning(request, f"Tipo de pergunta desconhecido ou inativo para: {pergunta.texto}")
            continue # Pula para a próxima pergunta

        if form: # Adiciona apenas se um formulário válido foi criado
            perguntas_forms.append({'pergunta': pergunta, 'form': form})

    context = {
        'enquete': enquete,
        'perguntas_forms': perguntas_forms,
        'Pergunta': Pergunta, # Adiciona a classe Pergunta ao contexto para acesso às constantes
    }
    return render(request, 'enquete/responder_enquete.html', context)


def processar_respostas(request, enquete_id):
    if request.method == 'POST':
        enquete = get_object_or_404(Enquete, pk=enquete_id)
        perguntas = enquete.pergunta_set.filter(ativa=True).order_by('id')
        
        aluno = None
        if request.user.is_authenticated:
            try:
                aluno = request.user.aluno
            except Aluno.DoesNotExist:
                # Criar um perfil de aluno se o usuário estiver logado mas não tiver um
                messages.info(request, "Seu perfil de aluno não foi encontrado. Criando um para você.")
                aluno = Aluno.objects.create(user=request.user, nome=request.user.username)
            except Exception as e:
                messages.error(request, f"Erro ao tentar obter ou criar perfil de aluno: {e}. As respostas serão salvas sem vinculação a um aluno específico.")
                aluno = None # Garante que aluno seja None em caso de outros erros
        
        respostas_validas = True
        
        for pergunta in perguntas:
            form = None # Inicializa form aqui também
            if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
                form = RespostaForm(request.POST, pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
                if form.is_valid():
                    opcao_selecionada = form.cleaned_data['opcao']
                    Resposta.objects.create(
                        aluno=aluno,
                        pergunta=pergunta,
                        opcao=opcao_selecionada
                    )
                else:
                    respostas_validas = False
                    messages.error(request, f"Erro na pergunta '{pergunta.texto}': {form.errors.as_text()}") # Use .as_text() para melhor formatação
            elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
                form = MultiplaEscolhaRespostaForm(request.POST, pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
                if form.is_valid():
                    opcoes_selecionadas = form.cleaned_data['opcoes']
                    multipla_resposta = MultiplaEscolhaResposta.objects.create(
                        aluno=aluno,
                        pergunta=pergunta
                    )
                    multipla_resposta.opcoes.set(opcoes_selecionadas)
                else:
                    respostas_validas = False
                    messages.error(request, f"Erro na pergunta '{pergunta.texto}': {form.errors.as_text()}") # Use .as_text() para melhor formatação
            else:
                messages.warning(request, f"Tipo de pergunta desconhecido ou inativo para: {pergunta.texto}. Nenhuma resposta foi processada para esta pergunta.")
                # Não altera respostas_validas pois a pergunta foi intencionalmente pulada
        
        if respostas_validas:
            messages.success(request, "Suas respostas foram salvas com sucesso!")
            return redirect('enquete:enquete_list') 
        else:
            messages.error(request, "Houve erros ao salvar suas respostas. Por favor, verifique.")
            # Para re-renderizar a página com os erros, chame responder_enquete com o request POST
            # Isso permitirá que os formulários sejam pré-preenchidos e mostrem os erros
            return responder_enquete(request, enquete_id) # ESSENCIAL: re-chamar com request

    return HttpResponseBadRequest("Método não permitido.")