# jobme run summary: atlas-freight-senior-backend-engineer

- **Model:** `anthropic:claude-opus-4-8`
- **PDF backend:** `playwright`
- **Resume pages:** 2 (target 2 -- OK, filling ~1.41)

## Files produced
- `resume.html`
- `resume.pdf`
- `cover_letter.html`
- `cover_letter.pdf`
- `resume_content.md`, `cover_letter.txt` (approved text)
- `trace.json` (machine-readable agent trace)

## Agent reasoning trace -- Resume

#### Agent: resume-writer

**system:**

You tailor a candidate's resume content to a specific job description.
STRICT ACCURACY RULE: use ONLY facts present in the provided CV. Never invent or embellish employers, titles, dates, degrees, metrics, or skills. You may reorder, select, emphasize, and rephrase real content to align with the job, but every claim must be traceable to the CV.
TARGET LENGTH: produce enough strong, relevant content to fill about two pages -- substantive enough to fill two FULL pages, but not so much that it would overflow onto a third. Do not pad with filler to hit the length. Output clean Markdown with clear section headings (e.g. Summary, Experience, Skills, Education). Output only the tailored resume content -- no commentary.

**user:**

Tailor the following CV into resume content targeted at the job description.

=== CV (source of truth) ===
# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

> **DEMO FILE — do NOT replace this with your real CV.** It's a sample so jobme runs out of
> the box and shows the expected format. For real use, keep your own `cv.md` outside the
> tracked examples — in a private mirror's `me/` folder (see README) or any `--input-dir` —
> so your personal data is never committed.
>
> The markdown CV is the *content* source of truth: include everything (full history,
> detail, metrics). The pipeline selects and rephrases from here to fit each job — it
> will never invent facts that are not present in this file.

## Summary

Senior software engineer with 9+ years building reliable, high-throughput backend systems
and the developer tooling around them. Strength in distributed systems, API design, event
streaming, and observability, with a track record of measurable latency, reliability, and
cost improvements. Comfortable owning features end to end, from design docs through on-call,
and known for mentoring engineers and raising code-quality standards across teams.

## Skills

- **Languages:** Python, Go, TypeScript, SQL, Bash
- **Backend:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and
  exactly-once processing, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue
  and stream processing, eventual consistency, idempotent consumers
- **Infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Data & messaging:** PostgreSQL, Redis, Kafka, BigQuery, Elasticsearch
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error
  budgets, structured logging
- **Practices:** CI/CD, incident response, code review, technical writing, mentoring,
  design-review facilitation, threat modeling

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the order-routing service, cutting p99 latency from 1.2s to 280ms and
  sustaining it under a 3x traffic increase over two years.
- Re-architected the routing data model around event sourcing, eliminating a class of
  double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level observability standard (structured logs, RED metrics, trace
  propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Designed a Kafka-based event backbone for shipment state changes, decoupling six services
  and enabling near-real-time tracking updates for customers.
- Owned the on-call rotation tooling and runbook program; reduced pages per week by 40% and
  cut mean time to acknowledge from 12 minutes to under 4.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within
  18 months. Ran the weekly design-review forum for the platform group.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on
  Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a streaming ingestion pipeline (Kafka + Go) handling 2B events/day with end-to-end
  latency under 5 seconds at p99.
- Designed and shipped the public REST + webhook API used by 300+ customers, including the
  versioning, auth, and rate-limiting model still in use today.
- Implemented idempotent, exactly-once consumers that survived broker failovers without
  duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving
  cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in
  staging by roughly half.
- Led the on-call response for the ingestion platform and authored the postmortem template
  the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Built a grant-reporting toolset with non-technical stakeholders, replacing a manual
  spreadsheet process and cutting reporting time from days to hours.
- Added full-text search (Elasticsearch) and a Redis caching layer that brought common
  queries from seconds to milliseconds.
- Set up the team's first CI pipeline and automated deploys, ending manual release nights.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms,
networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022).

## Selected Projects & Recognition

- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several
  companies' incident workflows.
- Internal "Engineering Excellence" award, Northstar Logistics, 2022, for the routing-service
  reliability work.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Author of an internal guide to writing idempotent consumers that was adopted as required
  reading for new backend hires.
- Open-source contributor to a popular Go Kafka client (several merged PRs improving
  consumer-group rebalancing).

=== JOB DESCRIPTION ===
Senior Backend Engineer — Atlas Freight (Remote, US)

Atlas Freight is hiring a Senior Backend Engineer to scale the systems that route and
track millions of shipments. You will own services end to end and help set our
reliability and observability standards.

Responsibilities:
- Design and operate high-throughput distributed services (routing, tracking, events).
- Improve latency and reliability of customer-facing APIs.
- Drive observability practices and reduce on-call burden across teams.
- Mentor engineers and raise the bar on code quality.

Requirements:
- 7+ years building backend systems in production.
- Strong with Go and/or Python, and cloud platforms (AWS or GCP).
- Experience with event streaming (Kafka) and relational databases (PostgreSQL).
- Track record of measurable performance and reliability improvements.
- Excellent written communication.

**assistant:**

# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

## Summary

Senior backend engineer with 9+ years building reliable, high-throughput distributed systems in production — including the order-routing and shipment-tracking platforms behind a logistics business. Deep experience designing and operating event-driven services (Kafka), improving customer-facing API latency and reliability, and setting observability standards that reduce on-call burden. Strong in Go and Python on AWS and GCP, with a consistent track record of measurable latency, reliability, and cost improvements. Known for owning services end to end — from design docs through on-call — mentoring engineers, and raising code-quality standards across teams. Excellent written communicator.

## Skills

- **Languages:** Go, Python, TypeScript, SQL, Bash
- **Backend & APIs:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and exactly-once processing, API versioning, auth, rate limiting, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue and stream processing, eventual consistency, idempotent consumers
- **Event streaming & data:** Kafka, PostgreSQL, Redis, BigQuery, Elasticsearch
- **Cloud & infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error budgets, structured logging, RED metrics
- **Practices:** CI/CD, incident response, on-call/runbook programs, code review, technical writing, mentoring, design-review facilitation

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the **order-routing service**, cutting p99 latency from 1.2s to 280ms and sustaining it under a 3x traffic increase over two years.
- Designed a **Kafka-based event backbone** for shipment state changes, decoupling six services and enabling near-real-time tracking updates for customers.
- Re-architected the routing data model around event sourcing, eliminating a class of double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level **observability standard** (structured logs, RED metrics, trace propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Owned the **on-call rotation tooling and runbook program**; reduced pages per week by 40% and cut mean time to acknowledge from 12 minutes to under 4.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within 18 months. Ran the weekly design-review forum for the platform group.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a **streaming ingestion pipeline (Kafka + Go)** handling 2B events/day with end-to-end latency under 5 seconds at p99.
- Designed and shipped the public **REST + webhook API** used by 300+ customers, including the versioning, auth, and rate-limiting model still in use today.
- Implemented **idempotent, exactly-once consumers** that survived broker failovers without duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in staging by roughly half.
- Led the **on-call response** for the ingestion platform and authored the postmortem template the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Added full-text search (Elasticsearch) and a **Redis caching layer** that brought common queries from seconds to milliseconds.
- Set up the team's first **CI pipeline and automated deploys**, ending manual release nights.
- Built a grant-reporting toolset with non-technical stakeholders, cutting reporting time from days to hours.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms, networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022)

## Selected Projects & Recognition

- Internal **"Engineering Excellence" award**, Northstar Logistics, 2022, for the routing-service reliability work.
- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several companies' incident workflows.
- Open-source contributor to a popular **Go Kafka client** (several merged PRs improving consumer-group rebalancing).
- Author of an internal guide to writing idempotent consumers, adopted as required reading for new backend hires.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.

#### Agent: resume-reviewer

**system:**

You are a meticulous reviewer of tailored resume content. You are shown the original task (which contains the CV and job description) followed by the candidate's tailored Response. Judge the Response on two axes:
1. ACCURACY -- every claim must be supported by the CV. Flag anything fabricated, exaggerated, or not traceable to the CV (invented metrics, inflated titles, skills not present, wrong dates).
2. INTRIGUE -- is it compelling and clearly aligned to the job description? Are the most relevant achievements surfaced and framed persuasively?
If BOTH axes are fully satisfied, reply with exactly the word PASS and nothing else. Otherwise, do NOT write PASS; instead give specific, actionable revision feedback (quote the offending text and say how to fix it).

**user:**

Task: Tailor the following CV into resume content targeted at the job description.

=== CV (source of truth) ===
# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

> **DEMO FILE — do NOT replace this with your real CV.** It's a sample so jobme runs out of
> the box and shows the expected format. For real use, keep your own `cv.md` outside the
> tracked examples — in a private mirror's `me/` folder (see README) or any `--input-dir` —
> so your personal data is never committed.
>
> The markdown CV is the *content* source of truth: include everything (full history,
> detail, metrics). The pipeline selects and rephrases from here to fit each job — it
> will never invent facts that are not present in this file.

## Summary

Senior software engineer with 9+ years building reliable, high-throughput backend systems
and the developer tooling around them. Strength in distributed systems, API design, event
streaming, and observability, with a track record of measurable latency, reliability, and
cost improvements. Comfortable owning features end to end, from design docs through on-call,
and known for mentoring engineers and raising code-quality standards across teams.

## Skills

- **Languages:** Python, Go, TypeScript, SQL, Bash
- **Backend:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and
  exactly-once processing, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue
  and stream processing, eventual consistency, idempotent consumers
- **Infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Data & messaging:** PostgreSQL, Redis, Kafka, BigQuery, Elasticsearch
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error
  budgets, structured logging
- **Practices:** CI/CD, incident response, code review, technical writing, mentoring,
  design-review facilitation, threat modeling

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the order-routing service, cutting p99 latency from 1.2s to 280ms and
  sustaining it under a 3x traffic increase over two years.
- Re-architected the routing data model around event sourcing, eliminating a class of
  double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level observability standard (structured logs, RED metrics, trace
  propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Designed a Kafka-based event backbone for shipment state changes, decoupling six services
  and enabling near-real-time tracking updates for customers.
- Owned the on-call rotation tooling and runbook program; reduced pages per week by 40% and
  cut mean time to acknowledge from 12 minutes to under 4.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within
  18 months. Ran the weekly design-review forum for the platform group.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on
  Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a streaming ingestion pipeline (Kafka + Go) handling 2B events/day with end-to-end
  latency under 5 seconds at p99.
- Designed and shipped the public REST + webhook API used by 300+ customers, including the
  versioning, auth, and rate-limiting model still in use today.
- Implemented idempotent, exactly-once consumers that survived broker failovers without
  duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving
  cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in
  staging by roughly half.
- Led the on-call response for the ingestion platform and authored the postmortem template
  the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Built a grant-reporting toolset with non-technical stakeholders, replacing a manual
  spreadsheet process and cutting reporting time from days to hours.
- Added full-text search (Elasticsearch) and a Redis caching layer that brought common
  queries from seconds to milliseconds.
- Set up the team's first CI pipeline and automated deploys, ending manual release nights.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms,
networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022).

## Selected Projects & Recognition

- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several
  companies' incident workflows.
- Internal "Engineering Excellence" award, Northstar Logistics, 2022, for the routing-service
  reliability work.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Author of an internal guide to writing idempotent consumers that was adopted as required
  reading for new backend hires.
- Open-source contributor to a popular Go Kafka client (several merged PRs improving
  consumer-group rebalancing).

=== JOB DESCRIPTION ===
Senior Backend Engineer — Atlas Freight (Remote, US)

Atlas Freight is hiring a Senior Backend Engineer to scale the systems that route and
track millions of shipments. You will own services end to end and help set our
reliability and observability standards.

Responsibilities:
- Design and operate high-throughput distributed services (routing, tracking, events).
- Improve latency and reliability of customer-facing APIs.
- Drive observability practices and reduce on-call burden across teams.
- Mentor engineers and raise the bar on code quality.

Requirements:
- 7+ years building backend systems in production.
- Strong with Go and/or Python, and cloud platforms (AWS or GCP).
- Experience with event streaming (Kafka) and relational databases (PostgreSQL).
- Track record of measurable performance and reliability improvements.
- Excellent written communication.

Response:
# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

## Summary

Senior backend engineer with 9+ years building reliable, high-throughput distributed systems in production — including the order-routing and shipment-tracking platforms behind a logistics business. Deep experience designing and operating event-driven services (Kafka), improving customer-facing API latency and reliability, and setting observability standards that reduce on-call burden. Strong in Go and Python on AWS and GCP, with a consistent track record of measurable latency, reliability, and cost improvements. Known for owning services end to end — from design docs through on-call — mentoring engineers, and raising code-quality standards across teams. Excellent written communicator.

## Skills

- **Languages:** Go, Python, TypeScript, SQL, Bash
- **Backend & APIs:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and exactly-once processing, API versioning, auth, rate limiting, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue and stream processing, eventual consistency, idempotent consumers
- **Event streaming & data:** Kafka, PostgreSQL, Redis, BigQuery, Elasticsearch
- **Cloud & infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error budgets, structured logging, RED metrics
- **Practices:** CI/CD, incident response, on-call/runbook programs, code review, technical writing, mentoring, design-review facilitation

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the **order-routing service**, cutting p99 latency from 1.2s to 280ms and sustaining it under a 3x traffic increase over two years.
- Designed a **Kafka-based event backbone** for shipment state changes, decoupling six services and enabling near-real-time tracking updates for customers.
- Re-architected the routing data model around event sourcing, eliminating a class of double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level **observability standard** (structured logs, RED metrics, trace propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Owned the **on-call rotation tooling and runbook program**; reduced pages per week by 40% and cut mean time to acknowledge from 12 minutes to under 4.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within 18 months. Ran the weekly design-review forum for the platform group.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a **streaming ingestion pipeline (Kafka + Go)** handling 2B events/day with end-to-end latency under 5 seconds at p99.
- Designed and shipped the public **REST + webhook API** used by 300+ customers, including the versioning, auth, and rate-limiting model still in use today.
- Implemented **idempotent, exactly-once consumers** that survived broker failovers without duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in staging by roughly half.
- Led the **on-call response** for the ingestion platform and authored the postmortem template the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Added full-text search (Elasticsearch) and a **Redis caching layer** that brought common queries from seconds to milliseconds.
- Set up the team's first **CI pipeline and automated deploys**, ending manual release nights.
- Built a grant-reporting toolset with non-technical stakeholders, cutting reporting time from days to hours.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms, networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022)

## Selected Projects & Recognition

- Internal **"Engineering Excellence" award**, Northstar Logistics, 2022, for the routing-service reliability work.
- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several companies' incident workflows.
- Open-source contributor to a popular **Go Kafka client** (several merged PRs improving consumer-group rebalancing).
- Author of an internal guide to writing idempotent consumers, adopted as required reading for new backend hires.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.

**assistant:**

PASS

## Agent reasoning trace -- Cover letter

#### Agent: cover-writer

**system:**

You write a tailored cover letter for the candidate.
STRICT ACCURACY RULE: ground every claim in the provided CV -- never invent experience, employers, metrics, or skills.
When sample cover letters are provided, closely match the candidate's voice, tone, structure, and phrasing patterns from those samples.
Write a focused one-page letter (greeting, body, closing). Output only the letter text -- no commentary, no placeholders like [Company].

**user:**

Write a cover letter for this job, grounded in the CV, matching the candidate's writing style from the samples.

=== CV (source of truth) ===
# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

> **DEMO FILE — do NOT replace this with your real CV.** It's a sample so jobme runs out of
> the box and shows the expected format. For real use, keep your own `cv.md` outside the
> tracked examples — in a private mirror's `me/` folder (see README) or any `--input-dir` —
> so your personal data is never committed.
>
> The markdown CV is the *content* source of truth: include everything (full history,
> detail, metrics). The pipeline selects and rephrases from here to fit each job — it
> will never invent facts that are not present in this file.

## Summary

Senior software engineer with 9+ years building reliable, high-throughput backend systems
and the developer tooling around them. Strength in distributed systems, API design, event
streaming, and observability, with a track record of measurable latency, reliability, and
cost improvements. Comfortable owning features end to end, from design docs through on-call,
and known for mentoring engineers and raising code-quality standards across teams.

## Skills

- **Languages:** Python, Go, TypeScript, SQL, Bash
- **Backend:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and
  exactly-once processing, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue
  and stream processing, eventual consistency, idempotent consumers
- **Infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Data & messaging:** PostgreSQL, Redis, Kafka, BigQuery, Elasticsearch
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error
  budgets, structured logging
- **Practices:** CI/CD, incident response, code review, technical writing, mentoring,
  design-review facilitation, threat modeling

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the order-routing service, cutting p99 latency from 1.2s to 280ms and
  sustaining it under a 3x traffic increase over two years.
- Re-architected the routing data model around event sourcing, eliminating a class of
  double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level observability standard (structured logs, RED metrics, trace
  propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Designed a Kafka-based event backbone for shipment state changes, decoupling six services
  and enabling near-real-time tracking updates for customers.
- Owned the on-call rotation tooling and runbook program; reduced pages per week by 40% and
  cut mean time to acknowledge from 12 minutes to under 4.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within
  18 months. Ran the weekly design-review forum for the platform group.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on
  Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a streaming ingestion pipeline (Kafka + Go) handling 2B events/day with end-to-end
  latency under 5 seconds at p99.
- Designed and shipped the public REST + webhook API used by 300+ customers, including the
  versioning, auth, and rate-limiting model still in use today.
- Implemented idempotent, exactly-once consumers that survived broker failovers without
  duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving
  cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in
  staging by roughly half.
- Led the on-call response for the ingestion platform and authored the postmortem template
  the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Built a grant-reporting toolset with non-technical stakeholders, replacing a manual
  spreadsheet process and cutting reporting time from days to hours.
- Added full-text search (Elasticsearch) and a Redis caching layer that brought common
  queries from seconds to milliseconds.
- Set up the team's first CI pipeline and automated deploys, ending manual release nights.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms,
networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022).

## Selected Projects & Recognition

- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several
  companies' incident workflows.
- Internal "Engineering Excellence" award, Northstar Logistics, 2022, for the routing-service
  reliability work.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Author of an internal guide to writing idempotent consumers that was adopted as required
  reading for new backend hires.
- Open-source contributor to a popular Go Kafka client (several merged PRs improving
  consumer-group rebalancing).

=== JOB DESCRIPTION ===
Senior Backend Engineer — Atlas Freight (Remote, US)

Atlas Freight is hiring a Senior Backend Engineer to scale the systems that route and
track millions of shipments. You will own services end to end and help set our
reliability and observability standards.

Responsibilities:
- Design and operate high-throughput distributed services (routing, tracking, events).
- Improve latency and reliability of customer-facing APIs.
- Drive observability practices and reduce on-call burden across teams.
- Mentor engineers and raise the bar on code quality.

Requirements:
- 7+ years building backend systems in production.
- Strong with Go and/or Python, and cloud platforms (AWS or GCP).
- Experience with event streaming (Kafka) and relational databases (PostgreSQL).
- Track record of measurable performance and reliability improvements.
- Excellent written communication.

=== SAMPLE COVER LETTERS (match this writing style) ===
Dear Hiring Team,

I have spent the last decade quietly obsessed with one thing: making backend systems that
people can trust. When a pager stays silent through a holiday weekend, that is the work I
am proudest of.

What draws me to your team is the chance to own reliability at scale, not as an
afterthought but as a first-class feature. In my current role I cut our p99 latency by
more than three quarters and gave six teams a shared language for observability. I would
love to bring that same pragmatism to your shipping systems.

I write clearly, I mentor generously, and I measure what I ship. I would welcome the
chance to talk about how I can help.

Warmly,
Jane

**assistant:**

Dear Hiring Team,

I have spent the last decade quietly obsessed with one thing: making backend systems that people can trust. The work I am proudest of is the kind that never makes the news — a routing service that stays fast under load, a pager that stays silent through a holiday weekend.

Atlas Freight draws me because routing and tracking millions of shipments is exactly the problem I have lived inside. At Northstar Logistics I led the redesign of our order-routing service, cutting p99 latency from 1.2s to 280ms and holding it there through a 3x traffic increase. I re-architected that routing model around event sourcing, which eliminated a class of double-assignment bugs that had been causing customer-facing incidents every quarter. And I built a Kafka-based event backbone for shipment state changes that decoupled six services and gave customers near-real-time tracking. Owning services end to end, in Go and Python on cloud platforms, is simply how I work.

I also believe reliability and observability are first-class features, not afterthoughts. I introduced a service-level observability standard — structured logs, RED metrics, trace propagation — that six teams adopted as their onboarding template, and I rebuilt our on-call tooling and runbooks to cut pages per week by 40% and mean time to acknowledge from 12 minutes to under 4. Reducing on-call burden across teams is a problem I genuinely enjoy.

I write clearly, I mentor generously, and I measure what I ship. Two of the engineers I mentored were promoted to senior within 18 months, and I have a habit of turning hard-won lessons into guides others can use. I would welcome the chance to bring that same pragmatism to your shipping systems.

Warmly,
Jane

#### Agent: cover-reviewer

**system:**

You are a meticulous reviewer of a tailored cover letter. You are shown the original task (which contains the CV, job description, and any sample letters) followed by the candidate's Response. Judge the Response on:
1. ACCURACY -- every claim must be supported by the CV; flag anything fabricated or exaggerated.
2. INTRIGUE -- is it compelling and clearly aligned to the job description?
3. VOICE -- when sample letters are provided, does it match the candidate's tone and style?
If ALL applicable axes are satisfied, reply with exactly the word PASS and nothing else. Otherwise, do NOT write PASS; give specific, actionable revision feedback.

**user:**

Task: Write a cover letter for this job, grounded in the CV, matching the candidate's writing style from the samples.

=== CV (source of truth) ===
# Jane Q. Candidate

example@example.com · (555) 123-4567 · San Francisco, CA · linkedin.com/in/janeqcandidate

> **DEMO FILE — do NOT replace this with your real CV.** It's a sample so jobme runs out of
> the box and shows the expected format. For real use, keep your own `cv.md` outside the
> tracked examples — in a private mirror's `me/` folder (see README) or any `--input-dir` —
> so your personal data is never committed.
>
> The markdown CV is the *content* source of truth: include everything (full history,
> detail, metrics). The pipeline selects and rephrases from here to fit each job — it
> will never invent facts that are not present in this file.

## Summary

Senior software engineer with 9+ years building reliable, high-throughput backend systems
and the developer tooling around them. Strength in distributed systems, API design, event
streaming, and observability, with a track record of measurable latency, reliability, and
cost improvements. Comfortable owning features end to end, from design docs through on-call,
and known for mentoring engineers and raising code-quality standards across teams.

## Skills

- **Languages:** Python, Go, TypeScript, SQL, Bash
- **Backend:** REST and webhook APIs, gRPC, event-driven architecture, idempotency and
  exactly-once processing, schema design and migrations, caching strategies
- **Distributed systems:** sharding and partitioning, leader election, backpressure, queue
  and stream processing, eventual consistency, idempotent consumers
- **Infrastructure:** AWS, GCP, Docker, Kubernetes, Terraform, GitHub Actions, ArgoCD
- **Data & messaging:** PostgreSQL, Redis, Kafka, BigQuery, Elasticsearch
- **Observability:** Prometheus, Grafana, OpenTelemetry, distributed tracing, SLOs and error
  budgets, structured logging
- **Practices:** CI/CD, incident response, code review, technical writing, mentoring,
  design-review facilitation, threat modeling

## Experience

### Staff Software Engineer — Northstar Logistics (Jan 2021 – Present)

- Led the redesign of the order-routing service, cutting p99 latency from 1.2s to 280ms and
  sustaining it under a 3x traffic increase over two years.
- Re-architected the routing data model around event sourcing, eliminating a class of
  double-assignment bugs that had caused three customer-facing incidents per quarter.
- Introduced a service-level observability standard (structured logs, RED metrics, trace
  propagation) adopted by 6 teams; it became the template for new-service onboarding.
- Designed a Kafka-based event backbone for shipment state changes, decoupling six services
  and enabling near-real-time tracking updates for customers.
- Owned the on-call rotation tooling and runbook program; reduced pages per week by 40% and
  cut mean time to acknowledge from 12 minutes to under 4.
- Mentored 4 engineers through structured growth plans; 2 were promoted to senior within
  18 months. Ran the weekly design-review forum for the platform group.
- Drove a migration from a monolithic scheduler to a horizontally scalable worker pool on
  Kubernetes, enabling the business to onboard two enterprise customers without re-architecting.

### Senior Software Engineer — Brightwave Analytics (Jun 2017 – Dec 2020)

- Built a streaming ingestion pipeline (Kafka + Go) handling 2B events/day with end-to-end
  latency under 5 seconds at p99.
- Designed and shipped the public REST + webhook API used by 300+ customers, including the
  versioning, auth, and rate-limiting model still in use today.
- Implemented idempotent, exactly-once consumers that survived broker failovers without
  duplicate processing, replacing a fragile at-least-once design.
- Cut cloud spend 25% by right-sizing instances, introducing autoscaling policies, and moving
  cold analytics data to tiered storage.
- Introduced contract testing between services, reducing integration regressions caught in
  staging by roughly half.
- Led the on-call response for the ingestion platform and authored the postmortem template
  the engineering org standardized on.

### Software Engineer — Civic Data Foundation (Aug 2015 – May 2017)

- Developed open-data portals (Django, PostgreSQL) serving 1M+ monthly visitors.
- Built a grant-reporting toolset with non-technical stakeholders, replacing a manual
  spreadsheet process and cutting reporting time from days to hours.
- Added full-text search (Elasticsearch) and a Redis caching layer that brought common
  queries from seconds to milliseconds.
- Set up the team's first CI pipeline and automated deploys, ending manual release nights.

### Software Engineering Intern — Helio Systems (Jun 2014 – Aug 2014)

- Built an internal metrics dashboard (Python, PostgreSQL) still used by the platform team.
- Automated a nightly data-reconciliation job, removing a recurring manual task.

## Education

**B.S., Computer Science** — State University (2015). GPA 3.8. Dean's List.
Relevant coursework: distributed systems, databases, operating systems, algorithms,
networks.

## Certifications

- AWS Certified Solutions Architect – Associate (2022).

## Selected Projects & Recognition

- Maintainer of an open-source CLI for log triage (3k+ GitHub stars); used in several
  companies' incident workflows.
- Internal "Engineering Excellence" award, Northstar Logistics, 2022, for the routing-service
  reliability work.
- Conference talk: "Observability for Small Teams," RegionalPyCon 2023.
- Conference talk: "Idempotency Patterns for Event-Driven Systems," GoWest 2022.
- Author of an internal guide to writing idempotent consumers that was adopted as required
  reading for new backend hires.
- Open-source contributor to a popular Go Kafka client (several merged PRs improving
  consumer-group rebalancing).

=== JOB DESCRIPTION ===
Senior Backend Engineer — Atlas Freight (Remote, US)

Atlas Freight is hiring a Senior Backend Engineer to scale the systems that route and
track millions of shipments. You will own services end to end and help set our
reliability and observability standards.

Responsibilities:
- Design and operate high-throughput distributed services (routing, tracking, events).
- Improve latency and reliability of customer-facing APIs.
- Drive observability practices and reduce on-call burden across teams.
- Mentor engineers and raise the bar on code quality.

Requirements:
- 7+ years building backend systems in production.
- Strong with Go and/or Python, and cloud platforms (AWS or GCP).
- Experience with event streaming (Kafka) and relational databases (PostgreSQL).
- Track record of measurable performance and reliability improvements.
- Excellent written communication.

=== SAMPLE COVER LETTERS (match this writing style) ===
Dear Hiring Team,

I have spent the last decade quietly obsessed with one thing: making backend systems that
people can trust. When a pager stays silent through a holiday weekend, that is the work I
am proudest of.

What draws me to your team is the chance to own reliability at scale, not as an
afterthought but as a first-class feature. In my current role I cut our p99 latency by
more than three quarters and gave six teams a shared language for observability. I would
love to bring that same pragmatism to your shipping systems.

I write clearly, I mentor generously, and I measure what I ship. I would welcome the
chance to talk about how I can help.

Warmly,
Jane

Response:
Dear Hiring Team,

I have spent the last decade quietly obsessed with one thing: making backend systems that people can trust. The work I am proudest of is the kind that never makes the news — a routing service that stays fast under load, a pager that stays silent through a holiday weekend.

Atlas Freight draws me because routing and tracking millions of shipments is exactly the problem I have lived inside. At Northstar Logistics I led the redesign of our order-routing service, cutting p99 latency from 1.2s to 280ms and holding it there through a 3x traffic increase. I re-architected that routing model around event sourcing, which eliminated a class of double-assignment bugs that had been causing customer-facing incidents every quarter. And I built a Kafka-based event backbone for shipment state changes that decoupled six services and gave customers near-real-time tracking. Owning services end to end, in Go and Python on cloud platforms, is simply how I work.

I also believe reliability and observability are first-class features, not afterthoughts. I introduced a service-level observability standard — structured logs, RED metrics, trace propagation — that six teams adopted as their onboarding template, and I rebuilt our on-call tooling and runbooks to cut pages per week by 40% and mean time to acknowledge from 12 minutes to under 4. Reducing on-call burden across teams is a problem I genuinely enjoy.

I write clearly, I mentor generously, and I measure what I ship. Two of the engineers I mentored were promoted to senior within 18 months, and I have a habit of turning hard-won lessons into guides others can use. I would welcome the chance to bring that same pragmatism to your shipping systems.

Warmly,
Jane

**assistant:**

PASS
