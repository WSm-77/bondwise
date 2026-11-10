"""Centralized product parameters for COI1030 / EDO1036 (Oct 2026 offer window)."""

from dataclasses import dataclass

FACE_VALUE = 100.0
BELKA_RATE = 0.19


@dataclass(frozen=True)
class ProductParams:
    code: str
    year1_rate: float
    margin: float
    early_exit_fee_per_bond: float
    maturity_years: int
    # If True, early-exit fee is always deducted in full in periods after year 1,
    # even when that year's interest is smaller (COI periods 2–4).
    fee_uncapped_after_year1: bool


COI = ProductParams(
    code="COI1030",
    year1_rate=0.0475,
    margin=0.015,
    early_exit_fee_per_bond=2.0,
    maturity_years=4,
    fee_uncapped_after_year1=True,
)

EDO = ProductParams(
    code="EDO1036",
    year1_rate=0.0535,
    margin=0.02,
    early_exit_fee_per_bond=3.0,
    maturity_years=10,
    fee_uncapped_after_year1=False,
)
