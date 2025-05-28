import os
import sys
from pathlib import Path
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_enquete.settings')
import django
django.setup()

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
from enquete.models import Enquete, Pergunta, Opcao, Resposta, MultiplaEscolhaResposta, Aluno, Area # Import Area
from django.db import transaction
from asgiref.sync import sync_to_async

# Pydantic Data Models
class OpcaoBase(BaseModel):
    id: int
    texto: str
    ativa: bool
    ordem: int
    peso: int

class PerguntaBase(BaseModel):
    id: int
    texto: str
    tipo: str
    ativa: bool
    tecnologia_id: Optional[int] = None
    opcoes: List[OpcaoBase] = []

class EnqueteBase(BaseModel):
    id: int
    titulo: str
    descricao: str
    ativa: bool
    area_id: Optional[int] = None
    perguntas: List[PerguntaBase] = []

class RespostaItem(BaseModel):
    pergunta_id: int
    opcoes_ids: List[int] | int

class RespostaEnquetePayload(BaseModel):
    respostas: List[RespostaItem]

class NewArea(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)

class UpdateDescription(BaseModel):
    descricao: str = Field(..., min_length=10, max_length=500)

# Enum for Path Parameter
class TipoPergunta(str, Enum):
    unica_escolha = "unica_escolha"
    multipla_escolha = "multipla_escolha"
    texto = "texto"

app = FastAPI(
    title="API de Enquetes",
    description="API para gerenciar enquetes, perguntas e respostas.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API de Enquetes!"}

# 1 Endpoint com Path Parameter
@app.get("/enquetes/{enquete_id}", response_model=EnqueteBase)
async def get_enquete_by_id(enquete_id: int):
    """
    Retorna uma enquete específica pelo seu ID.
    """
    try:
        enquete = await sync_to_async(Enquete.objects.get)(id=enquete_id, ativa=True)
        
        perguntas_data = []
        perguntas_qs = await sync_to_async(enquete.perguntas.all.filter)(ativa=True)
        for pergunta in await sync_to_async(list)(perguntas_qs):
            opcoes_data = []
            opcoes_qs = await sync_to_async(pergunta.opcao_set.filter)(ativa=True)
            for opcao in await sync_to_async(list)(opcoes_qs.order_by('ordem')):
                opcoes_data.append(
                    OpcaoBase(
                        id=opcao.id,
                        texto=opcao.texto,
                        ativa=opcao.ativa,
                        ordem=opcao.ordem,
                        peso=opcao.peso
                    )
                )
            
            # Safely access tecnologia.id
            tecnologia_id = None
            if await sync_to_async(hasattr)(pergunta, 'tecnologia'):
                tecnologia = await sync_to_async(getattr)(pergunta, 'tecnologia', None)
                if tecnologia:
                    tecnologia_id = tecnologia.id

            perguntas_data.append(
                PerguntaBase(
                    id=pergunta.id,
                    texto=pergunta.texto,
                    tipo=pergunta.tipo,
                    ativa=pergunta.ativa,
                    tecnologia_id=tecnologia_id,
                    opcoes=opcoes_data
                )
            )
        
        # Safely access area.id
        area_id = None
        if await sync_to_async(hasattr)(enquete, 'area'):
            area = await sync_to_async(getattr)(enquete, 'area', None)
            if area:
                area_id = area.id

        return EnqueteBase(
            id=enquete.id,
            titulo=enquete.titulo,
            descricao=enquete.descricao,
            ativa=enquete.ativa,
            area_id=area_id,
            perguntas=perguntas_data
        )
    except Enquete.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquete não encontrada ou inativa.")

# 1 Endpoint com Path Parameter com Enum
@app.get("/perguntas/tipo/{tipo_pergunta}", response_model=List[PerguntaBase])
async def get_perguntas_by_type(tipo_pergunta: TipoPergunta):
    """
    Retorna perguntas filtradas por um tipo específico usando Enum.
    """
    perguntas_qs = await sync_to_async(Pergunta.objects.filter)(tipo=tipo_pergunta.value, ativa=True)
    perguntas_data = []
    for pergunta in await sync_to_async(list)(perguntas_qs):
        opcoes_data = []
        opcoes_qs = await sync_to_async(pergunta.opcao_set.filter)(ativa=True)
        for opcao in await sync_to_async(list)(opcoes_qs.order_by('ordem')):
            opcoes_data.append(
                OpcaoBase(
                    id=opcao.id,
                    texto=opcao.texto,
                    ativa=opcao.ativa,
                    ordem=opcao.ordem,
                    peso=opcao.peso
                )
            )
        
        # Safely access tecnologia.id
        tecnologia_id = None
        if await sync_to_async(hasattr)(pergunta, 'tecnologia'):
            tecnologia = await sync_to_async(getattr)(pergunta, 'tecnologia', None)
            if tecnologia:
                tecnologia_id = tecnologia.id

        perguntas_data.append(
            PerguntaBase(
                id=pergunta.id,
                texto=pergunta.texto,
                tipo=pergunta.tipo,
                ativa=pergunta.ativa,
                tecnologia_id=tecnologia_id,
                opcoes=opcoes_data
            )
        )
    return perguntas_data

# 1 Endpoint com Path Parameter com Path
@app.get("/arquivos/{file_path:path}")
async def get_file(file_path: str):
    """
    Retorna o caminho de um arquivo, demonstrando um Path Parameter com Path.
    """
    return {"file_path": file_path}

# 1 Endpoint com Path Parameters opcionais
@app.get("/usuarios/{user_id}/itens/{item_id}")
async def get_user_item(user_id: int, item_id: Optional[int] = None):
    """
    Retorna informações sobre um usuário e opcionalmente um item.
    """
    if item_id:
        return {"user_id": user_id, "item_id": item_id, "message": f"Retornando item {item_id} do usuário {user_id}"}
    return {"user_id": user_id, "message": f"Retornando todos os itens do usuário {user_id}"}

# 2 Endpoint com Múltiplos Query Parameters
@app.get("/enquetes/", response_model=dict) # Use dict for response_model as it's a custom structure
async def get_enquetes(skip: int = 0, limit: int = 10, search: Optional[str] = Query(None, min_length=3)):
    """
    Retorna uma lista de enquetes com paginação e busca.
    """
    enquetes_qs = await sync_to_async(Enquete.objects.filter)(ativa=True)
    if search:
        enquetes_qs = await sync_to_async(enquetes_qs.filter)(titulo__icontains=search)
    
    total_enquetes = await sync_to_async(enquetes_qs.count)()
    
    # Apply slicing within sync_to_async
    enquetes_list = await sync_to_async(lambda qs, s, l: list(qs[s : s + l]))(enquetes_qs, skip, limit)

    enquetes_data = []
    for enquete in enquetes_list:
        perguntas_data = []
        perguntas_qs = await sync_to_async(lambda: enquete.perguntas.filter(ativa=True))()
        for pergunta in await sync_to_async(list)(perguntas_qs):
            opcoes_data = []
            opcoes_qs = await sync_to_async(pergunta.opcao_set.filter)(ativa=True)
            for opcao in await sync_to_async(list)(opcoes_qs.order_by('ordem')):
                opcoes_data.append(
                    OpcaoBase(
                        id=opcao.id,
                        texto=opcao.texto,
                        ativa=opcao.ativa,
                        ordem=opcao.ordem,
                        peso=opcao.peso
                    )
                )
            
            # Safely access tecnologia.id
            tecnologia_id = None
            if await sync_to_async(hasattr)(pergunta, 'tecnologia'):
                tecnologia = await sync_to_async(getattr)(pergunta, 'tecnologia', None)
                if tecnologia:
                    tecnologia_id = tecnologia.id

            perguntas_data.append(
                PerguntaBase(
                    id=pergunta.id,
                    texto=pergunta.texto,
                    tipo=pergunta.tipo,
                    ativa=pergunta.ativa,
                    tecnologia_id=tecnologia_id,
                    opcoes=opcoes_data
                )
            )
        
        # Safely access area.id
        area_id = None
        if await sync_to_async(hasattr)(enquete, 'area'):
            area = await sync_to_async(getattr)(enquete, 'area', None)
            if area:
                area_id = area.id

        enquetes_data.append(
            EnqueteBase(
                id=enquete.id,
                titulo=enquete.titulo,
                descricao=enquete.descricao,
                ativa=enquete.ativa,
                area_id=area_id,
                perguntas=perguntas_data
            )
        )
    return {"total": total_enquetes, "skip": skip, "limit": limit, "data": enquetes_data}

# Outro Endpoint com Múltiplos Query Parameters
@app.get("/perguntas/", response_model=List[PerguntaBase])
async def get_perguntas(ativa: Optional[bool] = None, tecnologia_id: Optional[int] = None):
    """
    Retorna uma lista de perguntas, filtrando por status de ativação e/ou tecnologia.
    """
    perguntas_qs = await sync_to_async(Pergunta.objects.all)()

    if ativa is not None:
        perguntas_qs = await sync_to_async(perguntas_qs.filter)(ativa=ativa)
    
    if tecnologia_id is not None:
        perguntas_qs = await sync_to_async(perguntas_qs.filter)(tecnologia__id=tecnologia_id)
    
    perguntas_data = []
    for pergunta in await sync_to_async(list)(perguntas_qs):
        opcoes_data = []
        opcoes_qs = await sync_to_async(pergunta.opcao_set.all)()
        for opcao in await sync_to_async(list)(opcoes_qs.order_by('ordem')):
            opcoes_data.append(
                OpcaoBase(
                    id=opcao.id,
                    texto=opcao.texto,
                    ativa=opcao.ativa,
                    ordem=opcao.ordem,
                    peso=opcao.peso
                )
            )
        
        # Safely access tecnologia.id
        tecnologia_id_val = None
        if await sync_to_async(hasattr)(pergunta, 'tecnologia'):
            tecnologia = await sync_to_async(getattr)(pergunta, 'tecnologia', None)
            if tecnologia:
                tecnologia_id_val = tecnologia.id

        perguntas_data.append(
            PerguntaBase(
                id=pergunta.id,
                texto=pergunta.texto,
                tipo=pergunta.tipo,
                ativa=pergunta.ativa,
                tecnologia_id=tecnologia_id_val,
                opcoes=opcoes_data
            )
        )
    return perguntas_data

# 2 Endpoint que recebem Body e validam com os Data Models (Pydantic)
@app.post("/areas/")
async def create_area(area: NewArea):
    """
    Cria uma nova área de programação.
    """
    try:
        await sync_to_async(Area.objects.create)(nome=area.nome, descricao=area.descricao)
        return {"message": f"Área '{area.nome}' criada com sucesso!", "data": area.dict()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/enquetes/{enquete_id}/descricao")
async def update_enquete_description(enquete_id: int, update_data: UpdateDescription):
    """
    Atualiza a descrição de uma enquete existente.
    """
    try:
        enquete = await sync_to_async(Enquete.objects.get)(id=enquete_id)
        enquete.descricao = update_data.descricao
        await sync_to_async(enquete.save)() # Descomente para salvar no banco de dados
        return {"message": f"Descrição da enquete {enquete_id} atualizada com sucesso para '{update_data.descricao}'"}
    except Enquete.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquete não encontrada.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/enquetes/{enquete_id}/responder")
async def responder_enquete(enquete_id: int, payload: RespostaEnquetePayload):
    """
    Recebe as respostas de uma enquete e as processa.
    """
    try:
        enquete = await sync_to_async(Enquete.objects.get)(id=enquete_id)
    except Enquete.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquete não encontrada.")

    aluno_fastapi = await sync_to_async(Aluno.objects.first)()
    if not aluno_fastapi:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum aluno cadastrado para registrar respostas.")

    async def process_responses_sync():
        with transaction.atomic():
            for resposta_item in payload.respostas:
                pergunta_id = resposta_item.pergunta_id
                opcoes_selecionadas_ids = resposta_item.opcoes_ids

                try:
                    pergunta = await sync_to_async(Pergunta.objects.get)(id=pergunta_id, enquete=enquete)
                except Pergunta.DoesNotExist:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pergunta {pergunta_id} não encontrada para a enquete {enquete_id}.")

                if await sync_to_async(Resposta.objects.filter(aluno=aluno_fastapi, pergunta=pergunta).exists)() or \
                   await sync_to_async(MultiplaEscolhaResposta.objects.filter(aluno=aluno_fastapi, pergunta=pergunta).exists)():
                    if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
                        await sync_to_async(Resposta.objects.filter(aluno=aluno_fastapi, pergunta=pergunta).delete)()
                    elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
                        await sync_to_async(MultiplaEscolhaResposta.objects.filter(aluno=aluno_fastapi, pergunta=pergunta).delete)()

                if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
                    if not isinstance(opcoes_selecionadas_ids, int):
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Resposta inválida para pergunta de única escolha ({pergunta.id}): 'opcoes_ids' deve ser um inteiro.")
                    try:
                        opcao = await sync_to_async(Opcao.objects.get)(id=opcoes_selecionadas_ids, pergunta=pergunta, ativa=True)
                    except Opcao.DoesNotExist:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Opção {opcoes_selecionadas_ids} inválida ou inativa para a pergunta {pergunta.id}.")

                    await sync_to_async(Resposta.objects.create)(aluno=aluno_fastapi, pergunta=pergunta, opcao=opcao)

                elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
                    if not isinstance(opcoes_selecionadas_ids, list) or not all(isinstance(i, int) for i in opcoes_selecionadas_ids):
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Resposta inválida para pergunta de múltipla escolha ({pergunta.id}): 'opcoes_ids' deve ser uma lista de inteiros.")

                    opcoes = await sync_to_async(Opcao.objects.filter)(id__in=opcoes_selecionadas_ids, pergunta=pergunta, ativa=True)
                    if await sync_to_async(len)(opcoes) != len(opcoes_selecionadas_ids):
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Uma ou mais opções selecionadas para a pergunta {pergunta.id} são inválidas ou inativas.")

                    multipla_resposta = await sync_to_async(MultiplaEscolhaResposta.objects.create)(aluno=aluno_fastapi, pergunta=pergunta)
                    await sync_to_async(multipla_resposta.opcoes.set)(opcoes)
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tipo de pergunta desconhecido: {pergunta.tipo}")
    
    await process_responses_sync()

    return {"message": "Respostas da enquete registradas com sucesso!"}