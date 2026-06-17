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