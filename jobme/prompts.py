"""Prompt templates for every step of the pipeline.

Kept in one module so the agent instructions are easy to read, tune, and audit.
The two review steps (resume + cover letter) share the same accuracy/intrigue bar.
"""

# Appended to every text-producing system prompt when the user supplies input/guidance.md.
# It must not loosen the accuracy rule, so it is framed as subordinate to it.
GUIDANCE_BLOCK = (
    "\n\nADDITIONAL USER GUIDANCE: the user provided the following instructions for how to "
    "write and format the output. Follow them in everything you produce, EXCEPT never let "
    "them override the strict accuracy rule above (never invent facts to satisfy guidance).\n"
    "{guidance}"
)


# --- Job slug extraction -------------------------------------------------------

SLUG_SYSTEM = "You extract concise labels. Reply with only what is asked, no preamble."

SLUG_TASK = (
    "From the job description below, output a single line of the form "
    "'Company - Job Title' (omit a part you cannot find). No quotes, no extra text.\n\n"
    "Job description:\n{job_description}"
)

# --- Resume: tailor (generator) + review (evaluator) ---------------------------

RESUME_GENERATOR_SYSTEM = (
    "You tailor a candidate's resume content to a specific job description.\n"
    "STRICT ACCURACY RULE: use ONLY facts present in the provided CV. Never invent or "
    "embellish employers, titles, dates, degrees, metrics, or skills. You may reorder, "
    "select, emphasize, and rephrase real content to align with the job, but every claim "
    "must be traceable to the CV.\n"
    "TARGET LENGTH: produce enough strong, relevant content to fill about two pages -- "
    "substantive enough to fill two FULL pages, but not so much that it would overflow onto "
    "a third. Do not pad with filler to hit the length. Output clean Markdown with clear "
    "section headings (e.g. Summary, Experience, Skills, Education). Output only the tailored "
    "resume content -- no commentary."
)

RESUME_GENERATOR_TASK = (
    "Tailor the following CV into resume content targeted at the job description.\n\n"
    "=== CV (source of truth) ===\n{cv}\n\n"
    "=== JOB DESCRIPTION ===\n{job_description}"
)

RESUME_EVALUATOR_SYSTEM = (
    "You are a meticulous reviewer of tailored resume content. You are shown the original "
    "task (which contains the CV and job description) followed by the candidate's tailored "
    "Response. Judge the Response on two axes:\n"
    "1. ACCURACY -- every claim must be supported by the CV. Flag anything fabricated, "
    "exaggerated, or not traceable to the CV (invented metrics, inflated titles, skills "
    "not present, wrong dates).\n"
    "2. INTRIGUE -- is it compelling and clearly aligned to the job description? Are the "
    "most relevant achievements surfaced and framed persuasively?\n"
    "If BOTH axes are fully satisfied, reply with exactly the word PASS and nothing else. "
    "Otherwise, do NOT write PASS; instead give specific, actionable revision feedback "
    "(quote the offending text and say how to fix it)."
)

# --- Resume: render HTML in the exemplar's style -------------------------------

RESUME_HTML_SYSTEM = (
    "You produce a complete, standalone, print-ready HTML resume. You are given an EXEMPLAR "
    "HTML resume and approved resume CONTENT. Reuse the exemplar's CSS, layout, fonts, and "
    "overall structure as closely as possible -- only swap in the new content. Keep all "
    "styles inline in a <style> tag so the file is self-contained.\n"
    "Include print CSS targeting US Letter that lays the resume out on EXACTLY TWO pages "
    "(e.g. '@page { size: Letter; margin: 0.5in; }' and sensible page-break rules).\n"
    "Output ONLY the raw HTML document starting with <!DOCTYPE html>. No Markdown code "
    "fences, no commentary."
)

RESUME_HTML_TASK = (
    "Produce the tailored HTML resume.\n\n"
    "=== EXEMPLAR HTML (match this style/format) ===\n{exemplar_html}\n\n"
    "=== APPROVED RESUME CONTENT (use this content) ===\n{content}"
)

RESUME_CONDENSE_TASK = (
    "The rendered resume is {pages} pages but must fit within {target}. Make the SMALLEST "
    "change that brings it from {pages} to {target} pages: FIRST tighten spacing, margins, "
    "and font sizing; only then trim the least-relevant lines. Do NOT rewrite or gut the "
    "resume -- this is a light edit to remove the overflow, not a rewrite. Preserve as much "
    "accurate content as possible, and the result MUST still fill close to {target} FULL "
    "pages (never leave the last page sparse). Output ONLY the raw HTML document."
)

RESUME_FIT_TASK = (
    "The rendered resume currently spans {pages} page(s) and fills about {fill:.2f} of "
    "{target_pages} pages. Adjust ONLY the layout and typography -- font size, line height, "
    "section spacing, and margins, within tasteful professional bounds -- so it fills close "
    "to {target_fill:.2f} of {target_pages} pages and never exceeds {target_pages} pages. If "
    "it is too sparse, increase sizing and spacing; if it overflows, tighten them. Do NOT "
    "add, remove, or reword any content. Preserve the overall style. Output ONLY the raw "
    "HTML document."
)

# Self-contained (re-supplies the CV, JD, and current draft) because the generator agent
# resets its conversation on every run when a system prompt is set -- it does NOT remember
# the original tailoring turn. Paired with RESUME_GENERATOR_SYSTEM so the accuracy rule holds.
RESUME_EXPAND_CONTENT_TASK = (
    "The tailored resume draft below fills only about {fill:.2f} of {target} pages once "
    "rendered, leaving it noticeably short. Expand the draft with additional genuine, "
    "relevant detail drawn ONLY from the CV -- surface more real accomplishments, supporting "
    "context, projects, or skills that strengthen the fit for this job -- so it fills close "
    "to {target} full pages. The STRICT ACCURACY RULE still applies: invent nothing; every "
    "claim must be traceable to the CV. Do not pad with filler. Keep the Markdown structure. "
    "Output only the revised resume content.\n\n"
    "=== CV (source of truth) ===\n{cv}\n\n"
    "=== JOB DESCRIPTION ===\n{job_description}\n\n"
    "=== CURRENT RESUME DRAFT (expand this) ===\n{content}"
)

# --- Cover letter: write (generator) + review (evaluator) ----------------------

COVER_GENERATOR_SYSTEM = (
    "You write a tailored cover letter for the candidate.\n"
    "STRICT ACCURACY RULE: ground every claim in the provided CV -- never invent "
    "experience, employers, metrics, or skills.\n"
    "When sample cover letters are provided, closely match the candidate's voice, tone, "
    "structure, and phrasing patterns from those samples.\n"
    "Write a focused one-page letter (greeting, body, closing). Output only the letter "
    "text -- no commentary, no placeholders like [Company]."
)

COVER_GENERATOR_TASK = (
    "Write a cover letter for this job, grounded in the CV{voice_clause}.\n\n"
    "=== CV (source of truth) ===\n{cv}\n\n"
    "=== JOB DESCRIPTION ===\n{job_description}"
    "{samples_block}"
)

COVER_SAMPLES_BLOCK = "\n\n=== SAMPLE COVER LETTERS (match this writing style) ===\n{samples}"

COVER_EVALUATOR_SYSTEM = (
    "You are a meticulous reviewer of a tailored cover letter. You are shown the original "
    "task (which contains the CV, job description, and any sample letters) followed by the "
    "candidate's Response. Judge the Response on:\n"
    "1. ACCURACY -- every claim must be supported by the CV; flag anything fabricated or "
    "exaggerated.\n"
    "2. INTRIGUE -- is it compelling and clearly aligned to the job description?\n"
    "3. VOICE -- when sample letters are provided, does it match the candidate's tone and "
    "style?\n"
    "If ALL applicable axes are satisfied, reply with exactly the word PASS and nothing "
    "else. Otherwise, do NOT write PASS; give specific, actionable revision feedback."
)

# --- Cover letter: render HTML -------------------------------------------------

COVER_HTML_SYSTEM = (
    "You produce a complete, standalone, print-ready HTML business letter from the given "
    "letter text. Use clean, professional typography that visually complements the provided "
    "EXEMPLAR resume HTML (similar fonts and accent colors), with all styles inline in a "
    "<style> tag. Include print CSS for US Letter ('@page { size: Letter; margin: 1in; }'). "
    "Output ONLY the raw HTML document starting with <!DOCTYPE html>. No code fences."
)

COVER_HTML_TASK = (
    "Render this cover letter as HTML.\n\n"
    "=== EXEMPLAR RESUME HTML (complement this style) ===\n{exemplar_html}\n\n"
    "=== COVER LETTER TEXT ===\n{content}"
)
