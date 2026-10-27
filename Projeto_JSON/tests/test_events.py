from pathlib import Path
import pytest
from event_normalizer import motivo_recusa, normalizar


def test_evento_sem_id_e_recusado():
    evento = {
        "occurred_at": "...",
        "user_id": "...",
        "name": "...",
    }
    resultado = motivo_recusa(evento)
    assert resultado == "evento sem id"


def test_array_e_jsonl_geram_a_mesma_saida(tmp_path):
    saida_array = tmp_path / "array.jsonl"
    saida_jsonl = tmp_path / "linhas.jsonl"
    normalizar("data/eventos.json", saida_array, tmp_path / "resumo_array.json")
    normalizar("data/eventos.jsonl", saida_jsonl, tmp_path / "resumo_json.jsonl")
    assert saida_array.read_text(encoding="utf-8") == saida_jsonl.read_text(encoding="utf-8")


def test_arquivo_vazio_e_rejeitado(tmp_path):
    entrada = tmp_path / "vazio.json"
    entrada.write_text("   \n", encoding="utf-8")
    with pytest.raises(ValueError):
        normalizar(entrada, tmp_path / "saida.jsonl", tmp_path / "resumo.json")