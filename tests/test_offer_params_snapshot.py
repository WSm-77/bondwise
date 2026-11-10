"""Fail when params.py drifts from the checked-in offer snapshot (#14)."""

from __future__ import annotations

import json
from pathlib import Path

from bondwise import params

FIXTURE = Path(__file__).parent / "fixtures" / "offer_params_expected.json"


def test_offer_params_match_snapshot() -> None:
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))

    assert params.FACE_VALUE == expected["face_value"]
    assert params.BELKA_RATE == expected["belka_rate"]

    for name, product in (("COI", params.COI), ("EDO", params.EDO)):
        want = expected["products"][name]
        assert product.code == want["code"]
        assert product.year1_rate == want["year1_rate"]
        assert product.margin == want["margin"]
        assert product.early_exit_fee_per_bond == want["early_exit_fee_per_bond"]
        assert product.maturity_years == want["maturity_years"]
        assert product.fee_uncapped_after_year1 == want["fee_uncapped_after_year1"]
