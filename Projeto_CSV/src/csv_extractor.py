from datetime import datetime
from pathlib import Path
import csv
import io
import json

COLUNAS = ["data", "loja", "sku", "quantidade", "valor"]


def detectar_encoding(dados):
    try:
        dados.decode("utf-8-sig")
        return "utf-8-sig"
    except UnicodeDecodeError:
        return "latin-1"


def detectar_delimitador(texto):
    cabecalho = texto.splitlines()[0]
    pontos_virgula = cabecalho.count(";")
    virgulas = cabecalho.count(",")

    if pontos_virgula > virgulas:
        return ";"
    elif virgulas > pontos_virgula:
        return ","
    else:
        raise ValueError("Não foi possível detectar o delimitador do cabeçalho")


def normalizar_valor(texto):
    texto_com_ponto = texto.replace(",", ".")
    return float(texto_com_ponto)


def data_valida(texto):
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except ValueError:
        return False
     

def quantidade_valida(texto):
    try:
        numero = int(texto)
        return numero > 0
    except ValueError:
        return False


def linha_completa(linha):
    return None not in linha.values()


def valor_valido(texto):
    try:
        normalizar_valor(texto)
        return True
    except ValueError:
        return False


def processar_linhas(texto, delimitador):
    leitor = csv.DictReader(io.StringIO(texto), delimiter=delimitador)
    if leitor.fieldnames != COLUNAS:
        raise ValueError(f"Cabeçalho inválido: {leitor.fieldnames}. Esperado: {COLUNAS}")


    linhas_aceitas = []
    rejeitadas = 0
    soma = 0.0
    for linha in leitor:
        if (linha_completa(linha)
             and data_valida(linha["data"])
             and quantidade_valida(linha["quantidade"])
             and valor_valido(linha["valor"])
        ):              
            linha["valor"] = normalizar_valor(linha["valor"])
            linhas_aceitas.append(linha)
            soma += linha["valor"]
        else:
            rejeitadas += 1
    resumo = {
        "linhas_lidas": len(linhas_aceitas) + rejeitadas,
        "linhas_aceitas": len(linhas_aceitas),
        "linhas_rejeitadas": rejeitadas,
        "soma_valor": round(soma, 2),
    }
    return linhas_aceitas, resumo


def gravar_csv(linhas, caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)


def gravar_resumo(resumo, caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, indent=2)


def extrair(caminho_entrada, caminho_saida, caminho_resumo):
    dados = Path(caminho_entrada).read_bytes()
    encoding = detectar_encoding(dados)
    texto = dados.decode(encoding)
    delimitador = detectar_delimitador(texto)
    linhas, resumo = processar_linhas(texto, delimitador)
    gravar_csv(linhas, caminho_saida)
    gravar_resumo(resumo, caminho_resumo)
    return resumo
