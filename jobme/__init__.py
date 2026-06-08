"""jobme -- agentic resume & cover letter tailoring built on AIMU.

Given a markdown CV (content), an HTML resume (style/format), optional sample cover
letters (voice), and a job description, the pipeline tailors and reviews a resume and
cover letter for accuracy and intrigue, then renders send-ready PDFs.
"""

from .pipeline import run

__all__ = ["run"]
