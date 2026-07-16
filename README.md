# Robo RPA para Tardz Automations

Este projeto contem um robo RPA em Python compativel com a plataforma Tardz Automations. A automacao abre o Google Chrome com Selenium, acessa o Google, realiza uma pesquisa e salva um screenshot dos resultados em `outputs/google-search-results.png`.

## Entrada na Tardz

O entrypoint que deve ser cadastrado na Tardz e:

```bash
main.py
```
teste
O runner externo deve executar:

```bash
python main.py
```

## Como executar localmente

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Execute o robo informando `TARDZ_PARAMETERS`:

```bash
$env:TARDZ_PARAMETERS='{"cliente":"empresa_x","data_inicio":"2026-07-01","data_fim":"2026-07-31","modo":"producao","termo_pesquisa":"Tardz Automations"}'
python main.py
```

## Parametros aceitos

`TARDZ_PARAMETERS` deve ser uma string JSON contendo um objeto.

Campos obrigatorios:

- `cliente`: identificador do cliente ou empresa.
- `data_inicio`: data inicial no formato `YYYY-MM-DD`.
- `data_fim`: data final no formato `YYYY-MM-DD`.
- `modo`: modo de execucao, por exemplo `producao`, `homologacao` ou `teste`.
- `termo_pesquisa`: texto que sera pesquisado no Google.

Campos opcionais:

- `headless`: `true` para executar sem janela grafica visivel. O padrao e `false`.
- `aguardar_segundos`: tempo de espera apos carregar os resultados. O padrao e `3`.

Exemplo:

```json
{
  "cliente": "empresa_x",
  "data_inicio": "2026-07-01",
  "data_fim": "2026-07-31",
  "modo": "producao",
  "termo_pesquisa": "Tardz Automations",
  "headless": false,
  "aguardar_segundos": 3
}
```

## Pastas locais

O robo cria automaticamente as pastas abaixo quando elas nao existirem:

- `downloads/`
- `outputs/`
- `logs/`

Use essas pastas para arquivos baixados, relatorios e registros gerados durante a execucao.

## Dependencias

Este projeto usa Selenium para controlar o Google Chrome.

```bash
pip install -r requirements.txt
```

O ambiente de execucao precisa ter o Google Chrome instalado. O Selenium Manager, incluido nas versoes recentes do Selenium, tenta localizar ou obter automaticamente o driver compativel quando necessario.

## Credenciais

Nao versione senhas, tokens, chaves ou qualquer dado sensivel. Quando necessario, receba credenciais por parametros, variaveis de ambiente ou outro mecanismo seguro externo.
