<!-- translated from README.md at 99fa92c -->

# Gecko AI Coach

[English](README.md) · **Português (rascunho)** · [Español (borrador)](README.es.md)

> **Rascunho.** Esta tradução foi gerada por máquina e ainda não foi revisada por
> um falante nativo. Encontrou algo estranho? [Corrija e abra um pull request](CONTRIBUTING.md#translate-the-readme)
> — é uma ótima primeira contribuição.

Faça uma pergunta sobre o curso e receba o trecho que responde, com um link para a
página. Depois, **meça quem encontrou esse trecho, e faça melhor.**

Feito para o [Dev3Pack AI-Engineering Bootcamp](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09),
e funciona com qualquer pasta de arquivos markdown.

## Sumário

- [Comece aqui](#comece-aqui)
- [Ajude sem escrever código](#ajude-sem-escrever-código)
- [Use dentro do seu assistente](#use-dentro-do-seu-assistente)
- [Feito para ser melhorado](#feito-para-ser-melhorado)
- [O que ele não faz](#o-que-ele-não-faz)
- [Contribuir](#contribuir)

## Comece aqui

Você precisa de `git` e [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Gecko-Academy/gecko-ai-coach.git
cd gecko-ai-coach
uv sync --extra dev

uv run ai-coach ask "where do I submit my work" --pages ../dev3pack-cohort-2026-09/units/en
```

Sem chave, sem download, sem internet: o buscador padrão lê as páginas e cita o
trecho.

**Faça as perguntas em inglês.** As páginas do curso estão em inglês, e o coach
compara palavras. Uma pergunta em português quase nunca encontra a página certa.

## Ajude sem escrever código

Encontrou uma pergunta que o coach responde errado? Isso já é uma contribuição.
Cada pergunta errada, com a página que deveria responder, vira um teste que toda
mudança futura precisa passar.

1. Faça um **fork** deste repositório (botão **Fork**, no canto superior direito
   do GitHub) e clone o seu fork ao lado do curso.
2. Pergunte algo que você realmente quis saber esta semana.
3. Se a página citada estiver errada, encontre a página certa. O id é o caminho
   dentro de `units/en/`, sem `.mdx`: `units/en/unit0/runtime-lanes.mdx` é
   `unit0/runtime-lanes`.
4. Confira e salve:

```bash
uv run ai-coach propose "can I use claude instead of a local model" --page unit0/runtime-lanes \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

5. Envie e abra o pull request:

```bash
git checkout -b question/claude-instead-of-local   # skip this if you made a branch already
git add data/community/can-i-use-claude-instead-of-a-local-model.jsonl   # your files, by name
git commit -m "question: can I use claude instead of a local model"
git push -u origin question/claude-instead-of-local
```

O `git push` mostra um link. Abra o link e clique em **Create pull request**.

O passo a passo completo, com os próximos degraus, está no
[CONTRIBUTING.md](CONTRIBUTING.md) (em inglês).

## Use dentro do seu assistente

O coach também roda como **servidor MCP**. Assim, o seu assistente (Claude Code,
Codex ou qualquer cliente MCP) pode consultar o curso enquanto você trabalha.

```json
{
  "mcpServers": {
    "gecko-ai-coach-course": {
      "command": "uvx",
      "args": ["--from", "gecko-ai-coach @ git+https://github.com/Gecko-Academy/gecko-ai-coach.git@main",
               "gecko-ai-coach-course"],
      "env": { "COACH_PAGES": "/path/to/dev3pack-cohort-2026-09/units/en" }
    }
  }
}
```

| Ferramenta | Faz |
|---|---|
| `ask_course` | os trechos que respondem a uma pergunta, cada um com o id da página |
| `list_pages` | todas as páginas que o coach pode citar |
| `measure_retrieval` | a taxa de acerto num conjunto rotulado, com cada erro listado |

Ele só lê: nunca grava arquivos, nunca acessa URLs e nunca olha fora da pasta de
páginas que recebeu.

## Feito para ser melhorado

Esta é uma ferramenta de ensino, e o ensino está em melhorá-la. O número que
diz o quanto ela é boa vem junto:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl
```

Hoje, a taxa de acerto nas 3 primeiras respostas é **59%**. Um pull request que
aumenta esse número — **e diz quanto, em qual conjunto de perguntas** — é a
contribuição que este projeto quer.

Buscadores, modelos e a biblioteca Python estão documentados no
[README em inglês](README.md#retrievers).

## O que ele não faz

- **Indexar uma pasta `solutions/` ou as respostas de um quiz.** Uma ferramenta
  do curso que cita o gabarito é uma cola. Dois testes garantem isso.
- **Guardar um índice em disco.** Um índice desatualizado erra de um jeito que
  ninguém percebe.
- **Ler uma chave de outro lugar que não seja o ambiente**, ou mostrá-la num erro.

## Contribuir

Comece pelo [degrau 1 do CONTRIBUTING.md](CONTRIBUTING.md#rung-1--add-a-question-the-coach-gets-wrong):
dez minutos, sem código. Ou [revise esta tradução](CONTRIBUTING.md#translate-the-readme).

MIT.
