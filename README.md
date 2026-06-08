# jobme

Generative AI for effective job hunting.

`jobme` is an [AIMU](../aimu)-powered, multi-step agentic pipeline that tailors your
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

## Setup

```bash
uv sync                          # installs deps + the sibling ../aimu (editable)
uv run playwright install chromium   # one-time, for the default PDF backend
```

Set your API key for the default (cloud) model:

```bash
# PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

You can also put `ANTHROPIC_API_KEY` (and an optional `JOBME_MODEL`) in a `.env` file.

> **WeasyPrint (optional backend):** `--pdf-backend weasyprint` needs GTK native libraries,
> which require an extra install on Windows (see the WeasyPrint docs). The default
> Playwright backend has no such requirement.

## Inputs

Put these in the `input/` directory (everything here stays private via `.gitignore`
except the two shipped examples):

| File | Role | Required |
|------|------|----------|
| `input/cv.md` | **Content** source of truth — your full CV in markdown | yes |
| `input/resume.html` | **Style/format** template — your existing styled resume | yes |
| `input/cover_letter1.txt`, `cover_letter2.txt`, … | Writing-style samples (voice) | optional |

`input/cv.md` and `input/resume.html` ship as **examples so the tool runs out of the box —
replace them with your own** before real use. The pipeline only uses facts present in
`cv.md`; it never invents experience.

## Usage

Save a job posting to a text file, then run:

```bash
uv run scripts/tailor.py --jd path/to/job_description.txt
```

Options:

```
--model        AIMU model string (e.g. anthropic:claude-sonnet-4-6, ollama:qwen3:8b).
               Overrides the JOBME_MODEL env var; defaults to anthropic:claude-sonnet-4-6.
--pdf-backend  playwright (default) | weasyprint
--name         Explicit "Company - Title" label for the output folder.
--input-dir    Inputs directory (default: input)
--output-dir   Results directory (default: output)
```

Results are written to `output/<company-title>/`:

```
resume.html      resume.pdf        cover_letter.html   cover_letter.pdf
resume_content.md  cover_letter.txt  summary.md          trace.json
```

Run it once per new job posting.

## Use jobme with your own private data (private mirror)

To run jobme on your real CV without committing it here, create a **private mirror** repo
that tracks this project. (GitHub won't make a *private* fork of a public repo, and you
can't fork a repo into the account that already owns it — so use a mirror, not the Fork
button.) Your real files stay in a separate `me/` folder on a branch, so the committed
samples in `input/` are never overwritten and upstream updates merge cleanly.

1. Create an empty **private** repo on GitHub, e.g. `you/jobme-private`.
2. Clone this project **as a sibling of `aimu`** (so the `../aimu` path dependency in
   `pyproject.toml` still resolves) and wire two remotes:

   ```
   git clone https://github.com/saxman/jobme.git jobme-private
   cd jobme-private
   git remote rename origin upstream                        # updates come FROM here
   git remote add origin https://github.com/you/jobme-private.git
   git push -u origin main                                  # main = a clean mirror
   ```

3. Keep your data on its own branch:

   ```
   git switch -c personal
   mkdir me     # add your real cv.md, resume.html, cover_letter*.txt here
   git add me && git commit -m "My CV and resume" && git push -u origin personal
   ```

4. Run against your data (the `input/` samples stay untouched):

   ```
   uv run scripts/tailor.py --jd path/to/posting.txt --input-dir me
   ```

5. Pull in updates later — refresh the mirror, then merge into your branch:

   ```
   git fetch upstream
   git switch main && git merge --ff-only upstream/main && git push
   git switch personal && git merge main && uv sync && git push
   ```

   You can also refresh `main` entirely on GitHub (no clone needed) with:
   `gh repo sync you/jobme-private --source saxman/jobme --branch main`.

Only ever **push to `origin`** and **fetch from `upstream`** — that guarantees your private
data never reaches the public project.
