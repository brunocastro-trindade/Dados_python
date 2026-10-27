import argparse
import logging
import sys

from event_normalizer import normalizar


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Normaliza eventos em JSON ou JSONL para um JSONL canônico.")
    parser.add_argument("--entrada", required=True, help="Eventos de origem (array, json ou jsonl)")
    parser.add_argument("--saida", required=True, help="Jsonl canônico de saída.")
    parser.add_argument("--resumo", required=True, help="Resumo JSON")
    args = parser.parse_args()
    try:
        resumo = normalizar(args.entrada, args.saida, args.resumo)
    except FileNotFoundError:
        logging.error("Arquivo de entrada não encontrado: %s", args.entrada)
        sys.exit(1)
    except ValueError as erro:
        logging.error("Arquivo rejeitado: %s", erro)
        sys.exit(1)

    logging.info(
        "Processamento concluído: %s lidos, %s aceitos, %s recusados",
        resumo["eventos_lidos"],
        resumo["eventos_aceitos"],
        resumo["eventos_recusados"],
    )

    if resumo["eventos_recusados"] > 0:
        logging.error("Eventos recusados: %s", resumo["motivos"])
        sys.exit(1)


if __name__ == "__main__":
    main()