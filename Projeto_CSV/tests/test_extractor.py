from csv_extractor import detectar_delimitador, extrair, processar_linhas


def test_detecta_ponto_e_virgula():
    texto = "data;loja;sku;quantidade;valor\n2024-05-10;Loja Rio;SKU;1;8,50"
    assert detectar_delimitador(texto) == ";"


def test_arquivo_com_bom(tmp_path):
    entrada = tmp_path / "bom.csv"
    conteudo = "data;loja;sku;quantidade;valor\n2024-05-10;Loja São Paulo;SKU;1;8,50\n"
    entrada.write_bytes(b"\xef\xbb\xbf" + conteudo.encode("utf-8"))

    resumo = extrair(entrada, tmp_path / "limpo.csv", tmp_path / "resumo.json")

    assert resumo["linhas_aceitas"] == 1


def test_linha_invalida_e_rejeitada():
    texto = "data;loja;sku;quantidade;valor\n2024-05-10;Loja Curitiba;SKU-CAFE-250;2;19.90\ndata-invalida;Loja Manaus;SKU-CAFE-250;1;12.00\n"

    linhas, resumo = processar_linhas(texto, ";")

    assert resumo["linhas_rejeitadas"] == 1
    assert resumo["linhas_aceitas"] == 1


def test_soma_considera_so_aceitas(tmp_path):
    resumo = extrair("data/vendas_ponto_virgula.csv", tmp_path / "limpo.csv", tmp_path / "resumo.json")

    assert resumo["soma_valor"] == 40.40
    assert resumo["linhas_lidas"] == 4
    assert resumo["linhas_rejeitadas"] == 1
