"""Testes de fumaça: validam fiação e contratos sem chamar LLM/banco real."""
from app.domain.models import ContextoUsuario, Papel
from app.infrastructure.database.null_repository import NullPurchasingRepository


def test_acesso_total_por_papel():
    assert ContextoUsuario(funcao="COMPRAS").pode_ver_sigiloso is True
    assert ContextoUsuario(funcao="RECEBIMENTO").pode_ver_sigiloso is False


def test_null_repository_nao_quebra():
    repo = NullPurchasingRepository()
    assert "erro" in repo.resumo_pedidos()
    assert repo.pedidos_por_status("PENDENTE") == []


def test_papeis_enum():
    assert Papel.COMPRAS.value == "COMPRAS"
