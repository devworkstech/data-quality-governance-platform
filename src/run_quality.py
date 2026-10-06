import json
import sys
import pandas as pd
import yaml
from src.quality_engine import evaluate_contract


def main(csv_path: str, contract_path: str) -> int:
    with open(contract_path, encoding="utf-8") as fh:
        contract = yaml.safe_load(fh)
    report = evaluate_contract(pd.read_csv(csv_path), contract)
    print(json.dumps(report, indent=2))
    return 1 if report["critical_failures"] else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m src.run_quality <data.csv> <contract.yml>")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
