---
name: job-application
description: Tailor the user's resume and cover letter to a specific job posting and produce send-ready PDFs. Use when the user shares a job posting, asks to apply somewhere, or asks for a resume tailored to a role.
license: Apache-2.0
compatibility: Requires the `jobme` toolset (pip install jobme, then declare "jobme" in the agent's tools).
metadata:
  author: jobme
---

# Tailoring a job application

A run costs real money and takes several minutes, and every document it produces is grounded in
the user's `cv.md`. Both facts drive the steps below: get the inputs right before spending, and
never put words in the user's mouth afterwards.

## Steps

1. **Get the whole posting, verbatim.** If the user pastes it, use exactly what they pasted. If
   they give a URL, fetch it first and show them what came back before going further. Never
   summarize a posting into `tailor_application`: the pipeline tailors against the text it is
   given, so a summary quietly produces a worse resume and nothing about the result looks wrong.

2. **Check the setup before the first run of a session.** Call `check_application_setup`. It is
   read-only and fast, and it catches a missing `cv.md`, an uninstalled browser, or an absent API
   key before several minutes of billed calls rather than after. Skip it only if a run already
   succeeded in this conversation.

3. **Confirm before running.** Tell the user the company and title you read off the posting, say
   the run takes a few minutes and costs money, and wait for them to agree. Kokua may also ask
   them to approve the tool call; that is a backstop, not a substitute for setting the
   expectation.

4. **Call `tailor_application`** with the posting's full text, and pass `name` as
   `"Company - Title"` whenever you can read both off the posting. That label names the output
   folder, which is what makes an application findable weeks later.

5. **Report every warning verbatim.** The tool returns page count, fill, download links, and any
   warnings. A low-fill warning means the CV does not contain enough relevant material for a
   full two-page resume. Say that plainly. Rewording it into "looks good" is the failure this
   step exists to prevent.

6. **Never write resume or cover-letter content yourself.** jobme's guarantee is that nothing
   appears in either document that the CV does not support. If the user wants a claim the resume
   does not make, the answer is to add it to `cv.md` and run again, not to draft a sentence for
   them.

## Notes

- The PDFs are copied into Kokua's downloads folder, so the `/download/...` links work in the web
  UI. The tool also gives the full path, which is what a terminal user needs.
- Inputs live in the directory `check_application_setup` names, `[jobme] input_dir` in
  `config.toml`. `cv.md` is the content source of truth and `resume.html` is the style template.
  `cover_letter*.txt` files are optional voice samples; `guidance.md` is optional free-form
  guidance applied to every generation step.
- If a run fails, call `check_application_setup` before retrying. Retrying blind spends the same
  money on the same failure.
