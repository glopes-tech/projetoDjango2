from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.forms import formset_factory
from .models import Enquete, Pergunta, Opcao, Area, Resposta, MultiplaEscolhaResposta, Aluno
from .forms import EnqueteForm, OpcaoForm, PerguntaForm, AreaForm, RespostaForm
from django.contrib import messages
from django.db import IntegrityError, transaction
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
    perguntas = enquete.perguntas.filter(ativa=True).order_by('id')
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
    perguntas = enquete.perguntas.all()
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


def opcao_create(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    if request.method == 'POST':
        form = OpcaoForm(request.POST) 
        if form.is_valid():
            try:
                opcao = form.save(commit=False)
                opcao.pergunta = pergunta 
                opcao.save()
                messages.success(request, f"Opção '{opcao.texto}' criada com sucesso!")
                return redirect('enquete:pergunta_detail', pk=pergunta.id)
            except IntegrityError:
                messages.error(request, "Erro de integridade: a opção pode já existir ou há um problema com os dados.")
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao criar a opção: {e}")
    else:
        form = OpcaoForm() 
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
    perguntas = enquete.perguntas.filter(ativa=True).order_by('id') 

    forms_for_template = []
    
    if request.method == 'POST':
        all_forms_valid = True 

        for pergunta in perguntas:
            form = RespostaForm(request.POST, pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
            forms_for_template.append({'pergunta': pergunta, 'form': form})

            if not form.is_valid():
                all_forms_valid = False

        if all_forms_valid:
            try:
                with transaction.atomic():
                    aluno = None 
                    if request.user.is_authenticated:
                        try:
                            aluno = request.user.aluno 
                        except Aluno.DoesNotExist:
                            messages.info(request, "Criando novo perfil de aluno para seu usuário.")
                            aluno = Aluno.objects.create(user=request.user, nome=request.user.username)
                        except Exception as e:
                            messages.error(request, f"Erro ao tentar obter ou criar perfil de aluno: {e}. As respostas serão salvas sem vinculação a um aluno específico.")
                            aluno = None 

                    for item in forms_for_template:
                        pergunta_atual = item['pergunta']
                        form_atual = item['form']
                        
                        campo_dinamico_nome = f'pergunta_{pergunta_atual.id}'

                        if pergunta_atual.tipo == Pergunta.UNICA_ESCOLHA:
                            opcao_selecionada = form_atual.cleaned_data.get(campo_dinamico_nome)
                            if opcao_selecionada: 
                                Resposta.objects.create(
                                    pergunta=pergunta_atual,
                                    opcao=opcao_selecionada,
                                    aluno=aluno 
                                )

                        elif pergunta_atual.tipo == Pergunta.MULTIPLA_ESCOLHA:
                            opcoes_selecionadas = form_atual.cleaned_data.get(campo_dinamico_nome)
                            if opcoes_selecionadas: 
                                multipla_resposta = MultiplaEscolhaResposta.objects.create(
                                    pergunta=pergunta_atual,
                                    aluno=aluno 
                                )
                                multipla_resposta.opcoes.set(opcoes_selecionadas) 

                        else:
                            messages.warning(request, f"Tipo de pergunta '{pergunta_atual.tipo}' desconhecido para: {pergunta_atual.texto}. Nenhuma resposta foi processada para esta pergunta.")
                
                messages.success(request, "Enquete respondida com sucesso! Obrigado pela sua participação.")
                return redirect(reverse('enquete:processar_resposta', args=[enquete_id]))

            except IntegrityError as e:
                messages.error(request, f"Erro de integridade ao salvar respostas: {e}. Pode haver uma resposta duplicada ou problema de relacionamento. Por favor, tente novamente.")
                all_forms_valid = False
            except Exception as e:
                messages.error(request, f"Ocorreu um erro inesperado ao salvar as respostas: {e}. Por favor, entre em contato com o suporte.")
                all_forms_valid = False 

        if not all_forms_valid:
            messages.error(request, "Houve erros ao salvar suas respostas. Por favor, verifique os campos destacados e tente novamente.")

    else: 
        for pergunta in perguntas:
            form = RespostaForm(pergunta=pergunta, prefix=f'pergunta_{pergunta.id}')
            forms_for_template.append({'pergunta': pergunta, 'form': form})

    context = {
        'enquete': enquete,
        'perguntas_forms': forms_for_template, 
    }
    return render(request, 'enquete/responder_enquete.html', context)


def processar_resposta(request, enquete_id):
    enquete = get_object_or_404(Enquete, pk=enquete_id)
    context = {
        'enquete': enquete,
    }
    return render(request, 'enquete/processar_resposta.html', context)