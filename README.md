# Data Quality & Governance Platform

A lightweight, testable reference implementation for data contracts, quality gates and governance metadata in a modern financial data platform. The repository demonstrates how engineering teams can make quality checks executable and auditable instead of relying only on documentation.

> Portfolio project with synthetic data and generic controls. No proprietary policies or employer code are represented.

## Architecture

```text
Source dataset
    |
    v
Contract validation -----> rejected records / quality report
    |
    v
Trusted dataset
    |
    +----> SQL/dbt-style assertions
    |
    +----> governance catalog metadata
    |
    +----> analytics / ML consumers
```

## Capabilities

- YAML data contracts describing schema, nullability and business rules.
- Executable field-level schema checks for declared column presence, string/number types and nullability; schema violations are critical quality-gate failures.
- Python quality engine for completeness, uniqueness, accepted values and numeric bounds.
- PII classification metadata separated from actual data values.
- SQL assertions suitable for warehouse/dbt adaptation.
- Quality score output that can be integrated into Airflow, Glue, Databricks or CI/CD gates.
- Unit tests for schema enforcement, rule behavior and failure reporting.

## Layout

```text
contracts/transactions.yml       Dataset contract and governance metadata
src/quality_engine.py            Reusable schema and quality-rule engine
src/run_quality.py               CLI quality gate
sql/warehouse_assertions.sql     Warehouse validation examples
tests/test_quality_engine.py      Unit tests
sample_data/transactions.csv     Synthetic dataset
```

## Run locally

```bash
python -m pip install -r requirements.txt
python -m src.run_quality sample_data/transactions.csv contracts/transactions.yml
pytest -q
```

The command exits non-zero when critical checks fail, making it usable as a CI/CD or orchestration quality gate.

## Governance model

The contract labels sensitive fields such as account identifiers and customer email as PII metadata. A production implementation should connect these classifications to a catalog such as AWS Glue/Lake Formation, Unity Catalog, Collibra or an enterprise metadata service, then enforce role-based access, masking, retention and audit requirements through the platform's policy layer.
