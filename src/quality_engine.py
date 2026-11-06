"""Contract-driven dataframe quality checks for tabular datasets."""
from __future__ import annotations

from decimal import Decimal
from numbers import Number

import pandas as pd


SUPPORTED_FIELD_TYPES = {"string", "number"}


def evaluate_field(df: pd.DataFrame, column: str, specification: dict) -> dict:
    """Validate one declared field's presence, type, and nullability."""
    expected_type = specification.get("type")
    if expected_type not in SUPPORTED_FIELD_TYPES:
        raise ValueError(
            f"unsupported or missing schema type for {column}: {expected_type!r}"
        )

    failures = 0
    details = []

    if column not in df.columns:
        failures = 1
        details.append("column missing")
    else:
        values = df[column]
        non_null_values = values[values.notna()]

        if expected_type == "string":
            invalid_types = ~non_null_values.map(lambda value: isinstance(value, str))
        else:
            invalid_types = ~non_null_values.map(
                lambda value: isinstance(value, (Number, Decimal))
                and not isinstance(value, bool)
            )

        type_failures = int(invalid_types.sum())
        if type_failures:
            failures += type_failures
            details.append(f"{type_failures} values do not match type {expected_type}")

        if specification.get("nullable", True) is False:
            null_failures = int(values.isna().sum())
            if null_failures:
                failures += null_failures
                details.append(f"{null_failures} null values in non-nullable field")

    return {
        "name": f"schema:{column}",
        "severity": "critical",
        "passed": failures == 0,
        "failures": failures,
        "detail": "; ".join(details) if details else "schema checks passed",
    }


def evaluate_rule(df: pd.DataFrame, rule: dict) -> dict:
    kind, column = rule["type"], rule["column"]
    if column not in df.columns:
        # A missing column is a structural failure even for an empty dataset.
        failures = max(len(df), 1)
        detail = "column missing"
    elif kind == "not_null":
        failures = int(df[column].isna().sum())
        detail = "null values"
    elif kind == "unique":
        failures = int(df[column].duplicated(keep=False).sum())
        detail = "rows with duplicate key"
    elif kind == "accepted_values":
        failures = int((~df[column].isin(rule["values"])).sum())
        detail = "values outside accepted set"
    elif kind == "min":
        numeric = pd.to_numeric(df[column], errors="coerce")
        failures = int((numeric < float(rule["value"])).sum() + numeric.isna().sum())
        detail = f"values below {rule['value']} or non-numeric"
    else:
        raise ValueError(f"unsupported rule type: {kind}")
    return {
        "name": rule["name"],
        "severity": rule.get("severity", "warning"),
        "passed": failures == 0,
        "failures": failures,
        "detail": detail,
    }


def evaluate_contract(df: pd.DataFrame, contract: dict) -> dict:
    schema_results = [
        evaluate_field(df, column, specification)
        for column, specification in contract.get("fields", {}).items()
    ]
    rule_results = [
        evaluate_rule(df, rule) for rule in contract.get("rules", [])
    ]
    results = schema_results + rule_results
    critical_failures = sum(
        1 for result in results
        if not result["passed"] and result["severity"] == "critical"
    )
    passed = sum(1 for result in results if result["passed"])
    score = round(100 * passed / len(results), 2) if results else 100.0
    return {
        "dataset": contract["dataset"],
        "score": score,
        "critical_failures": critical_failures,
        "results": results,
    }
