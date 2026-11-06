from decimal import Decimal

import pandas as pd

from src.quality_engine import evaluate_contract


CONTRACT = {
    "dataset": "transactions",
    "rules": [
        {"name": "id_unique", "type": "unique", "column": "transaction_id", "severity": "critical"},
        {"name": "amount_positive", "type": "min", "column": "amount", "value": 0.01, "severity": "critical"},
        {"name": "currency_valid", "type": "accepted_values", "column": "currency", "values": ["USD", "CAD"], "severity": "warning"},
    ],
}

SCHEMA_CONTRACT = {
    "dataset": "transactions",
    "fields": {
        "transaction_id": {"type": "string", "nullable": False},
        "amount": {"type": "number", "nullable": False},
        "customer_email": {"type": "string", "nullable": True},
    },
    "rules": [],
}


def test_clean_dataset_scores_100():
    df = pd.DataFrame({"transaction_id": ["t1", "t2"], "amount": [1.0, 2.0], "currency": ["USD", "CAD"]})
    report = evaluate_contract(df, CONTRACT)
    assert report["score"] == 100.0
    assert report["critical_failures"] == 0


def test_duplicate_and_negative_amount_fail_critical_rules():
    df = pd.DataFrame({"transaction_id": ["t1", "t1"], "amount": [1.0, -2.0], "currency": ["USD", "USD"]})
    report = evaluate_contract(df, CONTRACT)
    assert report["critical_failures"] == 2
    assert report["score"] < 100


def test_schema_contract_accepts_valid_types_and_nullable_fields():
    df = pd.DataFrame({
        "transaction_id": ["t1"],
        "amount": [Decimal("12.50")],
        "customer_email": [None],
    })
    report = evaluate_contract(df, SCHEMA_CONTRACT)
    assert report["score"] == 100.0
    assert report["critical_failures"] == 0
    assert all(result["passed"] for result in report["results"])


def test_missing_declared_column_is_a_critical_failure_on_empty_data():
    df = pd.DataFrame(columns=["transaction_id", "amount"])
    report = evaluate_contract(df, SCHEMA_CONTRACT)
    results = {result["name"]: result for result in report["results"]}
    assert results["schema:customer_email"]["passed"] is False
    assert results["schema:customer_email"]["failures"] == 1
    assert report["critical_failures"] == 1


def test_type_and_non_nullable_violations_are_reported():
    df = pd.DataFrame({
        "transaction_id": ["t1", None],
        "amount": ["12.50", "not-a-number"],
        "customer_email": [None, None],
    })
    report = evaluate_contract(df, SCHEMA_CONTRACT)
    results = {result["name"]: result for result in report["results"]}
    assert results["schema:transaction_id"]["failures"] == 1
    assert results["schema:amount"]["failures"] == 2
    assert results["schema:customer_email"]["passed"] is True
    assert report["critical_failures"] == 2


def test_missing_rule_column_fails_even_when_dataset_is_empty():
    contract = {
        "dataset": "transactions",
        "rules": [{"name": "required_id", "type": "not_null", "column": "id", "severity": "critical"}],
    }
    report = evaluate_contract(pd.DataFrame(), contract)
    assert report["results"][0]["passed"] is False
    assert report["critical_failures"] == 1
