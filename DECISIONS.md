## 1. Why this ingestion strategy over the obvious alternative?
The live demo uses Jobicy's public JSON API with Remote OK's public JSON API as a fallback, plus a controlled sandbox for deterministic failure demonstrations. This is safer and more maintainable than automating LinkedIn, Indeed, Naukri, or Wellfound, where authentication, CAPTCHA, anti-bot controls, and terms restrict automated collection. Public APIs provide explicit structured data, predictable portability, and a clear operational boundary while still exercising adapters, validation, normalization, deduplication, persistence, and health monitoring.

The detection surface of a protected platform includes headless-browser fingerprints, unusual request timing, missing or inconsistent headers, repeated navigation patterns, IP reputation, account behavior, CAPTCHA triggers, and sudden schema or markup changes. This project does not attempt to defeat those controls. It accounts for ordinary reliability concerns by using a descriptive HTTP client, conservative pacing, bounded retries, 429 handling, response validation, circuit breaking, and source fallback. It does not rotate identities, proxies, accounts, or fingerprints to evade detection.

The ingestion strategy is adapter-based: one scheduled request every configured interval, with a minimum request interval and bounded exponential backoff for transient failures. A 403 or explicit block is treated as a stop signal, not as a reason to increase retries. If the primary public source fails, the fallback adapter is tried; the sandbox can be selected as a deterministic last-resort demo source.

If a source changes its schema, response validation rejects the unexpected shape, records an ingestion error, updates source health, and prevents corrupted records from being saved. Empty responses are recorded as successful empty runs rather than silently treated as new jobs. Deduplication prevents repeated listings from inflating stored data.

The technical and personal stopping line is explicit: no CAPTCHA bypass, authentication bypass, access-control circumvention, fingerprint defeat, identity rotation, or aggressive retrying against a blocked source. We stop using a source when it blocks or disallows automation and continue only through a permitted public source or controlled sandbox.

## 2. One trade-off made under the time limit
I chose PostgreSQL plus a lightweight in-process scheduler instead of introducing a distributed queue such as Kafka or Celery. That keeps the MVP understandable, testable, and fast to deploy while remaining focused on ingestion resilience rather than distributed infrastructure. A full-week extension would likely add a durable queue, worker pool, and more advanced retry and observability layers.

## 3. AI usage
AI was used for architecture brainstorming, code generation assistance, debugging support, and documentation drafting. I reviewed, modified, tested, and verified the generated code before finishing this project. All generated code was reviewed, tested, modified, and verified by me.
