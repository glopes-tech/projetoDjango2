import os
import sys
from pathlib import Path

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_enquete.settings')
import django
django.setup()

from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enquete.models import Enquete, Pergunta, Opcao, Resposta, MultiplaEscolhaResposta, Aluno
from django.db import transaction
from asgiref.sync import sync_to_async

# Pydantic Schemas (Keep these as they are good for data validation and serialization)
class OpcaoBase(BaseModel):
    id: int
    texto: str
    ativa: bool
    ordem: int
    peso: int

    class Config:
        orm_mode = True
        from_attributes = True # ADD THIS LINE

class PerguntaBase(BaseModel):
    id: int
    texto: str
    tipo: str
    ativa: bool
    tecnologia_id: Optional[int] = None
    opcoes: List[OpcaoBase] = []

    class Config:
        orm_mode = True
        from_attributes = True # ADD THIS LINE

class EnqueteBase(BaseModel):
    id: int
    titulo: str
    descricao: str
    ativa: bool
    area_id: Optional[int] = None
    perguntas: List[PerguntaBase] = []

    class Config:
        orm_mode = True
        from_attributes = True # ADD THIS LINE

class RespostaItem(BaseModel):
    pergunta_id: int
    opcoes_ids: Union[List[int], int]

class RespostaEnquetePayload(BaseModel):
    respostas: List[RespostaItem]

app = FastAPI(
    title="Enquete FastAPI Microservice",
    description="API para gerenciar e responder enquetes, integrada com modelos Django.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API de Enquetes do FastAPI!"}

# Helper function to encapsulate synchronous Django ORM operations
# This function will be called by sync_to_async
def _get_enquetes_data_sync():
    enquetes_qs = Enquete.objects.filter(ativa=True).prefetch_related('pergunta_set__opcao_set', 'tecnologias', 'area')

    enquetes_data = []
    for enquete in enquetes_qs:
        perguntas_data = []
        for pergunta in enquete.pergunta_set.filter(ativa=True).order_by('id'):
            opcoes_data = [
                OpcaoBase.from_orm(opcao) # This is where the error originates from (for OpcaoBase)
                for opcao in pergunta.opcao_set.filter(ativa=True).order_by('ordem')
            ]
            perguntas_data.append(
                PerguntaBase( # This is where the error would also occur for PerguntaBase if not fixed
                    id=pergunta.id,
                    texto=pergunta.texto,
                    tipo=pergunta.tipo,
                    ativa=pergunta.ativa,
                    tecnologia_id=pergunta.tecnologia_id,
                    opcoes=opcoes_data
                )
            )
        enquetes_data.append(
            EnqueteBase( # This is where the error would also occur for EnqueteBase if not fixed
                id=enquete.id,
                titulo=enquete.titulo,
                descricao=enquete.descricao,
                ativa=enquete.ativa,
                area_id=enquete.area_id,
                perguntas=perguntas_data
            )
        )
    return enquetes_data

# The main FastAPI endpoint
@app.get("/enquetes/", response_model=List[EnqueteBase], tags=["Enquetes"])
async def get_enquetes():
    # Call the synchronous helper function using sync_to_async
    enquetes_data = await sync_to_async(_get_enquetes_data_sync)()
    return enquetes_data

# Helper function to encapsulate synchronous Django ORM operations for responding to an enquete
def _responder_enquete_sync(enquete_id: int, payload: RespostaEnquetePayload):
    try:
        enquete = Enquete.objects.get(id=enquete_id, ativa=True)
    except Enquete.DoesNotExist:
        # Re-raise as an exception that FastAPI can catch and convert to HTTPException
        raise ValueError("Enquete não encontrada ou inativa.")

    try:
        aluno_fastapi, created = Aluno.objects.get_or_create(user__username='fastapi_responder', defaults={'nome': 'FastAPI User'})
        if created:
            print("Aluno 'fastapi_responder' criado.")
    except Exception as e:
        print(f"Erro ao obter/criar Aluno para FastAPI: {e}")
        aluno_fastapi = None # Handle this case if aluno creation is critical

    with transaction.atomic(): # transaction.atomic() can be used inside a sync function called by sync_to_async
        for resposta_item in payload.respostas:
            pergunta_id = resposta_item.pergunta_id
            opcoes_selecionadas_ids = resposta_item.opcoes_ids

            try:
                pergunta = Pergunta.objects.get(id=pergunta_id, enquete=enquete, ativa=True)
            except Pergunta.DoesNotExist:
                raise ValueError(f"Pergunta {pergunta_id} não encontrada ou inativa na enquete.")

            if pergunta.tipo == Pergunta.UNICA_ESCOLHA:
                if not isinstance(opcoes_selecionadas_ids, int):
                    raise ValueError(f"Resposta inválida para pergunta de única escolha ({pergunta.id}): 'opcoes_ids' deve ser um inteiro.")
                try:
                    opcao = Opcao.objects.get(id=opcoes_selecionadas_ids, pergunta=pergunta, ativa=True)
                except Opcao.DoesNotExist:
                    raise ValueError(f"Opção {opcoes_selecionadas_ids} inválida ou inativa para a pergunta {pergunta.id}.")

                Resposta.objects.create(aluno=aluno_fastapi, pergunta=pergunta, opcao=opcao)

            elif pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
                if not isinstance(opcoes_selecionadas_ids, list) or not all(isinstance(i, int) for i in opcoes_selecionadas_ids):
                    raise ValueError(f"Resposta inválida para pergunta de múltipla escolha ({pergunta.id}): 'opcoes_ids' deve ser uma lista de inteiros.")

                opcoes = Opcao.objects.filter(id__in=opcoes_selecionadas_ids, pergunta=pergunta, ativa=True)
                if len(opcoes) != len(opcoes_selecionadas_ids):
                    raise ValueError(f"Uma ou mais opções selecionadas para a pergunta {pergunta.id} são inválidas ou inativas.")

                multipla_resposta = MultiplaEscolhaResposta.objects.create(aluno=aluno_fastapi, pergunta=pergunta)
                multipla_resposta.opcoes.set(opcoes)
            else:
                raise ValueError(f"Tipo de pergunta desconhecido: {pergunta.tipo}")
    return {"message": "Respostas salvas com sucesso no FastAPI!"}

@app.post("/enquetes/{enquete_id}/responder/", status_code=status.HTTP_201_CREATED, tags=["Enquetes"])
async def responder_enquete_fastapi(enquete_id: int, payload: RespostaEnquetePayload):
    try:
        # Call the synchronous helper function using sync_to_async
        result = await sync_to_async(
            _responder_enquete_sync, thread_sensitive=True
        )(enquete_id, payload)
        return result
    except ValueError as e:
        # Catch ValueErrors raised by the sync function and convert them to HTTPExceptions
        if "Enquete não encontrada" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Catch any other unexpected exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")