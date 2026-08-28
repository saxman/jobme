# jobme

Generative AI for effective job hunting.

`jobme` is an [AIMU](https://pypi.org/project/aimu/)-powered, multi-step agentic pipeline that tailors your
resume and cover letter to a specific job posting and produces send-ready PDFs. You point
it at a job description; it rewrites your resume content to fit, reviews the result for
accuracy and intrigue, renders a two-page printable resume in your own resume's style, and
writes a cover letter in your voice — then exports both as PDFs.

## Features

- **Tailors resume content** from a comprehensive markdown CV to a specific job description.
- **Agentic review loop** (AIMU `EvaluatorOptimizer`) enforcing **accuracy** — no
  fabrication; every claim must be traceable to your CV — and **intrigue** — compelling and
  aligned to the posting.
- **Two-page printable HTML resume** rendered in the style/format of your existing HTML
  resume, with an automatic fit loop (renders, measures real page count and fill, then
  condenses, adds genuine CV detail, or adjusts typography to fill close to two pages).
- **Cover letter in your own voice**, learned from optional sample letters, held to the same
  accuracy/intrigue bar.
- **Send-ready PDFs** of both the resume and the cover letter.
- **Configurable model backend** — Anthropic Claude by default, easily switched to a local
  Ollama model — and a **pluggable PDF backend** (Playwright or WeasyPrint).
- **Run summary** capturing the model used, files produced, page count, and the full agent
  reasoning trace (`summary.md` + `trace.json`).

## Getting started

Your CV and the materials jobme generates are personal, so the normal way to use it is from
your **own private copy** that still pulls code updates from this project. (GitHub won't make
a private fork of a public repo, and you can't fork a repo into the account that owns it — so
this is a "private mirror," not the Fork button.)

1. Create an empty **private** repo on GitHub, e.g. `you/jobme-private`.

2. Clone this project and point it at both repos:

   ```
   git clone https://github.com/saxman/jobme.git jobme-private
   cd jobme-private
   git remote rename origin upstream            # code updates come FROM the public project
   git remote add origin https://github.com/you/jobme-private.git
   git push -u origin main                      # publish to YOUR repo and track it
   ```

   `git status -sb` should now show `## main...origin/main` — i.e. your `main` tracks your
   private repo, not the public one.

3. Install dependencies:

   ```
   uv sync                              # installs dependencies + the `jobme` command, incl. AIMU from PyPI
   source .venv/bin/activate            # activate the venv so `jobme` is on your PATH
   uv run playwright install chromium   # one-time, for the default PDF backend
   ```

   On Windows the activate script is `.venv\Scripts\activate`.

4. Add your materials to the `input/` folder and save them to your private repo:

   ```
   mkdir input   # add cv.md, resume.html, and optional cover_letter-1.txt, cover_letter-2.txt, ...
   git add input
   git commit -m "Add my CV and resume"
   git push origin main
   ```

   `input/` and `output/` are the tool's default directories, so runs need no path flags.
   They're committed only here in your private mirror. See [Your inputs](#your-inputs) for
   what goes in `input/`.

5. Set an API key for the default (cloud) model — or switch to a local model, see
   [Configuration](#configuration):

   ```
   # PowerShell
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   ```

   You can instead put `ANTHROPIC_API_KEY` (and an optional `JOBME_MODEL`) in a `.env` file.

## Running jobme

Save a job posting to a text file, then run it (once per posting):

```
jobme --jd path/to/posting.txt
```

Results are written to `output/<company-title>/` — committing them archives every run:

```
resume.html        resume.pdf         cover_letter.html   cover_letter.pdf
resume_content.md  cover_letter.txt   summary.md          trace.json
```

```
git add input output
git commit -m "Tailored application for <company>"
git push origin main
```

### Options

```
--jd           Path to the job-description file. (required)
--input-dir    Inputs directory (default: input).
--output-dir   Where results are written (default: output).
--model        AIMU model string; overrides JOBME_MODEL. Default anthropic:claude-opus-4-8.
--pdf-backend  playwright (default) | weasyprint
--name         Explicit "Company - Title" label for the output folder.
```

### Configuration

- **Model** — `--model` or the `JOBME_MODEL` env var. Examples: `anthropic:claude-opus-4-8`
  (default, needs `ANTHROPIC_API_KEY`); `ollama:qwen3:8b` for a fully local run, no API key.
- **PDF backend** — `--pdf-backend`. `playwright` (default) needs a one-time
  `playwright install chromium`. `weasyprint` needs GTK native libraries (an extra install
  on Windows — see the WeasyPrint docs).

## Your inputs

Put these in your `input/` folder:

| File | Role | Required |
|------|------|----------|
| `cv.md` | **Content** source of truth — your full CV in markdown | yes |
| `resume.html` | **Style/format** template — a complete styled resume | yes |
| `cover_letter-1.txt`, `cover_letter-2.txt`, … | Writing-style samples (your voice) | optional |
| `guidance.md` | Free-form writing/formatting guidance for the model | optional |

**`cv.md` — your complete CV (the content).** jobme tailors each resume by *selecting and
rephrasing* from this file and **never invents anything that isn't in it**, so make it
comprehensive: full work history with dates, titles, and measurable accomplishments, plus
skills, education, projects, and certifications. Use clear markdown headings (e.g. Summary,
Skills, Experience, Education). The richer it is, the better jobme can tailor — and since a
resume can only be as full as the relevant material in your CV, a thin CV yields a short
resume (jobme prints a warning when it can't fill two pages from what you provided).

**`resume.html` — your style/format template (the look).** jobme reuses this file's CSS,
fonts, layout, and section structure, swapping in the tailored content. It should be:
- a **complete, well-filled two-page resume**, not a stub — the renderer mimics its density
  and structure, so a full example produces a full result and a sparse one produces a sparse
  result;
- **self-contained**, with all styling in an inline `<style>` block;
- **print-ready for US Letter**, with page-break rules that let sections *flow across the page
  boundary*: keep a heading with its section and a role with its bullets (`break-after: avoid`),
  but don't wrap whole sections in `break-inside: avoid` — that strands large gaps and leaves
  the pages underfilled.

**Cover-letter samples (optional).** One or more `.txt` files of letters you've written; jobme
matches their tone and phrasing. Omit them and it writes in a neutral professional voice.

**`guidance.md` (optional) — writing/formatting rules for the model.** Free-form instructions
applied to every generation step (resume content, cover letter, and rendering) — for example
"Don't use em dashes; use commas or parentheses", "Use British spelling", or "Keep bullets to
one line". Accuracy always wins: guidance can shape wording and format but never licenses
inventing anything that isn't in your `cv.md`.

> The committed [`example/`](example/) folder holds **demo files** (`cv.md`, `resume.html`,
> `cover_letter-1.txt`, `jd_sample.txt`) plus a sample run in [`example/output/`](example/output/)
> — open them to see the expected format and output, but **don't put your real data there**.
> Your real CV and runs live in `input/` and `output/` in your **private mirror**, never in
> this public checkout.

## Keeping your copy in sync

Pull the latest project code into your private copy whenever you want updates:

```
git fetch upstream
git merge upstream/main    # a normal merge; resolve any conflicts, then commit
uv sync                    # if dependencies changed
git push origin main
```

> Always push with an explicit **`git push origin main`**, and only ever fetch from
> **`upstream`** — that keeps your private materials out of the public project. Because this
> public project commits nothing to `input/`/`output/`, your data there won't conflict on sync.

## Example output

The committed [`example/`](example/) folder is a complete, self-contained demo: the synthetic
inputs (Jane Q. Candidate / Atlas Freight) plus a sample run under
[`example/output/`](example/output/) so you can see what jobme produces — the tailored
resume and cover letter (HTML + PDF), the approved text, and the run `summary.md`/`trace.json`.

To regenerate it yourself in a plain clone of this project:

```
uv sync && uv run playwright install chromium
uv run jobme --jd example/jd_sample.txt --input-dir example --output-dir example/output
```

For real use, set up a private copy as in [Getting started](#getting-started) and keep your
materials in `input/` (runs go to `output/`); both are committed in your private mirror.

## Use from Kokua

jobme registers itself as a [Kokua](https://github.com/saxman/kokua) toolset, so the assistant can
tailor an application in conversation. Kokua discovers it through an entry point; nothing in Kokua
changes.

1. Install jobme into Kokua's environment:

   ```bash
   cd ../kokua && uv add --editable ../jobme
   uv run playwright install chromium   # once, for the default PDF backend
   ```

2. Declare the toolset in `$KOKUA_HOME/config.toml`, and gate the expensive tool:

   ```toml
   [agents.assistant]
   tools = ["jobme", ...]

   [security]
   confirm_tools = ["tailor_application", ...]

   [jobme]
   input_dir = ""        # empty: $KOKUA_HOME/data/jobme/input
   output_dir = ""       # empty: $KOKUA_HOME/data/jobme/output
   model = ""            # empty: JOBME_MODEL, then jobme's default
   pdf_backend = "playwright"
   ```

   Gating `tailor_application` means a run always needs your approval. It also means jobme can
   never run in a scheduled task, since a gated tool auto-denies in an unattended turn. That is
   deliberate for a tool this expensive.

3. Install the skill that teaches the procedure:

   ```bash
   cp -r jobme/skill "$KOKUA_HOME/data/skills/job-application"
   ```

   `kokua skills install` only reads Kokua's own bundled skills, so this one is copied by hand.
   `check_application_setup` reports whether it is in place.

4. Put `cv.md` and `resume.html` in the input directory (plus any `cover_letter*.txt` samples and
   a `guidance.md`), then ask the assistant to check the setup.

The assistant's model and jobme's model are separate settings. `[jobme] model` is what tailors the
documents; leaving it empty uses `JOBME_MODEL` or jobme's own default.
