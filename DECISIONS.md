Architectural Trade-offs
1. The "Umpire" Strategy (Deterministic vs. Generative)
Decision: We strictly separate data validation from creative generation.

Rationale: To prevent "AI Echo Chambers," LLMs are banned from the Silver (Transformation) layer.

Trade-off: This requires more complex SQL in dbt to calculate "Heat" and "Confidence" scores manually, but it ensures that the prompts generated in the Gold layer are grounded in cross-platform reality.

2. Quota Guard & Circuit Breakers
Decision: Hard-coded unit caps (e.g., 9,000 units for YouTube) in the ingestion worker.

Rationale: Since this runs on GitHub Actions/Neon, an unoptimized loop could deplete free-tier API keys in minutes.

Implementation: We use a BaseScraper abstract class to enforce a standardized lifecycle and centralized logging for observability.

3. Storage: Why Neon Postgres?
Decision: Leveraging Neon’s "Branching" for CI/CD.

Rationale: Traditional data warehouses (Snowflake/BigQuery) are overkill for this scale and carry high idle costs.

Trade-off: Neon allows us to treat the database like code—ephemeral branches for every PR mean we never test against "dirty" production data.

4. dbt Materialization Strategy
Decision:

Staging: Views (to minimize storage and stay agile).

Intermediate: Tables (to cache complex cross-platform joins).

Marts: Incremental (to keep Neon compute hours low by only processing new trends).
