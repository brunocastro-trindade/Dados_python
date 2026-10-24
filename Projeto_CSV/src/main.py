import argparse
import logging
import sys

from csv_extractor import extrair


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Extrai e valida o export diário de vendas.")
    parser.add_argument("--entrada", required=True, help="CSV bruto de vendas")
    parser.add_argument("--saida", required=True, help="CSV limpo de saida")
    parser.add_argument("--resumo", required=True, help="Resumo JSON")
    args = parser.parse_args()
    try:
        resumo = extrair(args.entrada, args.saida, args.resumo)
    except FileNotFoundError:
        logging.error("Arquivo de entrada não encontrado: %s", args.entrada)
        sys.exit(1)
    except ValueError as erro:
        logging.error("Arquivo rejeitado: %s", erro)
        sys.exit(1)

    logging.info(
        "Processamento concluído: %s lidas, %s aceitas, %s rejeitadas, soma %s",
        resumo["linhas_lidas"],
        resumo["linhas_aceitas"],
        resumo["linhas_rejeitadas"],
        resumo["soma_valor"],
    )


main()