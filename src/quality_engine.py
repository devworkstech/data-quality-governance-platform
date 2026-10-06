"""Small dataframe quality engine driven by contract rule dictionaries."""
from __future__ import annotations
import pandas as pd


def evaluate_rule(df: pd.DataFrame, rule: dict) -> dict:
    kind, column = rule["type"], rule["column"]
    if column not in df.columns:
        failures = len(df)
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
    results = [evaluate_rule(df, rule) for rule in contract.get("rules", [])]
    critical_failures = sum(1 for r in results if not r["passed"] and r["severity"] == "critical")
    passed = sum(1 for r in results if r["passed"])
    score = round(100 * passed / len(results), 2) if results else 100.0
    return {"dataset": contract["dataset"], "score": score, "critical_failures": critical_failures, "results": results}
