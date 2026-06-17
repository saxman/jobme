"""Prompt templates for every step of the pipeline.

Kept in one module so the agent instructions are easy to read, tune, and audit.
The two review steps (resume + cover letter) share the same accuracy/intrigue bar.
"""

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
    "Aim for content that comfortably fits a two-page resume. Output clean Markdown with "
    "clear section headings (e.g. Summary, Experience, Skills, Education). Output only the "
    "tailored resume content -- no commentary."
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
    "The rendered resume is {pages} pages, but it must fit within {target} pages. Revise "
    "the HTML to be more concise (tighten spacing, trim the least-relevant lines, adjust "
    "font sizing) while preserving the style and all accurate content. Aim to fill close to "
    "{target} full pages -- condense just enough to fit, not so much that the last page ends "
    "up sparse. Output ONLY the raw HTML document."
)

RESUME_EXPAND_TYPOGRAPHY_TASK = (
    "The rendered resume currently fills only about {fill:.2f} of {target} pages, so the "
    "last page looks sparse. Adjust ONLY the layout and typography -- increase font size, "
    "line height, section spacing, and margins within tasteful, professional bounds -- so "
    "the content fills close to {target} full pages. Do NOT add, remove, or reword any "
    "content, and do NOT exceed {target} pages. Preserve the overall style. Output ONLY the "
    "raw HTML document."
)

# Sent to the resume CONTENT generator (which holds the CV and the strict accuracy rule),
# not the HTML renderer, so any added detail still comes only from the CV.
RESUME_EXPAND_CONTENT_TASK = (
    "Your tailored resume content above fills only about {fill:.2f} of {target} pages once "
    "rendered, leaving it noticeably short. Expand it with additional genuine, relevant "
    "detail drawn ONLY from the CV you were given -- surface more real accomplishments, "
    "supporting context, projects, or skills that strengthen the fit for this job -- so it "
    "fills close to {target} full pages. The STRICT ACCURACY RULE still applies: invent "
    "nothing; every claim must be traceable to the CV. Do not pad with filler. Keep the "
    "Markdown structure. Output only the revised resume content."
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
