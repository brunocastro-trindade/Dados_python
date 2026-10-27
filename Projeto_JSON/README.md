# 002 — JSON e JSON Lines

Material educacional de Engenharia de Dados. Projeto anterior recomendado: 001 — Extração robusta de CSV. Os eventos e usuários deste exercício são fictícios.

## Descrição

O coletor do aplicativo manda o mesmo tipo de evento em dois formatos: um array JSON e um arquivo JSON Lines. Este projeto lê os dois, exige `event_id`, `occurred_at`, `user_id` e `name`, recusa evento sem id e grava um JSONL canônico com escrita atômica.

## Problema

Um array JSON grande precisa ser parseado inteiro. Um JSONL pode ser lido linha a linha, mas uma linha sem `event_id` quebra a deduplicação mais adiante. Gravar o destino direto também deixa arquivo pela metade se o processo morre no meio da escrita.

## Objetivos de aprendizagem

- Reconhecer array JSON e JSONL pelo conteúdo.
- Validar um contrato mínimo de evento.
- Recusar evento sem identificador em vez de inventar um id.
- Trocar o arquivo de saída por `os.replace` depois de escrever um temporário.

## Conceitos de Engenharia de Dados

Formato canônico, contrato de evento, rejeição, escrita atômica e resumo de carga. O JSONL de saída é a forma estável que os jobs seguintes consomem, independente de como o aplicativo entregou o lote.

## Tecnologias

Python 3.11 ou superior e biblioteca padrão (`json`, `tempfile`, `os.replace`, `argparse`, `logging`).

## Arquitetura

A origem entra como array ou como linhas. A validação separa aceitos e recusados. O destino só aparece depois do replace do arquivo temporário.

![Arquitetura](assets/architecture.png)

## Estrutura de diretórios

```text
002-json-e-jsonl/
  src/main.py
  src/event_normalizer.py
  tests/test_events.py
  data/eventos.json
  data/eventos.jsonl
  assets/architecture.png
  requirements.txt
  .env.example
```

## Pré-requisitos

Python 3.11+. Nenhuma dependência externa para rodar o job.

## Instalação e configuração

```powershell
cd 002-json-e-jsonl
copy .env.example .env
```

## Como executar

```powershell
python src/main.py --entrada data/eventos.jsonl --saida out/eventos.jsonl --resumo out/resumo.json
```

Se algum evento for recusado, o JSONL recebe só os aceitos e o processo termina com código 1. Arquivo vazio ou JSON inválido também termina com código 1.

## Como validar

```powershell
pytest
```

Os testes comparam os dois formatos de origem e verificam a recusa de evento sem `event_id`.

## Exemplos de entrada e saída

Array:

```json
[{"event_id": "evt-01", "occurred_at": "2024-07-01T14:32:00-03:00", "user_id": "usr-1001", "name": "produto_visto"}]
```

Linha canônica, com chaves ordenadas:

```json
{"event_id": "evt-01", "name": "produto_visto", "occurred_at": "2024-07-01T14:32:00-03:00", "user_id": "usr-1001"}
```

Um objeto sem `event_id` entra no resumo como `evento sem id` e não aparece no JSONL.

## Decisões técnicas

O formato é decidido pelo primeiro caractere não branco: `[` indica array; caso contrário cada linha não vazia é um objeto. A escrita usa arquivo temporário no mesmo diretório e `os.replace`, que é atômico no mesmo volume. Chaves ordenadas deixam a saída comparável em teste. Evento recusado não ganha id sintético.

## Limitações

Não faz streaming de array JSON gigante. Não valida o calendário de `occurred_at`, só a presença do texto. Não há fila nem compactação.

## Melhorias sugeridas

Validar o timestamp com fuso. Particionar o JSONL por dia do evento. Enviar os recusados para um arquivo morto em vez de só contar no resumo.

## Aplicação empresarial

Times de produto que exportam cliques tanto num dump JSON do dia quanto num stream já em JSONL, e precisam de uma trilha única antes de carregar o data lake.

## Competências para o portfólio

Mostra leitura de dois formatos semi-estruturados, contrato de evento e publicação segura do arquivo de saída.

## Desafios opcionais

Aceitar JSON concatenado (vários valores seguidos) além de JSONL. Calcular atraso entre `occurred_at` e o horário de processamento.
