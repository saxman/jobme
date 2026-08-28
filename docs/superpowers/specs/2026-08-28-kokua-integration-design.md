# jobme as a Kokua capability

Date: 2026-08-28
Status: approved, ready for an implementation plan

## Goal

Let the [Kokua](https://github.com/saxman/kokua) personal assistant tailor a resume and cover letter
to a job posting by driving jobme's existing pipeline, without either project growing a hard
dependency on the other and without any change to Kokua's `src/`.

## Constraints that shaped the design

Both come from the projects as they stand, and neither is negotiable in this work.

- **Kokua grows by plugin, not by core change.** All 21 toolsets Kokua ships register through the
  `kokua.toolsets` entry-point group exactly the way a third party's would, and
  `tests/toolsets/test_registration.py` pins that table against `src/kokua/toolsets/` in both
  directions. jobme is a third party, so it registers the same way and Kokua's package is untouched.
- **jobme's pipeline is synchronous and prints.** `jobme.pipeline.run` blocks for minutes across a
  chain of LLM calls and reports progress with `print`. Kokua's turn loop is async and its stated
  purpose is that the loop is watched rather than inferred, so progress has to reach the channel.

## Decisions

| Question | Decision |
|---|---|
| Seam | A Kokua `Toolset` shipped from the jobme repo, plus a Kokua skill that is a procedure over its tools |
| Skill's job | Procedure only, no script of its own (the pattern `synthesize-documents` uses over the `documents` toolset) |
| Skill's home | The jobme repo, copied into `$KOKUA_HOME/data/skills` by hand |
| Inputs and outputs | Under `$KOKUA_HOME/data/jobme/`, with finished PDFs copied into the downloads folder |
| Run behavior | A blocking tool call on a worker thread, streaming progress to the channel |
| Tool surface | `tailor_application` and `check_application_setup` |
| Packaging | Installed into Kokua's environment as a third party; Kokua declares nothing |

## Architecture

### What lands where

jobme repo:

```
jobme/kokua.py            # TOOLSET, the two tools, settings, guidance
jobme/skill/SKILL.md      # the job-application procedure (content, not code)
tests/test_kokua.py       # mock-only adapter tests (jobme's first tests)
pyproject.toml            # the kokua.toolsets entry point
README.md                 # a "Use from Kokua" section
CLAUDE.md                 # the rule that jobme/kokua.py is the only Kokua-aware module
```

Kokua repo: documentation only. A `docs/how-to/` page on installing a third-party toolset, using
jobme as the worked example, and its `CHANGELOG.md` line. No `src/` change, no `pyproject.toml`
change, no test change.

### The dependency direction

`jobme/kokua.py` is the only module that imports from `kokua`, and jobme does not depend on Kokua.
An entry point is inert unless something loads its group, so `pip install jobme` stays exactly as
heavy as it is today and jobme's CLI keeps working with Kokua absent. The adapter imports
`kokua.registry` at module scope (it must, to build the `Toolset`), which is safe because nothing
imports `jobme.kokua` unless Kokua's plugin loader does.

### Installation

The user installs jobme into Kokua's environment (`uv add --editable ../jobme`, or
`pip install jobme`) and Kokua discovers the toolset through the entry point. The agent holds it
once `[agents.assistant].tools` names `jobme`, per Kokua's rule that a capability is declared and
never defaulted.

The `aimu` floors are compatible: jobme requires `>=0.26.0`, Kokua requires `>=0.25.0`, and the
sibling `../aimu` checkout both projects develop against is 0.26.0.

## Changes to jobme's pipeline

Three changes. The pipeline's structure, prompts, two-page fit loop, and PDF code are untouched.

### 1. Progress becomes a callback

`pipeline.run` grows a keyword-only `progress: Callable[[str], None] = print`, threaded through
`_with_retry` and `_render_resume`, which are the only other functions that print. Every existing
`print(f"[jobme] ...")` becomes a `progress(...)` call. The CLI passes nothing and behaves as it does
today.

### 2. `run()` returns its warnings

The low-fill warning is currently only a printed line. It becomes an entry in a `warnings: list[str]`
key on the dict `run()` already returns, so the tool can put it in the tool result where the model
will relay it rather than leaving it in a progress line the model may not attend to. The line is
still emitted through `progress` as well, so CLI output is unchanged.

### 3. Cancellation

`run` grows a keyword-only `cancel: threading.Event | None = None`, checked between steps in `run`
and between rounds in the fit loop, raising a `RunCancelled` exception the adapter turns into a plain
message. Without it, a Kokua `/stop` ends the turn while the worker thread keeps spending on model
calls for several more minutes. Six checks, no other structure.

### The Playwright gotcha

`jobme/pdf.py` uses Playwright's **sync** API, which raises when a loop is running in the calling
thread. `asyncio.to_thread` puts the pipeline on a worker with no loop, so it works. This is why the
adapter can never be "optimized" into running the pipeline directly on the event loop. It goes in the
adapter's module docstring.

## The toolset

`jobme/kokua.py` exports a module-level `TOOLSET` named `jobme`, `cross_cutting=False` (jobme is
domain work, so an agent holding it should read as tool-heavy to Kokua's delegation guidance).

### Settings

The `[jobme]` section of `config.toml`, declared as `Setting` instances on the toolset:

| key | kind | default | resolution |
|---|---|---|---|
| `input_dir` | `str` | `""` | empty resolves to `$KOKUA_HOME/data/jobme/input` |
| `output_dir` | `str` | `""` | empty resolves to `$KOKUA_HOME/data/jobme/output` |
| `model` | `str` | `""` | empty falls through to jobme's `JOBME_MODEL` env var, then `DEFAULT_MODEL`; this is deliberately not Kokua's assistant model |
| `pdf_backend` | `str` | `"playwright"` | one of jobme's `BACKENDS` keys |

A `Setting` default is static and has no view of `AssistantConfig`, so `""`-means-derive is how the
defaults land under `$KOKUA_HOME`. This is the pattern `[github_backup].repo` already uses. All four
are cold (`hot=False`): each is read once when a run starts, and no live surface offers them.

### `tailor_application(job_description: str, name: str = "") -> str`

1. Resolve the settings, creating the input and output directories if absent.
2. Write `job_description` to a file under the output directory, since jobme's `Config` takes a
   `jd_path`.
3. Build a jobme `Config` and run the pipeline under `asyncio.to_thread`.
4. Marshal progress back with `asyncio.run_coroutine_threadsafe(notify(line), loop)`, where `notify`
   is `ctx.state.notify` (Kokua wires it to `channel.send`). When `notify` is `None`, as it is for a
   spawned worker with no channel, progress degrades to a no-op rather than failing.
5. Copy both PDFs into `$KOKUA_HOME/data/downloads` as `<slug>_resume.pdf` and
   `<slug>_cover_letter.pdf`. The web front end serves that folder flat, so the slug prefix is what
   keeps two applications from colliding.
6. Return the page count, the fill, every warning, the absolute output directory, and the
   `/download/<name>` links. Both the path and the link are reported because the link only resolves
   in the web UI and the toolset has no way to ask which front end is attached.

Failures return a sentence naming what to fix rather than raising, following `github_backup`'s
reasoning: AIMU's generic `Tool '<name>' raised an error` line loses the part the user needs.

### `check_application_setup() -> str`

Read-only and cheap. Reports the resolved input directory, which of `cv.md`, `resume.html`,
`cover_letter*.txt`, and `guidance.md` are present, whether `check_backend` passes (Chromium
installed), whether the model's API key is in the environment, and whether the skill is installed in
`$KOKUA_HOME/data/skills`.

`build` returns both tools unconditionally, unlike `github_backup`, which returns nothing when its
`repo` is unset. A missing `cv.md` is exactly what `check_application_setup` exists to report, so
hiding the toolset when inputs are absent would remove the thing that explains the absence.

### Guidance

The toolset's `guidance` string tells the model what jobme is, that a run takes minutes and costs
money so the posting and the job title should be confirmed with the user first, to call
`check_application_setup` when inputs may be missing, and that it must never write CV content itself
because jobme's whole accuracy guarantee is that nothing appears in the resume that is not in
`cv.md`.

### Environment

The adapter deliberately does not walk parent directories for `.env` files the way jobme's CLI does.
That is cwd-dependent behavior belonging to a CLI; under Kokua the API key comes from the process
environment, and `check_application_setup` says so when it is missing.

### Security

The recommendation, documented rather than coded, is to add `"tailor_application"` to
`[security].confirm_tools`. A run is minutes of billed calls. The consequence is that jobme can never
run in a scheduled proactive turn, since gated tools auto-deny there, and that is the right trade for
a tool this expensive. Kokua's principle that every security control is a value in `config.toml` and
never a constant in source is why this is a documented recommendation and not something the toolset
enforces.

## The skill

`jobme/skill/SKILL.md`, name `job-application`, declaring `compatibility: Requires the jobme
toolset`. A procedure with no script. Its steps:

1. **Get the whole posting, verbatim.** If the user gives a URL, fetch it first and show what came
   back. Never paraphrase a posting into the tool: jobme tailors against the text it is given, and a
   summary silently degrades the output.
2. **Check setup before the first run of a session** with `check_application_setup`, so a missing
   `cv.md` or an uninstalled Chromium surfaces before several minutes of billed calls rather than
   after.
3. **Confirm before running.** Name the company and title inferred from the posting, say the run
   takes minutes and costs money, and wait for a yes. The `confirm_tools` gate is the backstop; the
   model still sets the expectation.
4. **Call `tailor_application`** with the full text and an explicit `name` of `"Company - Title"`
   when it is inferable, so the output folder is findable later.
5. **Report every warning verbatim.** A low-fill warning means the CV lacks the material, and
   softening it into "looks good" is the failure this step exists to prevent.
6. **Never invent CV content.** If the user wants a claim the resume does not make, the answer is to
   edit `cv.md`. This mirrors jobme's accuracy constraint into the conversation, where the user could
   otherwise talk the model past it.

Because `kokua skills install` reads only Kokua's own `skills/` directory, this skill has no install
command. jobme's README documents a one-line `cp -r`, and `check_application_setup` reports whether
it is in place. Bundling it in Kokua's `skills/` instead would make it installable and would not
violate Kokua's principles (that directory is content, outside the wheel), but it would put a skill
naming a toolset Kokua does not ship into Kokua's repo, which is inconsistent with the decision that
Kokua declares nothing about jobme.

## Testing

jobme has no test suite today. This adds `tests/test_kokua.py`, mock-only (no model, no network, no
keys), matching Kokua's own testing stance:

- the adapter marshals progress lines to `notify`
- both PDFs are copied into the downloads folder, with slug-prefixed names
- warnings from `run()` appear in the tool result
- the `""`-means-derive settings resolve under `$KOKUA_HOME`
- a `RunCancelled` becomes a plain message rather than an exception
- the entry point loads and `TOOLSET.name` equals its entry-point key

The last one is the failure Kokua's `test_registration.py` catches for Kokua's own toolsets and that
nothing would catch for a third party's.

`pipeline.run` is stubbed throughout. Nothing here exercises the pipeline itself, which stays covered
by end-to-end runs as it is today.

## Verification

One real run, whichever way the tests land:

1. Set `[jobme].model` to an installed Ollama model to avoid API cost.
2. Run a posting through Kokua's web UI.
3. Confirm progress lines stream during the run, the `/download/` links resolve, the page count and
   any warning appear in the reply, and `/stop` ends the spend rather than letting the thread run on.

## Out of scope

- A `/apply` Workflow. jobme's pipeline is a genuine multi-step turn strategy and Kokua's `Workflow`
  seam would show it better, but that means re-expressing the orchestration against
  `WorkflowContext` rather than calling `pipeline.run`. Worth revisiting once the toolset is in use.
- A background run with a status tool. The blocking call is enough while a run is something the user
  is waiting for.
- A `list_applications` tool. The filesystem and documents toolsets already reach the output folder.
- Slimming jobme's dependencies (weasyprint, Playwright) behind extras.
