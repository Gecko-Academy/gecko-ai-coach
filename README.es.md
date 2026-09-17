<!-- translated from README.md at 99fa92c -->

# Gecko AI Coach

[English](README.md) · [Português (rascunho)](README.pt-BR.md) · **Español (borrador)**

> **Borrador.** Esta traducción fue generada por máquina y todavía no la revisó
> un hablante nativo. ¿Encontraste algo raro? [Corrígelo y abre un pull request](CONTRIBUTING.md#translate-the-readme)
> — es una muy buena primera contribución.

Hazle una pregunta al curso y recibe el fragmento que la responde, con un enlace
a la página. Después, **mide qué lo encontró, y mejóralo.**

Hecho para el [Dev3Pack AI-Engineering Bootcamp](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09),
y funciona con cualquier carpeta de archivos markdown.

## Contenido

- [Empieza aquí](#empieza-aquí)
- [Ayuda sin escribir código](#ayuda-sin-escribir-código)
- [Úsalo dentro de tu asistente](#úsalo-dentro-de-tu-asistente)
- [Hecho para mejorarse](#hecho-para-mejorarse)
- [Lo que no hace](#lo-que-no-hace)
- [Contribuir](#contribuir)

## Empieza aquí

Necesitas `git` y [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Gecko-Academy/gecko-ai-coach.git
cd gecko-ai-coach
uv sync --extra dev

uv run ai-coach ask "where do I submit my work" --pages ../dev3pack-cohort-2026-09/units/en
```

Sin clave, sin descargas, sin internet: el buscador por defecto lee las páginas y
cita el fragmento.

**Haz las preguntas en inglés.** Las páginas del curso están en inglés, y el
coach compara palabras. Una pregunta en español casi nunca encuentra la página
correcta.

## Ayuda sin escribir código

¿Encontraste una pregunta que el coach responde mal? Eso ya es una contribución.
Cada pregunta mal respondida, con la página que debería responderla, se convierte
en una prueba que todo cambio futuro tiene que pasar.

1. Haz un **fork** de este repositorio (botón **Fork**, arriba a la derecha en
   GitHub) y clona tu fork junto al curso.
2. Pregunta algo que de verdad quisiste saber esta semana.
3. Si la página citada es incorrecta, busca la correcta. El id es la ruta dentro
   de `units/en/`, sin `.mdx`: `units/en/unit0/runtime-lanes.mdx` es
   `unit0/runtime-lanes`.
4. Compruébalo y guárdalo:

```bash
uv run ai-coach propose "can I use claude instead of a local model" --page unit0/runtime-lanes \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

5. Súbelo y abre el pull request:

```bash
git checkout -b question/claude-instead-of-local   # skip this if you made a branch already
git add data/community/can-i-use-claude-instead-of-a-local-model.jsonl   # your files, by name
git commit -m "question: can I use claude instead of a local model"
git push -u origin question/claude-instead-of-local
```

`git push` muestra un enlace. Ábrelo y haz clic en **Create pull request**.

La guía completa, con los siguientes pasos, está en
[CONTRIBUTING.md](CONTRIBUTING.md) (en inglés).

## Úsalo dentro de tu asistente

El coach también funciona como **servidor MCP**. Así tu asistente (Claude Code,
Codex o cualquier cliente MCP) puede consultar el curso mientras trabajas.

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

| Herramienta | Hace |
|---|---|
| `ask_course` | los fragmentos que responden una pregunta, cada uno con el id de su página |
| `list_pages` | todas las páginas que el coach puede citar |
| `measure_retrieval` | la tasa de acierto en un conjunto etiquetado, con cada fallo listado |

Solo lee: nunca escribe archivos, nunca accede a URLs y nunca mira fuera de la
carpeta de páginas que recibió.

## Hecho para mejorarse

Es una herramienta de enseñanza, y la enseñanza está en mejorarla. El número que
dice qué tan buena es viene incluido:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl
```

Hoy, la tasa de acierto en las 3 primeras respuestas es **59%**. Un pull request
que sube ese número — **y dice cuánto, en qué conjunto de preguntas** — es la
contribución que este proyecto busca.

Los buscadores, los modelos y la biblioteca de Python están documentados en el
[README en inglés](README.md#retrievers).

## Lo que no hace

- **Indexar una carpeta `solutions/` o las respuestas de un quiz.** Una
  herramienta del curso que cita las respuestas es una chuleta. Dos pruebas lo
  garantizan.
- **Guardar un índice en disco.** Un índice desactualizado falla de una forma que
  nadie nota.
- **Leer una clave de otro lugar que no sea el entorno**, o mostrarla en un error.

## Contribuir

Empieza por el [paso 1 de CONTRIBUTING.md](CONTRIBUTING.md#rung-1--add-a-question-the-coach-gets-wrong):
diez minutos, sin código. O [revisa esta traducción](CONTRIBUTING.md#translate-the-readme).

MIT.
