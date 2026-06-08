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
  resume, with an automatic page-count fit check (renders, counts pages, condenses if over).
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
   uv sync                              # installs dependencies, incl. AIMU from PyPI
   uv run playwright install chromium   # one-time, for the default PDF backend
   ```

4. Add your materials in a `me/` folder and save them to your private repo:

   ```
   mkdir me     # add cv.md, resume.html, and optional cover_letter1.txt, ...
   git add me
   git commit -m "Add my CV and resume"
   git push origin main
   ```

   See [Your inputs](#your-inputs) for what goes in `me/`.

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
uv run scripts/tailor.py --jd path/to/posting.txt --input-dir me --output-dir me/output
```

Results are written to `me/output/<company-title>/`, which lives inside your tracked `me/`
folder — so committing them archives every run:

```
resume.html        resume.pdf         cover_letter.html   cover_letter.pdf
resume_content.md  cover_letter.txt   summary.md          trace.json
```

```
git add me
git commit -m "Tailored application for <company>"
git push origin main
```

### Options

```
--jd           Path to the job-description file. (required)
--input-dir    Inputs directory (your me/ folder).
--output-dir   Where results are written (me/output).
--model        AIMU model string; overrides JOBME_MODEL. Default anthropic:claude-sonnet-4-6.
--pdf-backend  playwright (default) | weasyprint
--name         Explicit "Company - Title" label for the output folder.
```

### Configuration

- **Model** — `--model` or the `JOBME_MODEL` env var. Examples: `anthropic:claude-sonnet-4-6`
  (default, needs `ANTHROPIC_API_KEY`); `ollama:qwen3:8b` for a fully local run, no API key.
- **PDF backend** — `--pdf-backend`. `playwright` (default) needs a one-time
  `playwright install chromium`. `weasyprint` needs GTK native libraries (an extra install
  on Windows — see the WeasyPrint docs).

## Your inputs

Put these in your `me/` folder:

| File | Role | Required |
|------|------|----------|
| `cv.md` | **Content** source of truth — your full CV in markdown | yes |
| `resume.html` | **Style/format** template — your existing styled resume | yes |
| `cover_letter1.txt`, `cover_letter2.txt`, … | Writing-style samples (your voice) | optional |

jobme only uses facts present in `cv.md` — it never invents experience — and the two-page
resume it generates reuses the look of your `resume.html`.

> The public project ships example `input/cv.md` and `input/resume.html` you can open to see
> the expected format (and to try jobme before adding your own — see below).

## Keeping your copy in sync

Pull the latest project code into your private copy whenever you want updates:

```
git fetch upstream
git merge upstream/main    # a normal merge; resolve any conflicts, then commit
uv sync                    # if dependencies changed
git push origin main
```

> Always push with an explicit **`git push origin main`**, and only ever fetch from
> **`upstream`** — that keeps your private materials out of the public project. Because your
> data lives in `me/` (which the public project doesn't have), merges rarely conflict.

## Try it without a private repo (optional)

To kick the tires in a plain clone of this project, jobme ships example inputs. Run against
them with the defaults:

```
uv sync && uv run playwright install chromium
uv run scripts/tailor.py --jd path/to/posting.txt
```

This reads the example `input/cv.md` / `input/resume.html` and writes results to `output/`
(git-ignored). For real use, set up a private copy as in [Getting started](#getting-started)
and keep your materials in `me/`.
