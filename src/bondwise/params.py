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

# Hypothetical later COI window used only by the offer-refresh demo schedule.
# Not a live obligacjeskarbowe.pl series — illustrates roll optionality.
COI_REFRESH_DEMO_NEXT = ProductParams(
    code="COI-DEMO-NEXT",
    year1_rate=0.065,
    margin=0.025,
    early_exit_fee_per_bond=2.0,
    maturity_years=4,
    fee_uncapped_after_year1=True,
)

# Cycle-indexed COI offer schedule: [initial buy, first roll, ...].
# Demo scenario (documented in tests): lump 10_000, horizon 8y, inflation 2.5%,
# Belka on — fixed COI loses to EDO; this schedule beats EDO after the year-4 roll.
COI_OFFER_REFRESH_DEMO: tuple[ProductParams, ...] = (COI, COI_REFRESH_DEMO_NEXT)
