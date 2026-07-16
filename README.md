# Robo RPA para Tardz Automations

Este projeto contem um robo RPA em Python compativel com a plataforma Tardz Automations. A automacao abre o Google Chrome com Selenium, acessa o Google, digita o termo de pesquisa, envia a busca e salva um screenshot dos resultados em `outputs/google-search-results.png`.

## Entrada na Tardz

O entrypoint que deve ser cadastrado na Tardz e:

```bash
main.py
```

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
$env:TARDZ_PARAMETERS='{"cliente":"empresa_x","data_inicio":"2026-07-01","data_fim":"2026-07-31","modo":"producao","termo_pesquisa":"Tardz Automations","headless":false,"intervalo_acoes":1,"manter_aberto_segundos":30}'
python main.py
```

## Parametros aceitos

`TARDZ_PARAMETERS` deve ser uma string JSON contendo um objeto.

Campos obrigatorios:

- `cliente`: identificador do cliente ou empresa.
- `data_inicio`: data inicial no formato `YYYY-MM-DD`.
- `data_fim`: data final no formato `YYYY-MM-DD`.
- `modo`: modo de execucao, por exemplo `producao`, `homologacao` ou `teste`.

Campos opcionais:

- `termo_pesquisa`: texto que sera pesquisado no Google. Se nao for informado, usa `Tardz Automations`.
- `headless`: `false` para abrir o Chrome visivel na tela. Use `true` para executar sem janela grafica. O padrao e `false`.
- `aguardar_segundos`: tempo de espera apos carregar os resultados. O padrao e `3`.
- `intervalo_acoes`: pausa em segundos entre as acoes visiveis, como abrir, clicar e digitar. O padrao e `1`.
- `manter_aberto_segundos`: tempo para manter o Chrome aberto no final da automacao. O padrao e `30`. Use `0` para deixar a janela aberta apos o fim do robo.
- `chrome_binary_path`: caminho do executavel do Chrome, se o runner usar uma instalacao customizada.
- `chromedriver_path`: caminho do ChromeDriver, se voce nao quiser depender do Selenium Manager.

Tambem e possivel informar `CHROME_BINARY_PATH` e `CHROMEDRIVER_PATH` como variaveis de ambiente.

Exemplo:

```json
{
  "cliente": "empresa_x",
  "data_inicio": "2026-07-01",
  "data_fim": "2026-07-31",
  "modo": "producao",
  "termo_pesquisa": "Tardz Automations",
  "headless": false,
  "aguardar_segundos": 3,
  "intervalo_acoes": 1,
  "manter_aberto_segundos": 30
}
```

Para ver o Chrome na tela, o runner precisa executar em uma sessao de desktop interativa, com usuario logado e area de trabalho desbloqueada. Se o runner estiver rodando como servico em segundo plano, em servidor sem interface grafica ou em sessao bloqueada, a janela do Chrome pode nao aparecer mesmo com `headless` igual a `false`.

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
