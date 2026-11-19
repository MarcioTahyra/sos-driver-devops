
import pytest
from fastapi.testclient import TestClient

from app.main import app, solicitacoes

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpar_solicitacoes():
    solicitacoes.clear()
    yield
    solicitacoes.clear()


def test_pagina_inicial():
    response = client.get("/")

    assert response.status_code == 200

    dados = response.json()

    assert dados["aplicacao"] == "SOS Driver"
    assert dados["status"] == "online"
    assert dados["documentacao"] == "/docs"


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_listar_servicos():
    response = client.get("/servicos")

    assert response.status_code == 200

    servicos = response.json()["servicos"]

    assert len(servicos) == 4
    assert "reboque" in servicos
    assert "pneu" in servicos
    assert "bateria" in servicos
    assert "pane_seca" in servicos

    assert servicos["reboque"]["preco_base"] == 150.0


@pytest.mark.parametrize(
    "tipo_servico,preco",
    [
        ("reboque", 150.0),
        ("pneu", 80.0),
        ("bateria", 70.0),
        ("pane_seca", 60.0),
    ],
)
def test_criar_solicitacao_valida(tipo_servico, preco):
    response = client.post(
        "/solicitacoes",
        json={
            "tipo_servico": tipo_servico,
            "latitude": -23.5505,
            "longitude": -46.6333,
        },
    )

    assert response.status_code == 201

    dados = response.json()

    assert dados["id"]
    assert dados["tipo_servico"] == tipo_servico
    assert dados["preco_estimado"] == preco
    assert dados["moeda"] == "BRL"
    assert dados["status"] == "aguardando_prestador"
    assert dados["criado_em"]


def test_consultar_solicitacao_existente():
    criacao = client.post(
        "/solicitacoes",
        json={
            "tipo_servico": "reboque",
            "latitude": -23.5505,
            "longitude": -46.6333,
        },
    )

    assert criacao.status_code == 201

    identificador = criacao.json()["id"]

    response = client.get(f"/solicitacoes/{identificador}")

    assert response.status_code == 200
    assert response.json()["id"] == identificador
    assert response.json()["tipo_servico"] == "reboque"


def test_consultar_solicitacao_inexistente():
    response = client.get("/solicitacoes/id-inexistente")

    assert response.status_code == 404
    assert response.json()["detail"] == "Solicitacao nao encontrada"


def test_criar_solicitacao_com_servico_invalido():
    response = client.post(
        "/solicitacoes",
        json={
            "tipo_servico": "servico_inexistente",
            "latitude": -23.5505,
            "longitude": -46.6333,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Tipo de servico invalido"


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (-91, -46.6333),
        (91, -46.6333),
        (-23.5505, -181),
        (-23.5505, 181),
    ],
)
def test_coordenadas_invalidas(latitude, longitude):
    response = client.post(
        "/solicitacoes",
        json={
            "tipo_servico": "reboque",
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    assert response.status_code == 422


def test_campos_obrigatorios():
    response = client.post(
        "/solicitacoes",
        json={"tipo_servico": "reboque"},
    )

    assert response.status_code == 422


def test_documentacao_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/health" in response.json()["paths"]
    assert "/solicitacoes" in response.json()["paths"]


def test_metricas_prometheus():
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "sos_http_requests_total" in response.text
    assert "sos_http_request_duration_seconds" in response.text
    assert "python_info" in response.text
