<!-- translated from README.md at 99fa92c -->

# Gecko AI Coach

[English](README.md) · [Português (rascunho)](README.pt-BR.md) · **Español (borrador)**

> **Borrador.** Esta traducción se generó automáticamente y todavía no la ha revisado
> un hablante nativo. ¿Encontraste algo raro? [Corrígelo y abre un pull request](CONTRIBUTING.md#translate-the-readme)
> — es una muy buena primera contribución.

Haz una pregunta sobre el curso y recibe el fragmento que la responde, con un
enlace a la página. Después, **evalúa el buscador y mejóralo.**

Hecho para el [Dev3Pack AI-Engineering Bootcamp](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09),
y sirve para cualquier carpeta de archivos Markdown.

## Contenido

- [Empieza aquí](#empieza-aquí)
- [Ayuda sin escribir código](#ayuda-sin-escribir-código)
- [Úsalo dentro de tu asistente](#úsalo-dentro-de-tu-asistente)
- [Hecho para mejorarse](#hecho-para-mejorarse)
- [Lo que no hace](#lo-que-no-hace)
- [Contribuir](#contribuir)

## Empieza aquí

Necesitas `git` y [`uv`](https://docs.astral.sh/uv/). El ejemplo también necesita
una copia del curso en la carpeta vecina `../dev3pack-cohort-2026-09`. Sigue
[la preparación inicial](CONTRIBUTING.md#set-up-once) para obtenerla.

```bash
git clone https://github.com/Gecko-Academy/gecko-ai-coach.git
cd gecko-ai-coach
uv sync --extra dev

uv run ai-coach ask "where do I submit my work" --pages ../dev3pack-cohort-2026-09/units/en
```

Una vez instaladas las herramientas y descargadas las páginas, el buscador
predeterminado funciona sin clave de API, sin descargar un modelo y sin conexión
a internet. Lee las páginas y cita los fragmentos.

**Haz las preguntas en inglés.** Las páginas del curso están en inglés, y el
coach compara palabras. Una pregunta en español casi nunca encuentra la página
correcta.

## Ayuda sin escribir código

¿Encontraste una pregunta que el coach responde mal? Eso ya es una contribución.
Cada pregunta mal respondida, junto con la página que sí la responde, se guarda
como un caso de evaluación para medir los cambios futuros.

1. Haz un **fork** de este repositorio (botón **Fork**, arriba a la derecha en
   GitHub) y clona tu fork junto al curso.
2. Pregunta algo que realmente hayas querido saber esta semana.
3. Revisa los fragmentos y las páginas citadas. Si ninguna responde a la
   pregunta, busca una que sí lo haga. El identificador es la ruta dentro
   de `units/en/`, sin `.mdx`: `units/en/unit0/runtime-lanes.mdx` es
   `unit0/runtime-lanes`.
4. Compruébalo y guárdalo:

```bash
uv run ai-coach propose "can I use claude instead of a local model" --page unit0/runtime-lanes \
  --pages ../dev3pack-cohort-2026-09/units/en --write
```

5. Continúa solo si `propose` ha escrito un archivo nuevo. Si indica
   `ALREADY ANSWERED` o que la pregunta ya existe, prueba otra. Comprueba también
   que ninguna de las otras páginas citadas responda a la pregunta: `propose`
   solo comprueba la página que le indicaste. Después, sube el archivo y abre
   el pull request:

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

| Herramienta | Función |
|---|---|
| `ask_course` | los fragmentos que responden una pregunta, cada uno con el identificador de su página |
| `list_pages` | todas las páginas que el coach puede citar |
| `measure_retrieval` | la tasa de aciertos en un conjunto etiquetado, con cada fallo detallado |

Solo lee: nunca escribe archivos, nunca accede a URLs y nunca mira fuera de la
carpeta de páginas indicada. El texto recuperado se trata como datos, nunca como
instrucciones.

## Hecho para mejorarse

Esta herramienta sirve para aprender mientras la mejoras. Incluye un comando
para medir si encuentra las páginas correctas:

```bash
uv run ai-coach measure --pages ../dev3pack-cohort-2026-09/units/en --cases data/dev3pack.jsonl
```

La tasa de aciertos mide cuántas preguntas tienen una página aceptada entre los
tres primeros resultados. Depende del conjunto de preguntas y de la versión de
las páginas; ejecuta el comando para medir tu copia. Consulta también
[los resultados documentados](CONTRIBUTING.md#the-numbers-today). Un cambio en el
buscador debe indicar el resultado antes y después, el conjunto usado y las
preguntas que empeoraron.

Los buscadores, los modelos y la biblioteca de Python están documentados en el
[README en inglés](README.md#retrievers).

## Lo que no hace

- **Indexar una carpeta `solutions/` o las respuestas de un quiz.** Una
  herramienta que revela las soluciones deja de ayudar a aprender. Dos pruebas
  verifican esta protección.
- **Guardar un índice en disco.** Un índice desactualizado falla de una forma que
  nadie nota.
- **Leer una clave fuera de las variables de entorno**, o mostrarla en un error.

## Contribuir

Empieza por el [paso 1 de CONTRIBUTING.md](CONTRIBUTING.md#rung-1--add-a-question-the-coach-gets-wrong):
diez minutos, sin código. O [revisa esta traducción](CONTRIBUTING.md#translate-the-readme).

MIT.
