import pandas as pd
from src.quality_engine import evaluate_contract

CONTRACT = {
    "dataset": "transactions",
    "rules": [
        {"name":"id_unique","type":"unique","column":"transaction_id","severity":"critical"},
        {"name":"amount_positive","type":"min","column":"amount","value":0.01,"severity":"critical"},
        {"name":"currency_valid","type":"accepted_values","column":"currency","values":["USD","CAD"],"severity":"warning"},
    ],
}


def test_clean_dataset_scores_100():
    df = pd.DataFrame({"transaction_id":["t1","t2"],"amount":[1.0,2.0],"currency":["USD","CAD"]})
    report = evaluate_contract(df, CONTRACT)
    assert report["score"] == 100.0
    assert report["critical_failures"] == 0


def test_duplicate_and_negative_amount_fail_critical_rules():
    df = pd.DataFrame({"transaction_id":["t1","t1"],"amount":[1.0,-2.0],"currency":["USD","USD"]})
    report = evaluate_contract(df, CONTRACT)
    assert report["critical_failures"] == 2
    assert report["score"] < 100
