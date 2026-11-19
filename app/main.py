
import time
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.responses import Response

app = FastAPI(
    title="SOS Driver - API de Assistencia Veicular",
    description="Marketplace de assistencia veicular sob demanda",
    version="1.0.0",
)

SERVICOS = {
    "reboque": {"nome": "Reboque", "preco_base": 150.0},
    "pneu": {"nome": "Troca de pneu", "preco_base": 80.0},
    "bateria": {"nome": "Auxilio de bateria", "preco_base": 70.0},
    "pane_seca": {"nome": "Pane seca", "preco_base": 60.0},
}

solicitacoes = {}
lock = Lock()

REQUISICOES = Counter(
    "sos_http_requests_total",
    "Total de requisicoes HTTP",
    ["method", "endpoint", "status"],
)

LATENCIA = Histogram(
    "sos_http_request_duration_seconds",
    "Duracao das requisicoes HTTP",
    ["endpoint"],
)

REQUISICOES_ATIVAS = Gauge(
    "sos_http_requests_in_progress",
    "Requisicoes HTTP em andamento",
)


class Solicitacao(BaseModel):
    tipo_servico: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


@app.middleware("http")
async def monitorar_requisicao(request: Request, call_next):
    inicio = time.perf_counter()
    endpoint = request.url.path
    status = 500

    REQUISICOES_ATIVAS.inc()

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duracao = time.perf_counter() - inicio

        if endpoint != "/metrics":
            REQUISICOES.labels(
                method=request.method,
                endpoint=endpoint,
                status=str(status),
            ).inc()

            LATENCIA.labels(endpoint=endpoint).observe(duracao)

        REQUISICOES_ATIVAS.dec()


@app.get("/")
def inicio():
    return {
        "aplicacao": "SOS Driver",
        "descricao": "Assistencia veicular sob demanda",
        "status": "online",
        "documentacao": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/servicos")
def listar_servicos():
    return {"servicos": SERVICOS}


@app.post("/solicitacoes", status_code=201)
def criar_solicitacao(dados: Solicitacao):
    servico = SERVICOS.get(dados.tipo_servico)

    if servico is None:
        raise HTTPException(
            status_code=400,
            detail="Tipo de servico invalido",
        )

    identificador = str(uuid4())

    solicitacao = {
        "id": identificador,
        "tipo_servico": dados.tipo_servico,
        "preco_estimado": servico["preco_base"],
        "moeda": "BRL",
        "status": "aguardando_prestador",
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }

    with lock:
        solicitacoes[identificador] = solicitacao

    return solicitacao


@app.get("/solicitacoes/{identificador}")
def consultar_solicitacao(identificador: str):
    with lock:
        solicitacao = solicitacoes.get(identificador)

    if solicitacao is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitacao nao encontrada",
        )

    return solicitacao


@app.get("/metrics")
def metricas():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
