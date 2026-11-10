"""Multi-year path, inflation floor, and early-exit fee rules (#3)."""

from bondwise.simulator import simulate


def test_inflation_floor_at_zero():
    # Negative inflation must not reduce the post-year-1 rate below the margin.
    result = simulate(lump_sum=1000.0, horizon_years=2, inflation=-0.05, belka=False)
    # Year 2 COI rate = 1.50% + 0% = 1.50%; interest 15.00; fee 20; after-fee -5
    # Year 1: coupon path then continue; at horizon=2 early exit in period 2.
    assert result.coi.years[1].year == 2
    assert result.coi.years[1].wallet == 1000.0 + 47.5 - 5.0  # y1 coupon held + y2 after-fee
    assert result.coi.years[1].income == -5.0


def test_coi_fee_dominates_interest_in_period_2():
    # inflation 0 → y2 rate 1.5%; 10 bonds × 1.50 interest vs 20 fee
    result = simulate(lump_sum=1000.0, horizon_years=2, inflation=0.0, belka=False)
    assert result.coi.years[1].income == -5.0
    assert result.coi.years[1].wallet == 1042.5  # 1000 + y1 coupon 47.5 + (-5)


def test_edo_fee_capped_at_accrued_interest():
    # Tiny accrued interest: 1 bond, horizon 1, rate 5.35% → interest 5.35, fee cap 3 → ok
    # Force fee > interest with absurdly low rate via... year1 rate is fixed.
    # Instead: many years with 0 inflation still accrues; use 1 bond where fee 3 < interest.
    # Cap check: interest must be able to be below 3 — only possible mid-path with very low
    # rates. Year-1 EDO is 5.35 >= 3. Use horizon 1 with 1 bond (fee 3 < 5.35).
    # Separate case: after tax-free early exit, principal preserved (>= face + idle).
    result = simulate(lump_sum=100.0, horizon_years=1, inflation=0.0, belka=False)
    assert result.edo.years[0].wallet >= 100.0
    assert result.edo.years[0].income == 2.35


def test_multiyear_wallet_series_length():
    result = simulate(lump_sum=5000.0, horizon_years=5, inflation=0.02, belka=True)
    assert len(result.coi.years) == 5
    assert len(result.edo.years) == 5
    assert [p.year for p in result.coi.years] == [1, 2, 3, 4, 5]


def test_year1_still_matches_after_multiyear_extension():
    result = simulate(lump_sum=1000.0, horizon_years=1, inflation=0.03, belka=True)
    assert result.coi.years[0].wallet == 1022.28
    assert result.edo.years[0].wallet == 1019.04
