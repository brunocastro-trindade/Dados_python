import os
import tempfile
import json
from pathlib import Path


CAMPOS_OBRIGATORIOS = ["event_id", "occurred_at", "user_id", "name"]


def detectar_formato(texto: str) -> str:
    limpar_texto = texto.lstrip()
    if limpar_texto == "":
        raise ValueError("Arquivo vazio")
    if limpar_texto[0] == "[":
        return "array"
    else:
        return "jsonl"


def ler_eventos(texto: str) -> list[dict]:
    novo_formato = detectar_formato(texto)
    if novo_formato == "array":
        return json.loads(texto)
    eventos = []
    for linha in texto.splitlines():
        if linha.strip() == "":
            continue
        eventos.append(json.loads(linha))
    return eventos


def motivo_recusa(evento: dict) -> str | None:
    var_evento = evento.get("event_id")
    if (var_evento is None) or (var_evento == ""):
        return "evento sem id"
    for campo in CAMPOS_OBRIGATORIOS:
        preenche = evento.get(campo)
        if (preenche is None) or (preenche == ""):
            return f"campo ausente: {campo}"
    return None


def separar_eventos(eventos: list[dict]) -> tuple[list[dict], list[str]]:
    aceitos = []
    recusados = []
    for evento in eventos:
        motivo = motivo_recusa(evento)
        if motivo is None:
            aceitos.append(evento)
        else:
            recusados.append(motivo)
    return aceitos, recusados


def montar_resumo(eventos, aceitos, recusados: str) -> list[dict]:
    motivos = {}
    for motivo in recusados:
        motivos[motivo] = motivos.get(motivo, 0) + 1
    return {
        "eventos_lidos": len(eventos),
        "eventos_aceitos": len(aceitos),
        "eventos_recusados": len(recusados),
        "motivos": motivos,
    }


def gravar_jsonl_atomico(eventos, destino: str) -> None:
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destino.parent, suffix=".tmp", delete=False) as rascunho:
        for evento in eventos:
            rascunho.write(json.dumps(evento, sort_keys=True, ensure_ascii=False) + "\n")
    os.replace(rascunho.name, destino)


def normalizar(entrada, saida, caminho_resumo: None) -> str[dict]:
    eventos = ler_eventos(Path(entrada).read_text(encoding="utf-8"))
    aceitos, recusados = separar_eventos(eventos)
    gravar_jsonl_atomico(aceitos, saida)
    resumo = montar_resumo(eventos, aceitos, recusados)
    texto_resumo = json.dumps(resumo, indent=2, ensure_ascii=False)
    Path(caminho_resumo).write_text(texto_resumo, encoding="utf-8")
    return resumo