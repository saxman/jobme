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
button.) You keep your real files in a `me/` folder and work on a single `main` branch;
the committed samples in `input/` are left untouched.

**The model:** two remotes, one branch.

- `upstream` → this public project (you only ever *fetch* from it, for code updates).
- `origin` → your private repo (you only ever *push* to it).
- `main` → your private repo's code **plus** your `me/` data folder. This is where you work.

> ⚠️ **Safety rule:** always push with an explicit `git push origin main`, and only ever
> fetch from `upstream`. The commands below are explicit on purpose — a bare `git push`
> can target whichever remote `main` happens to track, which after cloning is `upstream`
> (the *public* project). Being explicit guarantees your private data only goes to `origin`.

The commands assume you `cd` into your mirror directory once; then every `git` command is
plain (no `-C <path>` needed).

### Workflow 1 — Getting set up (one time)

1. Create an empty **private** repo on GitHub, e.g. `you/jobme-private`.
2. Clone this project **as a sibling of `aimu`** (so the `../aimu` path dependency in
   `pyproject.toml` resolves) and wire the two remotes:

   ```
   git clone https://github.com/saxman/jobme.git jobme-private
   cd jobme-private
   git remote rename origin upstream                        # code updates come FROM here
   git remote add origin https://github.com/you/jobme-private.git
   git push -u origin main                                  # publish main to YOUR repo + track it
   ```

   The `-u origin main` is important: it makes your local `main` track *your private repo*,
   not the public project. Confirm with `git status -sb` — the first line should read
   `## main...origin/main`.

3. Add your data and install dependencies:

   ```
   mkdir me     # put your real cv.md, resume.html, cover_letter*.txt here
   git add me
   git commit -m "Add my CV and resume"
   git push origin main

   uv sync
   uv run playwright install chromium
   ```

### Workflow 2 — Making changes (run it / update your data)

Edit files in `me/`, then run against them — the `input/` samples stay untouched:

```
uv run scripts/tailor.py --jd path/to/posting.txt --input-dir me
```

### Workflow 3 — Pushing your changes to your private repo

```
git add me              # (and any other personal tweaks)
git commit -m "Update my materials"
git push origin main    # explicit origin → your private repo
```

### Workflow 4 — Syncing code updates from the public project

Fetch the latest project code and merge it into your `main`:

```
git fetch upstream
git merge upstream/main   # a normal merge; resolve conflicts if any
uv sync                   # if dependencies changed
git push origin main      # save the merged result to your private repo
```

If you hit a conflict in `.gitignore` or other files you've customized, resolve it in your
editor, `git add` the file, and `git commit`. Because your data lives in `me/` (which the
public project doesn't have), conflicts are usually limited to files you've changed yourself.
